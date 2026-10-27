(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const apiUrl = 'api.php';
  const cartKey = 'TE-training-cart-v1';
  const currency = value => new Intl.NumberFormat('en-IE', {style:'currency',currency:'EUR'}).format(value / 100);
  const dateLabel = value => new Intl.DateTimeFormat('en-GB',{day:'numeric',month:'short',year:'numeric'}).format(new Date(value+'T12:00:00'));
  const key = () => crypto.randomUUID ? crypto.randomUUID() : Array.from(crypto.getRandomValues(new Uint8Array(20)), n => n.toString(16).padStart(2,'0')).join('');
  let config, cart, quote, order, requestKey = key(), quoteRequest = 0, busy = false;

  function element(tag, text, classes) {
    const item = document.createElement(tag);
    if (text !== undefined) item.textContent = text;
    if (classes) item.className = classes;
    return item;
  }
  function error(message) {
    $('order-error').textContent = message;
    $('order-error').hidden = false;
    $('order-error').focus();
  }
  function clearError() { $('order-error').hidden = true; }
  function saveBillingDraft() {
    const customer = Object.fromEntries(new FormData($('billing-form')));
    TrainingDocuments.saveCustomer(customer);
    return customer;
  }
  function renderTerms(terms, target) {
    const list = $(target);
    list.replaceChildren();
    if (!terms) { list.parentElement.hidden = true; return; }
    list.parentElement.hidden = false;
    ['Invoices are valid for '+terms.validity_months+' calendar months from issue.',terms.rescheduling,terms.refunds].forEach(text => list.append(element('li',text,'mb-1')));
  }
  async function api(action, body) {
    const response = await fetch(apiUrl + '?action=' + action, {
      method:body ? 'POST' : 'GET', credentials:'same-origin',
      headers:body ? {'Content-Type':'application/json','X-CSRF-Token':config.csrf,'Idempotency-Key':requestKey} : {},
      body:body ? JSON.stringify(body) : undefined,
      signal:AbortSignal.timeout(45000)
    });
    const type = response.headers.get('content-type') || '';
    if (!type.includes('application/json')) throw new Error('Online ordering is temporarily unavailable. Please reload the page or return to the calculator.');
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The order could not be prepared. Please try again.');
    return data;
  }
  function renderQuote(data) {
    const lines = $('quote-lines');
    lines.replaceChildren();
    data.courses.forEach(course => {
      const item = element('div', undefined, 'order-line');
      item.append(element('p', 'Level ' + course.id + ' · ' + course.name, 'fw-bold mb-1'));
      item.append(element('p', course.days + ' days · ' + course.hours + ' hours · ' + course.participants + (course.participants === 1 ? ' participant' : ' participants'), 'small mb-1'));
      item.append(element('p', course.startDate ? 'Desired start: ' + course.startDate + ' (provisional)' : 'Dates to be agreed', 'small text-muted mb-1'));
      if (course.billedParticipants > course.participants) item.append(element('p', 'Minimum fee for ' + course.billedParticipants + ' participants applies.', 'small text-muted mb-1'));
      item.append(element('p', currency(course.totalCents), 'fw-bold text-primary mb-0'));
      lines.append(item);
    });
    $('quote-subtotal').textContent = currency(data.netCents);
    $('quote-tax').textContent = data.tax.approved ? currency(data.taxCents) : 'To confirm';
    $('quote-total').textContent = currency(data.totalCents);
    $('quote-total-label').textContent = data.paymentReady ? 'Total' : 'Indicative total';
    $('quote-tax-note').textContent = data.tax.note;
    renderTerms(data.commercialTerms,'quote-terms');
    $('prerequisite-area').hidden = !data.needsPrerequisiteConfirmation;
    $('prerequisiteConfirmed').required = data.needsPrerequisiteConfirmation;
    $('prepare-order').textContent = data.paymentReady ? 'Prepare invoice & documents' : 'Prepare preview documents';
    $('preview-banner').hidden = data.paymentReady || (config.mode === 'live' && !$('country').value);
    if (config.mode === 'live' && !data.paymentReady && $('country').value) $('preview-banner').textContent = 'A payable invoice is not yet available for this billing country. You can prepare a proposal and an invoice preview.';
  }
  async function refreshQuote() {
    const version = ++quoteRequest;
    $('prepare-order').disabled = true;
    quote = null;
    try {
      const data = await api('quote', {courses:cart.courses,country:$('country').value});
      if (version !== quoteRequest) return;
      quote = data;
      renderQuote(data);
    } finally { if (version === quoteRequest) $('prepare-order').disabled = !quote; }
  }
  function bankField(label, value) {
    if (!value) return;
    $('payment-details').append(element('dt',label,'small'),element('dd',value,'mb-2'));
  }
  function showOrder(data) {
    order = data;
    $('checkout-layout').hidden = true;
    $('order-result').hidden = false;
    $('resume-area').hidden = true;
    $('result-heading').textContent = data.expired ? 'This quotation has expired' : data.preview ? 'Your preview documents are ready' : 'Your documents are ready';
    $('result-introduction').textContent = data.expired ? 'Return to the calculator to prepare an updated quotation before arranging payment. The original documents remain available for your records.' : data.preview ? 'Download the proposal, sample payment request and any requested agreement. These preview documents must not be used to make a payment.' : 'Send the pro forma invoice to your finance team or arrange the bank transfer now. Training dates will be confirmed separately.';
    $('result-reference').textContent = data.reference;
    $('result-validity').hidden = !data.validUntil;
    $('result-validity').textContent = data.validUntil ? 'Valid until: '+dateLabel(data.validUntil) : '';
    renderTerms(data.commercialTerms,'result-terms');
    $('result-customer').textContent = data.customer.companyName + ' · ' + data.customer.email;
    $('document-list').replaceChildren();
    data.documents.forEach(document => {
      const button = element('button',document.label + ' · PDF','btn btn-outline-primary');
      button.type = 'button';
      button.addEventListener('click', () => download(document.kind,document.filename,button));
      $('document-list').append(button);
    });
    $('result-amount').textContent = (data.expired ? 'Quoted: ' : data.preview ? 'Indicative: ' : 'Payable: ') + currency(data.quote.totalCents);
    $('payment-details').replaceChildren();
    if (data.expired) {
      $('payment-message').textContent = 'This quotation expired on '+dateLabel(data.validUntil)+'. Please prepare an updated quotation before making a payment.';
      $('payment-term').textContent = 'Use Change your training plan to return to the calculator.';
    } else if (data.bank) {
      bankField('Beneficiary',data.bank.beneficiary);
      bankField('IBAN',data.bank.iban);
      bankField('SWIFT / BIC',data.bank.swift);
      bankField('Bank',data.bank.name);
      bankField('Bank address',data.bank.address);
      bankField('Correspondent bank',data.bank.correspondent);
      bankField('Payment reference',data.reference);
      $('payment-message').textContent = 'Awaiting bank transfer. Include the payment reference above. A downloaded invoice does not confirm payment.';
      $('payment-term').textContent = data.paymentTerm;
    } else {
      $('payment-message').textContent = 'Payments are not available in this preview. No bank instructions have been included, so this document cannot be mistaken for a payable invoice.';
      $('payment-term').textContent = 'The live version will show the confirmed bank details and the exact payment reference here.';
    }
    $('order-result').focus();
  }
  async function download(kind, filename, button) {
    clearError();
    const original = button.textContent;
    button.disabled = true;
    button.textContent = 'Preparing download…';
    $('download-status').textContent = 'Preparing your ' + (kind === 'pack' ? 'document package' : 'PDF') + '…';
    try {
      const response = await fetch(apiUrl + '?action=document&kind=' + kind, {headers:{Authorization:'Bearer ' + order.token},credentials:'same-origin',signal:AbortSignal.timeout(90000)});
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || 'The document could not be downloaded. Please try again.');
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = element('a');
      link.href = url; link.download = filename; link.hidden = true;
      document.body.append(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(url),60000);
      $('download-status').textContent = 'Download started. Keep these files for your purchasing and finance teams.';
    } catch (failure) { error(failure.message || 'The download could not be prepared.'); $('download-status').textContent = ''; }
    finally { button.disabled = false; button.textContent = original; }
  }
  $('billing-form').addEventListener('input', () => { if (!busy) { requestKey = key(); saveBillingDraft(); } });
  $('country').addEventListener('change', () => { requestKey = key(); saveBillingDraft(); refreshQuote().catch(failure => error(failure.message)); });
  $('download-proposal-preview').addEventListener('click', async () => {
    if (busy || !cart || $('download-proposal-preview').dataset.busy === 'true') return;
    clearError();
    try { await TrainingDocuments.downloadProposal(apiUrl,cart.courses,saveBillingDraft(),$('download-proposal-preview'),$('proposal-status')); }
    catch (failure) { error(failure.message || 'The proposal could not be prepared.'); }
  });
  $('billing-form').addEventListener('submit', async event => {
    event.preventDefault();
    if (busy || !quote) return;
    clearError(); busy = true;
    const customer = saveBillingDraft();
    const body = {courses:cart.courses,customer,quoteFingerprint:quote.quoteFingerprint,includeAgreement:$('includeAgreement').checked,businessAuthorised:$('businessAuthorised').checked,prerequisiteConfirmed:$('prerequisiteConfirmed').checked};
    const controls = [...$('billing-form').elements];
    controls.forEach(control => { control.disabled = true; });
    $('prepare-order').textContent = 'Preparing your order…';
    try { showOrder(await api('order',body)); }
    catch (failure) { error(failure.message); await refreshQuote().catch(() => {}); }
    finally { busy = false; controls.forEach(control => { control.disabled = false; }); $('prepare-order').disabled = !quote; if (quote) $('prepare-order').textContent = quote.paymentReady ? 'Prepare invoice & documents' : 'Prepare preview documents'; }
  });
  $('download-pack').addEventListener('click', () => download('pack',order.reference+'-documents.zip',$('download-pack')));
  $('resume-order').addEventListener('click', async () => { try { showOrder(await api('resume')); } catch (failure) { error(failure.message); } });
  $('new-order').addEventListener('click', () => {
    clearError(); requestKey=key(); $('order-result').hidden=true; $('checkout-layout').hidden=false;
    $('businessAuthorised').checked=false;
    $('companyName').focus();
  });
  async function initialise() {
    try {
      config = await api('config');
      $('resume-area').hidden = !config.resumeAvailable;
      Object.entries(config.countries).sort((a,b)=>a[1].localeCompare(b[1])).forEach(([code,name]) => {
        const option=element('option',name); option.value=code; $('country').append(option);
      });
      Object.entries(TrainingDocuments.readCustomer()).forEach(([name,value]) => {
        const control = $('billing-form').elements.namedItem(name);
        if (control) control.value = value;
      });
      if (config.agreementApproved) $('agreement-label').textContent='Include a training agreement (optional)';
      try { cart = JSON.parse(sessionStorage.getItem(cartKey)); } catch { cart = null; }
      if (!cart || !Array.isArray(cart.courses) || !cart.courses.length) { $('empty-cart').hidden=false; return; }
      await refreshQuote();
      $('checkout-layout').hidden=false;
    } catch (failure) { error(failure.message || 'The order page could not be loaded. Please try again.'); }
    finally { $('order-loading').hidden=true; }
  }
  initialise();
})();
