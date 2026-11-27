"""Measure role handoffs, summaries and two-copy recovery on 35 synthetic tickets."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json, math, os, statistics, time


def main():
    with TemporaryDirectory() as tmp:
        os.environ["DORMFIX_DB_PATH"]=str(Path(tmp)/"bench.sqlite")
        import ticket_service as svc
        import ticket_store as store
        result={}
        def measure(label,fn,*args,**kwargs):
            t=time.perf_counter()
            value=fn(*args,**kwargs)
            result.setdefault(label,[]).append((time.perf_counter()-t)*1000)
            return value
        svc.initialize()
        for i in range(35):
            draft=dict(description="Sink drips",category="plumbing",building="Hall",room=str(i),availability="After 4")
            tid=svc.submit_maintenance_request("resident.alex",draft,str(i))["ticket_id"]
            measure("assign",svc.manager_assign,"manager.morgan",tid,"tech.taylor","Normal")
            measure("progress",svc.technician_progress,"tech.taylor",tid,"Inspected")
            measure("complete",svc.technician_complete,"tech.taylor",tid,"Repaired")
            measure("resolve",svc.resident_confirm_resolution,"resident.alex",tid,True)
            assert measure("summary",svc.administration_summary,"admin.housing")["total"]==i+1
        record=store.events(tid)
        for i in range(10):
            measure("checkpoint",svc.support_create_checkpoint,"it.support")
            measure("restore",svc.support_restore_checkpoint,"it.support",confirmed=True)
            assert store.events(tid)==record and len(store.list_tickets())==35
        stats={k:{"n":len(v),"median_ms":round(statistics.median(v),2),
              "p95_ms":round(sorted(v)[math.ceil(.95*len(v))-1],2)} for k,v in result.items()}
        print(json.dumps(stats,indent=2))


if __name__=='__main__':main()
