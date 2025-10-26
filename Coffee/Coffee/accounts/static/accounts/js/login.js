(function () {
  const form = document.getElementById('loginForm');
  const submitBtn = document.getElementById('submitBtn');
  const username = document.getElementById('username');
  const pwd = document.getElementById('password');
  const eyeBtn = document.querySelector('.eye');

  // Hiện/ẩn mật khẩu
  eyeBtn?.addEventListener('click', () => {
    const isPwd = pwd.type === 'password';
    pwd.type = isPwd ? 'text' : 'password';
    eyeBtn.setAttribute('aria-label', isPwd ? 'Ẩn mật khẩu' : 'Hiện mật khẩu');
  });

  // Validate nhanh + trạng thái loading
  form?.addEventListener('submit', (e) => {
    const u = username.value.trim();
    const p = pwd.value.trim();
    if (!u || !p) {
      e.preventDefault();
      document.getElementById('usernameHint').textContent = u ? '' : 'Vui lòng nhập tên đăng nhập.';
      document.getElementById('passwordHint').textContent = p ? '' : 'Vui lòng nhập mật khẩu.';
      (u ? pwd : username).focus();
      return;
    }
    submitBtn.disabled = true;
    const old = submitBtn.textContent;
    submitBtn.textContent = 'Đang đăng nhập…';
    setTimeout(() => {  // phòng khi request bị treo lúc dev
      if (submitBtn.disabled) {
        submitBtn.disabled = false;
        submitBtn.textContent = old;
      }
    }, 8000);
  });
})();
