// Mobile navigation
(function () {
  var toggle = document.querySelector('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = document.body.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }
  document.querySelectorAll('.sub-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var sub = btn.parentElement.querySelector('.sub');
      var open = sub.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(open));
    });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && document.body.classList.contains('nav-open')) {
      document.body.classList.remove('nav-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.focus();
    }
  });
})();

// Contact form: sends through Web3Forms when an access key is configured,
// otherwise opens the visitor's email app with the message pre-filled.
(function () {
  var form = document.getElementById('contact-form');
  if (!form) return;
  var status = form.querySelector('.form-status');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (form.botcheck && form.botcheck.checked) return;
    var data = new FormData(form);
    var name = (data.get('first_name') + ' ' + data.get('last_name')).trim();
    var key = form.dataset.key;

    if (!key) {
      var subject = 'Website message from ' + name;
      var body = data.get('message') + '\n\n— ' + name + ' (' + data.get('email') + ')';
      window.location.href = 'mailto:' + form.dataset.to +
        '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      status.className = 'form-status ok';
      status.textContent = 'Your email app should open with your message ready to send.';
      return;
    }

    data.append('access_key', key);
    data.append('subject', 'New message from knowledgeislight.us — ' + name);
    data.append('from_name', 'Knowledge Is Light website');
    var btn = form.querySelector('button[type=submit]');
    btn.disabled = true;
    status.className = 'form-status';
    status.textContent = 'Sending…';
    fetch('https://api.web3forms.com/submit', { method: 'POST', body: data })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.success) throw new Error(res.message);
        form.reset();
        status.className = 'form-status ok';
        status.textContent = 'JazakAllahu khayran! Your message has been sent — we’ll be in touch soon, inshaAllah.';
      })
      .catch(function () {
        status.className = 'form-status err';
        status.innerHTML = 'Sorry, something went wrong. Please email us directly at <a href="mailto:' +
          form.dataset.to + '">' + form.dataset.to + '</a>.';
      })
      .finally(function () { btn.disabled = false; });
  });
})();
