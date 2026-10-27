/* Shared quotation downloads and billing draft. No personal details enter URLs or localStorage. */
(function () {
  'use strict';
  const draftKey = 'TE-training-customer-v1';
  const fields = ['companyName','registrationId','vatId','contactName','email','address','city','postalCode','country','phone','poReference'];
  function customerOnly(values) {
    return Object.fromEntries(fields.map(name => [name, typeof values?.[name] === 'string' ? values[name] : '']));
  }
  function readCustomer() {
    try { return customerOnly(JSON.parse(sessionStorage.getItem(draftKey))); }
    catch { return customerOnly({}); }
  }
  function saveCustomer(values) {
    try { sessionStorage.setItem(draftKey,JSON.stringify(customerOnly(values))); return true; }
    catch { return false; }
  }
  function saveBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url; link.download = filename; link.hidden = true;
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url),60000);
  }
  async function downloadProposal(apiUrl, courses, customer, button, status) {
    const original = button.textContent;
    button.disabled = true; button.dataset.busy = 'true';
    button.textContent = 'Preparing PDF…';
    status.hidden = false; status.textContent = 'Preparing your one-page proposal…';
    try {
      const configResponse = await fetch(apiUrl+'?action=config',{credentials:'same-origin',signal:AbortSignal.timeout(15000)});
      const config = await configResponse.json();
      if (!configResponse.ok || !config.csrf) throw new Error('Document downloads are temporarily unavailable. Please try again.');
      const response = await fetch(apiUrl+'?action=proposal',{
        method:'POST',credentials:'same-origin',
        headers:{'Content-Type':'application/json','X-CSRF-Token':config.csrf},
        body:JSON.stringify({courses,customer:customerOnly(customer)}),signal:AbortSignal.timeout(90000)
      });
      if (!response.ok || !(response.headers.get('Content-Type')||'').includes('application/pdf')) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || 'The proposal could not be downloaded. Please try again.');
      }
      const filename = response.headers.get('Content-Disposition')?.match(/filename="([A-Za-z0-9_.-]+)"/)?.[1] || 'TopEngineer-training-proposal.pdf';
      saveBlob(await response.blob(),filename);
      status.textContent = 'Proposal downloaded. You can prepare an invoice using the same courses and company details.';
    } catch (failure) { status.textContent = ''; throw failure; }
    finally { button.disabled = false; button.dataset.busy = 'false'; button.textContent = original; }
  }
  window.TrainingDocuments = {readCustomer,saveCustomer,downloadProposal,saveBlob};
})();
