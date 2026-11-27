"""Run repeatable Chapter 13 checks against a new database. No operational records are used."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import socket
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import build_opener, ProxyHandler, Request
import uuid

ROOT = Path(__file__).resolve().parent
CLIENT = build_opener(ProxyHandler({}))
RES = "resident.alex"
FIXTURE = {"description":"The kitchen sink drips.", "building":"Test Hall","room":"101",
           "availability":"","resident_contact":"synthetic@example.invalid"}


class ModelFixture(BaseHTTPRequestHandler):
    calls = []
    replies = []

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        prompt = json.loads(body["messages"][1]["content"])
        self.calls.append(prompt)
        payload = {"category":"electrical","summary":"Electrical repair"}
        if "extra-fields" in prompt["description"]:
            payload.update(availability="2 AM", location="Invented room", missing_fields=[],
                           priority="High", assignee="tech.jordan")
        if "wrong-type" in prompt["description"]:
            payload["availability"] = ["tomorrow"]
        if "unavailable" in prompt["description"]:
            self.send_error(503)
            return
        self.replies.append((body["response_format"]["json_schema"]["schema"], payload))
        reply = {"choices":[{"message":{"content":json.dumps(payload)}}]}
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(reply).encode())

    def log_message(self, *args):
        pass


def request(url, body=None, actor=RES, form=False):
    headers = {"X-DormFix-Actor":actor} if actor else {}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
        data = urlencode(body).encode() if form else json.dumps(body).encode()
    try:
        res = CLIENT.open(Request(url, data=data, headers=headers), timeout=50)
    except HTTPError as err:
        res = err
    with res:
        content = res.read().decode()
        return res.status, json.loads(content) if res.headers.get_content_type()=="application/json" else content


@contextmanager
def app(db, endpoint):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1",0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen([sys.executable, str(ROOT/"chapter13.py"),"--port",str(port),"--db",str(db),
                             "--model-url",endpoint], cwd=ROOT, stdout=subprocess.DEVNULL)
    try:
        for _ in range(130):
            if proc.poll() is not None:
                raise RuntimeError("Application stopped during startup")
            try:
                if request(url)[0]==200: break
            except (URLError, OSError): pass
            time.sleep(.1)
        else: raise RuntimeError("Application startup timed out")
        yield url
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def check(condition, name):
    if not condition: raise AssertionError(name)


def run(url, db, live):
    timings = {k:[] for k in ["draft","confirm","read"]}
    def call(label, path, body=None, actor=RES):
        tick = time.perf_counter()
        status, result = request(url+path,body,actor)
        timings[label].append((time.perf_counter()-tick)*1000)
        check(status==200,(path,status,result))
        return result
    page=request(url)[1]
    check('id=\'intake\'' in page and 'resident_intake.js' in page and 'Confirm and submit' in page, "front end")
    check('/api/drafts' in request(url+'/resident_intake.js')[1], "browser calls REST")
    sample=call("draft","/api/drafts",FIXTURE)
    check(sample["suggestions"]["source"]=="configured-llm" and not sample["manual_fallback"],"real adapter response")
    if not live:
        schema, raw = ModelFixture.replies[-1]
        check(set(raw) == set(schema["required"]) == {"category", "summary"}, "exact required fields")
        check(all(isinstance(value, str) for value in raw.values()), "both fields are strings")
        check(raw["category"] in schema["properties"]["category"]["enum"], "category is permitted")
        check(sample["draft"]["category"] == "electrical" and not sample["manual_fallback"], "schema-valid incorrect meaning")
        check("resident_contact" not in ModelFixture.calls[-1]["provided"],"private fields")
        extra = request(url+"/api/drafts", dict(FIXTURE, description="The sink drips. extra-fields"))[1]
        check(extra["suggestions"]["availability"] == "2 AM", "exercised spurious access")
        check(extra["draft"]["availability"] == "" and extra["draft"]["room"] == "101", "resident authority")
        check("priority" not in extra["suggestions"] and "assignee" not in extra["suggestions"], "manager authority")
    check(sample["draft"]["availability"]=="" and "availability" in sample["missing_fields"],"invented access excluded")
    check(sample["draft"]["room"]=="101","preserve original location")
    with closing(sqlite3.connect(db)) as conn:
        check(conn.execute("select count(*) from tickets").fetchone()==(0,), "no premature ticket")
    key=str(uuid.uuid4())
    submit={"draft":dict(sample["draft"],category="plumbing",availability="After 4 PM"),"confirmed":True,
            "submission_key":key,"suggestions":sample["suggestions"]}
    check(request(url+"/api/tickets",dict(submit,confirmed=False))[0]==400,"confirmation required")
    receipt=call("confirm","/api/tickets",submit)
    tid=receipt["ticket_id"]
    record=call("read","/api/tickets/"+tid)
    check(record["category"]=="plumbing" and record["availability"]=="After 4 PM" and not record["priority"] and not record["assigned_technician"],"confirmed meaning")
    check(tid in request(url)[1],"acknowledged ticket renders in resident page")
    check(request(url+"/api/tickets/"+tid,actor="resident.sam")[0]==403,"scoped read")
    check(request(url+"/api/drafts",FIXTURE,actor="")[0]==401,"missing actor")
    check(request(url+"/api/tickets",submit,actor="resident.sam")[0]==403,"scoped submission key")
    check(request(url+"/api/tickets",dict(submit,draft=dict(submit["draft"],building="")))[0]==400,"incomplete draft")
    if not live:
        for condition in ["wrong-type","unavailable"]:
            result=request(url+"/api/drafts",dict(FIXTURE,description=condition))[1]
            check(result["manual_fallback"] and result["suggestions"]["source"]=="local-heuristic",condition)
        with ThreadPoolExecutor(4) as pool:
            ids=list(pool.map(lambda _: request(url+"/api/tickets",submit)[1]["ticket_id"],range(8)))
        check(ids==[tid]*8,"concurrent retries")
    # Real role pages perform the handoffs, including the owner-confirmed closure.
    for actor,action,extras in [("manager.morgan","assign",{"technician_id":"tech.taylor","priority":"Normal"}),
             ("tech.taylor","progress",{"note":"Diagnosed leak"}),("tech.taylor","complete",{"note":"Washer replaced"}),
             (RES,"resolve",{"reason":"No further drip"})]:
        status,html=request(url+"/",dict(actor=actor,action=action,ticket_id=tid,**extras),form=True)
        check(status==200 and "Action completed" in html, action)
    record=call("read","/api/tickets/"+tid)
    check(record["status"]=="Closed" and len(record["history"])>=5,"closed history")
    # 35 opportunities cover repeated processing. Four clients submit in each batch,
    # using distinct keys for new requests. These are engineering scenarios.
    count=3 if live else 35
    def trial(i):
        res=call("draft","/api/drafts",dict(FIXTURE,description=f"The sink drips in test {i}."))
        check(res["suggestions"]["source"]=="configured-llm","model active in volume run")
        body=dict(submit,submission_key=str(uuid.uuid4()),draft=dict(submit["draft"],room=str(200+i)))
        saved=call("confirm","/api/tickets",body)
        got=call("read","/api/tickets/"+saved["ticket_id"])
        check(got["room"]==str(200+i) and len(got["history"])==1,"concurrent row correspondence")
    with ThreadPoolExecutor(1 if live else 4) as pool: list(pool.map(trial,range(count)))
    def stats(samples):
        s=sorted(samples)
        return {"n":len(s),"median_ms":round(statistics.median(s),2),"p95_ms":round(s[math.ceil(.95*len(s))-1],2),"max_ms":round(s[-1],2)}
    print(json.dumps({"mode":"weights" if live else "injected HTTP model","volume":count,
                      "schema_valid_wrong_category_contained":None if live else True,
                      "additional_access_and_authority_fields_contained":None if live else True,
                      "example_suggestion":sample["suggestions"].get("category"),"committed":"plumbing",
                      "lifecycle":record["status"],"timings":{k:stats(v) for k,v in timings.items()}},indent=2),flush=True)
    return tid


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--live",action="store_true",help="require the real local weights, never a fallback")
    args=parser.parse_args()
    fixture=ThreadingHTTPServer(("127.0.0.1",0),ModelFixture) if not args.live else None
    if fixture: threading.Thread(target=fixture.serve_forever,daemon=True).start()
    port=fixture.server_port if fixture else 8081
    try:
        with tempfile.TemporaryDirectory() as temp:
            db=Path(temp)/"fresh.sqlite"
            with app(db,f"http://127.0.0.1:{port}/v1/chat/completions") as url: tid=run(url,db,args.live)
            with app(db,"") as url:
                check(request(url+"/api/tickets/"+tid)[1]["status"]=="Closed","restart durability")
                check(request(url+"/api/drafts",FIXTURE)[1]["manual_fallback"],"manual-only launch")
            print("Restart and unavailable-model checks passed.",flush=True)
    finally:
        if fixture:
            fixture.shutdown()
            fixture.server_close()


if __name__=="__main__": main()
