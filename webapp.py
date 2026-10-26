from __future__ import annotations

import html
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

from config import SUPPORTED_CATEGORIES
from ticket_service import (
    administration_summary,
    begin_request,
    demo_accounts,
    get_visible_ticket,
    initialize,
    list_visible_tickets,
    manager_assign,
    manager_pending,
    resident_confirm_resolution,
    resident_reopen,
    submit_maintenance_request,
    support_health,
    technician_complete,
    technician_progress,
    technician_return,
)

initialize()

CSS = """
body{font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:#f5f7fb;color:#162033}
header{background:#14213d;color:white;padding:18px 28px;display:flex;align-items:center;justify-content:space-between}
main{max-width:1100px;margin:24px auto;padding:0 20px}.card{background:white;border:1px solid #e1e6ef;border-radius:14px;padding:18px;margin:14px 0;box-shadow:0 2px 7px rgba(0,0,0,.04)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.pill{display:inline-block;background:#eef3ff;border-radius:999px;padding:5px 10px;margin-right:6px}.warn{background:#fff4df;border-left:5px solid #e5a100;padding:12px}.bad{background:#ffe9e9;border-left:5px solid #d33;padding:12px}.ok{background:#e9f8ef;border-left:5px solid #2c8c55;padding:12px}
label{display:block;font-weight:600;margin-top:10px}input,textarea,select{width:100%;box-sizing:border-box;padding:9px;margin-top:4px;border:1px solid #cdd4df;border-radius:8px}button{background:#2457d6;color:white;border:0;border-radius:8px;padding:9px 13px;margin-top:12px;cursor:pointer}.muted{color:#667085;font-size:.92rem}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:8px;border-bottom:1px solid #eee}a{color:#2457d6;text-decoration:none}
"""


def esc(v): return html.escape(str(v if v is not None else ""))

def actor_options(current):
    out=[]
    for a in demo_accounts():
        if not a['active']: continue
        label=f"{a['display_name']} · {a['role']}"
        sel=" selected" if a['account_id']==current else ""
        out.append(f"<option value='{esc(a['account_id'])}'{sel}>{esc(label)}</option>")
    return ''.join(out)

def layout(actor, body, message=""):
    acct=next((a for a in demo_accounts() if a['account_id']==actor), None)
    role=acct['role'] if acct else 'Unknown'
    msg=f"<div class='ok'>{esc(message)}</div>" if message else ""
    return f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>DormFix</title><style>{CSS}</style></head>
<body><header><div><strong>🛠️ DormFix</strong><div style='font-size:.8rem;opacity:.8'>SYSEN 5151 / 5930 demonstration prototype</div></div><form method='get'><select name='actor' onchange='this.form.submit()'>{actor_options(actor)}</select></form></header>
<main><div class='warn'><strong>Routine non-emergency maintenance only.</strong> This prototype does not dispatch emergency response, purchase parts, bill residents, or integrate with rent systems.</div>{msg}<p class='muted'>Demo identity: {esc(actor)} · {esc(role)}. Identity selection is a classroom demo mechanism, not production authentication.</p>{body}</main></body></html>"""

def hidden_actor(actor): return f"<input type='hidden' name='actor' value='{esc(actor)}'>"

def ticket_view(t):
    history=''.join(f"<tr><td>{esc(e['ts'])}</td><td>{esc(e['event_type'])}</td><td>{esc(e['actor_id'])}</td><td>{esc(e.get('notes') or '')}</td></tr>" for e in t.get('history',[]))
    return f"<div class='card'><h3>{esc(t['ticket_id'])}</h3><span class='pill'>{esc(t['status'])}</span><span class='pill'>{esc(t.get('category'))}</span><p>{esc(t['description'])}</p><p><strong>Location:</strong> {esc(t['building'])} / {esc(t['room'])}<br><strong>Access:</strong> {esc(t['availability'])}<br><strong>Assigned:</strong> {esc(t.get('assigned_technician') or 'Unassigned')}</p><p><strong>Next step:</strong> {esc(t.get('next_step',''))}</p><details><summary>Audit history</summary><table><tr><th>Time</th><th>Event</th><th>Actor</th><th>Note</th></tr>{history}</table></details></div>"

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, content):
        data=content.encode('utf-8'); self.send_response(code); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def _redirect(self, actor, msg=""):
        q={'actor':actor};
        if msg:q['msg']=msg
        self.send_response(303); self.send_header('Location','/?'+urlencode(q)); self.end_headers()
    def log_message(self, fmt, *args): pass
    def do_GET(self):
        q=parse_qs(urlparse(self.path).query); actor=q.get('actor',['resident.alex'])[0]; msg=q.get('msg',[''])[0]
        acct=next((a for a in demo_accounts() if a['account_id']==actor and a['active']),None)
        if not acct: actor='resident.alex'; acct=next(a for a in demo_accounts() if a['account_id']==actor)
        role=acct['role']; body=''
        try:
            if role=='Resident': body=self.resident(actor)
            elif role=='Manager': body=self.manager(actor)
            elif role=='Technician': body=self.technician(actor)
            elif role=='Administration': body=self.admin(actor)
            else: body=self.it(actor)
        except Exception as exc:
            body=f"<div class='bad'>{esc(type(exc).__name__+': '+str(exc))}</div>"
        self._send(200,layout(actor,body,msg))
    def _form(self):
        n=int(self.headers.get('Content-Length','0')); return {k:v[0] for k,v in parse_qs(self.rfile.read(n).decode()).items()}
    def do_POST(self):
        f=self._form(); actor=f.get('actor','resident.alex'); action=f.get('action','')
        try:
            if action=='create':
                result=begin_request(f.get('description',''),{k:f.get(k,'') for k in ('building','room','category','availability','resident_contact')},use_ai=False)
                if result['emergency_warning']: raise ValueError('Possible emergency keyword detected; use the appropriate emergency/housing emergency channel, not DormFix.')
                if result['missing_fields']: raise ValueError('Missing: '+', '.join(result['missing_fields']))
                t=submit_maintenance_request(actor,result['draft'],str(uuid.uuid4()),result['suggestions']); self._redirect(actor,'Committed '+t['ticket_id']); return
            tid=f.get('ticket_id','')
            if action=='assign': manager_assign(actor,tid,f['technician_id'],f['priority'])
            elif action=='progress': technician_progress(actor,tid,f.get('note',''))
            elif action=='complete': technician_complete(actor,tid,f.get('note',''))
            elif action=='return': technician_return(actor,tid,f.get('reason',''))
            elif action=='resolve': resident_confirm_resolution(actor,tid,True,f.get('reason',''))
            elif action=='unresolved': resident_confirm_resolution(actor,tid,False,f.get('reason',''))
            elif action=='reopen': resident_reopen(actor,tid,f.get('reason',''))
            else: raise ValueError('Unknown action')
            self._redirect(actor,'Action completed'); return
        except Exception as exc:
            self._redirect(actor,f"{type(exc).__name__}: {exc}")
    def resident(self,actor):
        form=f"""<div class='card'><h2>Report maintenance</h2><form method='post'>{hidden_actor(actor)}<input type='hidden' name='action' value='create'><label>Description<textarea name='description' required></textarea></label><div class='grid'><label>Building<input name='building' required></label><label>Room<input name='room' required></label><label>Category<select name='category'>{''.join(f'<option>{c}</option>' for c in SUPPORTED_CATEGORIES)}</select></label><label>Access availability<input name='availability' required></label></div><label>Resident contact (manager-only, optional)<input name='resident_contact'></label><button>Create confirmed demo ticket</button></form><p class='muted'>The Streamlit UI provides the full two-step editable draft/explicit-confirmation interaction. This zero-dependency fallback uses this submitted form as the confirmation step.</p></div>"""
        parts=[form]
        for t in list_visible_tickets(actor):
            parts.append(ticket_view(t))
            if t['status']=='Awaiting resident confirmation':
                parts.append(f"<div class='card'><form method='post'>{hidden_actor(actor)}<input type='hidden' name='ticket_id' value='{esc(t['ticket_id'])}'><label>Resolution note<input name='reason'></label><button name='action' value='resolve'>Confirm resolved</button> <button name='action' value='unresolved'>Not resolved / reopen</button></form></div>")
            if t['status']=='Closed':
                parts.append(f"<div class='card'><form method='post'>{hidden_actor(actor)}<input type='hidden' name='ticket_id' value='{esc(t['ticket_id'])}'><label>Reason to reopen<input name='reason' required></label><button name='action' value='reopen'>Reopen</button></form></div>")
        return ''.join(parts)
    def manager(self,actor):
        pending=manager_pending(actor); parts=[f"<div class='card'><h2>Manager dashboard</h2><p>Pending decisions: <strong>{len(pending)}</strong></p></div>"]
        techs=[a for a in demo_accounts() if a['role']=='Technician' and a['active']]
        for t in list_visible_tickets(actor):
            parts.append(ticket_view(t))
            if t['status'] in ('Submitted','Reopened'):
                opts=''.join(f"<option value='{esc(a['account_id'])}'>{esc(a['display_name'])}</option>" for a in techs)
                parts.append(f"<div class='card'><form method='post'>{hidden_actor(actor)}<input type='hidden' name='action' value='assign'><input type='hidden' name='ticket_id' value='{esc(t['ticket_id'])}'><label>Priority<select name='priority'><option>Routine</option><option>Normal</option><option>High</option></select></label><label>Technician<select name='technician_id'>{opts}</select></label><button>Assign</button></form></div>")
        return ''.join(parts)
    def technician(self,actor):
        parts=["<div class='card'><h2>Assigned work</h2></div>"]
        for t in list_visible_tickets(actor):
            parts.append(ticket_view(t)); parts.append(f"<div class='card'><form method='post'>{hidden_actor(actor)}<input type='hidden' name='ticket_id' value='{esc(t['ticket_id'])}'><label>Progress/completion note<input name='note'></label><button name='action' value='progress'>Update progress</button> <button name='action' value='complete'>Mark complete</button><label>Blocked-work return reason<input name='reason'></label><button name='action' value='return'>Return to manager</button></form></div>")
        return ''.join(parts)
    def admin(self,actor):
        s=administration_summary(actor); rows=''.join(f"<tr><td>{esc(k)}</td><td>{v}</td></tr>" for k,v in s['by_status'].items())
        return f"<div class='card'><h2>Housing Administration summary</h2><p>Total: <strong>{s['total']}</strong> · Unfinished: <strong>{s['unfinished']}</strong></p><table><tr><th>Status</th><th>Count</th></tr>{rows}</table><p class='muted'>Aggregate-only view: no room, access, contact, or ticket history.</p></div>"
    def it(self,actor):
        h=support_health(actor); rows=''.join(f"<tr><td>{esc(d['ts'])}</td><td>{esc(d['kind'])}</td><td>{esc(d['state'])}</td><td>{esc(d['detail'])}</td></tr>" for d in h['recent_diagnostics'])
        return f"<div class='card'><h2>IT Support</h2><p>Service: {esc(h['service'])} · Database: {esc(h['database'])}</p><table><tr><th>Time</th><th>Kind</th><th>State</th><th>Detail</th></tr>{rows}</table><p class='muted'>Ordinary IT support has diagnostics, not ticket-detail access.</p></div>"

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--host',default='127.0.0.1'); p.add_argument('--port',type=int,default=8502); a=p.parse_args()
    print(f"DormFix zero-dependency web demo: http://{a.host}:{a.port}")
    ThreadingHTTPServer((a.host,a.port),Handler).serve_forever()
