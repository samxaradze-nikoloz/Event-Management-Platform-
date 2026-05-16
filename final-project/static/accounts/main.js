// ── Login form ──
const loginForm = document.getElementById('login-form');
if (loginForm) {
  loginForm.addEventListener('submit', function (e) {
    const btn = document.getElementById('login-btn');
    btn.classList.add('btn-loading');
    btn.textContent = 'Signing in...';
  });
}

// ── Register form ──
const registerForm = document.getElementById('register-form');
if (registerForm) {

  // Password strength
  const passwordInput = document.getElementById('password');
  if (passwordInput) {
    const bar = document.createElement('div');
    bar.innerHTML = '<div class="strength-bar"><div class="strength-fill" id="strength-fill"></div></div><div class="strength-label" id="strength-label"></div>';
    passwordInput.parentNode.appendChild(bar);

    passwordInput.addEventListener('input', function () {
      const val = this.value;
      const fill = document.getElementById('strength-fill');
      const label = document.getElementById('strength-label');
      fill.className = 'strength-fill';

      if (val.length === 0) {
        label.textContent = '';
      } else if (val.length < 6) {
        fill.classList.add('strength-weak');
        label.textContent = 'Weak password';
        label.style.color = 'var(--red)';
      } else if (val.length < 10 || !/[0-9]/.test(val)) {
        fill.classList.add('strength-medium');
        label.textContent = 'Medium password';
        label.style.color = 'var(--amber)';
      } else {
        fill.classList.add('strength-strong');
        label.textContent = 'Strong password';
        label.style.color = 'var(--green)';
      }
    });
  }

  // Submit loading state
  registerForm.addEventListener('submit', function () {
    const btn = document.getElementById('register-btn');
    btn.classList.add('btn-loading');
    btn.textContent = 'Creating account...';
  });
}

// ── Auto-dismiss toasts ──
document.querySelectorAll('.toast').forEach(function (toast) {
  setTimeout(function () {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-6px)';
    toast.style.transition = 'all 0.3s';
    setTimeout(function () { toast.remove(); }, 300);
  }, 3500);
});