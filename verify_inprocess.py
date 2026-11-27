"""Run the same fault campaign with in-memory HTTP transports where sockets are unavailable."""
from email.message import Message
from io import BytesIO
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlsplit

import verify_ch13 as suite


def exchange(handler_type, method, path, data, headers):
    handler=handler_type.__new__(handler_type)
    handler.path=path
    handler.command=method
    handler.rfile=BytesIO(data)
    handler.wfile=BytesIO()
    handler.headers=Message()
    for k,v in headers.items(): handler.headers[k]=v
    handler.headers["Content-Length"]=str(len(data))
    response_headers={}
    status=[]
    handler.send_response=lambda code,*args: status.append(int(code))
    handler.send_header=lambda key,value:response_headers.update({key:value})
    handler.end_headers=lambda:None
    handler.send_error=lambda code,*args:status.append(code)
    getattr(handler,"do_"+method)()
    return status[0], response_headers, handler.wfile.getvalue()


class ModelTransport:
    def open(self, req, timeout):
        code, _, data=exchange(suite.ModelFixture,"POST",urlsplit(req.full_url).path,req.data,dict(req.headers))
        if code>=400: raise HTTPError(req.full_url,code,"fixture unavailable",{},None)
        return BytesIO(data)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"fresh.db"
        os.environ["DORMFIX_DB_PATH"]=str(path)
        os.environ["DORMFIX_LLM_URL"]="http://fixture.local/v1/chat/completions"
        from webapp import Handler
        def request(url,body=None,actor=suite.RES,form=False):
            headers={"X-DormFix-Actor":actor} if actor else {}
            payload=b""
            if body is not None:
                headers["Content-Type"]="application/x-www-form-urlencoded" if form else "application/json"
                payload=suite.urlencode(body).encode() if form else json.dumps(body).encode()
            code,resp,data=exchange(Handler,"GET" if body is None else "POST",url.split("app.local")[-1] or "/",payload,headers)
            if code==303: return request("http://app.local"+resp["Location"],actor=actor)
            content=data.decode()
            return code,json.loads(content) if "application/json" in resp.get("Content-Type","") else content
        with patch.object(suite,"request",request), patch("intake_model.urllib.request.build_opener",return_value=ModelTransport()):
            suite.run("http://app.local",path,False)
        print("Transport: in-process application and model HTTP handlers. No network or real weights in this check.")


if __name__=="__main__":main()
