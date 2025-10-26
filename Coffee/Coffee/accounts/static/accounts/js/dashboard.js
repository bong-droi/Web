(() => {
  const frame = document.getElementById('mainFrame');
  const buttons = Array.from(document.querySelectorAll('.nav-btn'));
  const ACTIVE_KEY = 'coffee_owner_active_tab';

  // Chuyển tab
  function setActive(btn) {
    buttons.forEach(b => b.classList.toggle('active', b === btn));
    const url = btn.getAttribute('data-url');
    if (url && frame) {
      frame.src = url;
      try { localStorage.setItem(ACTIVE_KEY, url); } catch (e) {}
    }
  }

  // Click handler
  buttons.forEach(btn => {
    btn.addEventListener('click', () => setActive(btn));
  });

  // Khôi phục tab trước đó
  try {
    const saved = localStorage.getItem(ACTIVE_KEY);
    const found = buttons.find(b => b.getAttribute('data-url') === saved);
    if (saved && found) setActive(found);
  } catch (e) {}
})();
