(() => {
  const form = document.getElementById('intake');
  if (!form) return;
  const confirm = document.getElementById('confirm-draft');
  const message = document.getElementById('intake-result');
  const prepare = document.getElementById('prepare-draft');
  const actor = form.elements.actor.value;
  let suggestions = null;
  let key = null;
  function fields() {
    const values = Object.fromEntries(new FormData(form));
    delete values.actor;
    delete values.use_ai;
    return values;
  }
  async function request(url, body) {
    const response = await fetch(url, {method: body ? 'POST' : 'GET',
      headers: {'Content-Type':'application/json', 'X-DormFix-Actor':actor},
      body: body ? JSON.stringify(body) : undefined});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error);
    return result;
  }
  form.addEventListener('submit', async event => {
    event.preventDefault();
    prepare.disabled = true;
    confirm.hidden = true;
    message.textContent = 'Preparing your draft…';
    try {
      const result = await request('/api/drafts', {...fields(), use_ai:form.elements.use_ai.checked});
      suggestions = result.suggestions;
      for (const [name,value] of Object.entries(result.draft)) form.elements[name].value = value;
      if (!key) key = crypto.randomUUID();
      if (result.emergency_warning) throw new Error('Possible emergency. Use the appropriate emergency channel.');
      const source = !form.elements.use_ai.checked ? 'Manual entry' : result.manual_fallback ? 'Manual fallback' : 'Language model';
      message.textContent = source + '. Review the category and enter your own access time. ' +
        (result.missing_fields.length ? 'Missing: ' + result.missing_fields.join(', ') + '. ' : '') +
        'No ticket has been created.';
      confirm.hidden = false;
    } catch(error) { message.textContent = error.message; }
    finally { prepare.disabled = false; }
  });
  confirm.addEventListener('click', async () => {
    confirm.disabled = true;
    prepare.disabled = true;
    try {
      const receipt = await request('/api/tickets', {draft:fields(), suggestions, confirmed:true, submission_key:key});
      const record = await request('/api/tickets/' + encodeURIComponent(receipt.ticket_id));
      location.assign('/?' + new URLSearchParams({actor, msg:'Committed ' + record.ticket_id + ' · ' + record.status}));
    } catch(error) { message.textContent = error.message; }
    finally { confirm.disabled = false; prepare.disabled = false; }
  });
})();
