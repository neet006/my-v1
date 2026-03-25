/**
 * auth.js — Client-side form validation for login and signup pages.
 */
(function () {
  'use strict';

  function showInlineError(formEl, msg) {
    let box = formEl.querySelector('.auth-error');
    if (!box) {
      box = document.createElement('div');
      box.className = 'auth-error';
      formEl.prepend(box);
    }
    box.innerHTML = '<span>⚠️</span> ' + msg;
    box.style.display = 'flex';
  }

  // ── Login form ───────────────────────────────────────────────
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
      const email    = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      if (!email || !password) {
        e.preventDefault();
        showInlineError(loginForm, 'Please fill in all fields.');
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        e.preventDefault();
        showInlineError(loginForm, 'Please enter a valid email address.');
        return;
      }
      // Let the form submit to Flask
    });
  }

  // ── Signup form ──────────────────────────────────────────────
  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', function (e) {
      const name    = document.getElementById('name').value.trim();
      const email   = document.getElementById('email').value.trim();
      const pw      = document.getElementById('password').value;
      const confirm = document.getElementById('confirm_password').value;

      if (!name || !email || !pw || !confirm) {
        e.preventDefault();
        showInlineError(signupForm, 'Please fill in all fields.');
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        e.preventDefault();
        showInlineError(signupForm, 'Please enter a valid email address.');
        return;
      }
      if (pw.length < 6) {
        e.preventDefault();
        showInlineError(signupForm, 'Password must be at least 6 characters.');
        return;
      }
      if (pw !== confirm) {
        e.preventDefault();
        showInlineError(signupForm, 'Passwords do not match.');
        return;
      }
    });
  }
})();
