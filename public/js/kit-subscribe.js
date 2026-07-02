(function () {
  var cfg = window.NP_KIT || {};
  var FORM_ID = cfg.formId;
  var PUB_KEY = cfg.publicKey;

  if (!FORM_ID || !PUB_KEY || FORM_ID === 'YOUR_KIT_FORM_ID') return;

  document.querySelectorAll('.newsletter-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var emailEl = form.querySelector('[name="email"]');
      var nameEl = form.querySelector('[name="first_name"]');
      var btn = form.querySelector('button[type="submit"]');
      var errEl = form.querySelector('.kit-error');

      var email = emailEl ? emailEl.value.trim() : '';
      if (!email) return;

      var origText = btn ? btn.textContent : '';
      if (btn) { btn.textContent = 'Subscribing…'; btn.disabled = true; }
      if (errEl) errEl.textContent = '';

      var payload = { api_key: PUB_KEY, email: email };
      if (nameEl && nameEl.value.trim()) payload.first_name = nameEl.value.trim();

      fetch('https://api.convertkit.com/v3/forms/' + FORM_ID + '/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).then(function (res) {
        if (res.ok) {
          window.location.href = '/thank-you/';
        } else {
          throw new Error('non-2xx: ' + res.status);
        }
      }).catch(function () {
        if (btn) { btn.textContent = origText; btn.disabled = false; }
        if (errEl) errEl.textContent = 'Something went wrong — please try again.';
      });
    });
  });
})();
