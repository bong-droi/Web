(() => {
  const links = Array.from(document.querySelectorAll('.nav-link'));
  const brand = document.querySelector('.brand-link');

  function setActive(el){
    links.forEach(a => a.classList.toggle('active', a === el));
  }
  links.forEach(a => a.addEventListener('click', () => setActive(a)));

  brand?.addEventListener('click', () => {
    links.forEach(a => a.classList.remove('active')); // về Home thì không tab nào active
  });
})();
