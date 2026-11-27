// Exercise the shipped browser script with isolated DOM and transport controls.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function control(value = '') {
  return {value, hidden:false, disabled:false, handlers:{},
    addEventListener(name, fn) { this.handlers[name] = fn; }};
}
test('resident corrects the draft and retries a lost receipt with the same key', async () => {
  const form=control();
  const values={actor:'resident.alex',description:'Sink drips',building:'Hall',room:'10',
    availability:'',category:'',resident_contact:''};
  form.elements=Object.fromEntries(Object.entries(values).map(([k,v])=>[k,control(v)]));
  form.elements.use_ai={checked:true};
  const confirm=control(), message=control(), prepare=control();
  const ids={intake:form,'confirm-draft':confirm,'intake-result':message,'prepare-draft':prepare};
  const requests=[];
  let destination='';
  let loseFirst=true;
  const context={document:{getElementById:k=>ids[k]},URLSearchParams,
    FormData:class { *[Symbol.iterator]() {for(const k of Object.keys(values)) yield [k,form.elements[k].value];} },
    crypto:{randomUUID:()=> '4557097f-782b-40e8-85ef-f45c2e509759'},
    location:{assign:s=>{destination=s;}},
    fetch:async(url, options)=>{
      const body=options.body && JSON.parse(options.body);
      requests.push({url, body, actor:options.headers['X-DormFix-Actor']});
      if(url==='/api/tickets' && loseFirst) { loseFirst=false; throw Error('Lost reply'); }
      let result = {ticket_id:'DORMFIX-0001',status:'Submitted'};
      if(url==='/api/drafts') result={draft:{...values,category:'electrical'},suggestions:{category:'electrical'},
        missing_fields:['availability'],manual_fallback:false};
      return {ok:true,json:async()=>result};
    }};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'..','resident_intake.js'),'utf8'),context);
  await form.handlers.submit({preventDefault(){}});
  assert.deepEqual(requests.map(r=>r.url),['/api/drafts']);
  assert.match(message.textContent,/Language model/);
  assert.equal(confirm.hidden,false);
  form.elements.category.value='plumbing';
  form.elements.availability.value='After 4 PM';
  await confirm.handlers.click();
  assert.equal(message.textContent,'Lost reply');
  assert.equal(form.elements.availability.value,'After 4 PM');
  await confirm.handlers.click();
  assert.deepEqual(requests.map(r=>r.url),['/api/drafts','/api/tickets','/api/tickets','/api/tickets/DORMFIX-0001']);
  assert.equal(requests[1].body.submission_key,requests[2].body.submission_key);
  assert.equal(requests[2].body.confirmed,true);
  assert.equal(requests[2].body.draft.category,'plumbing');
  assert.ok(requests.every(r=>r.actor==='resident.alex'));
  assert.match(destination,/DORMFIX-0001/);
});
