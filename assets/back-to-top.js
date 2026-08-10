(() => {
  const button = document.querySelector(".back-to-top");
  if (!button) return;

  document.documentElement.classList.add("back-to-top-enhanced");
  const update = () => button.classList.toggle("is-visible", window.scrollY > 480);
  update();
  window.addEventListener("scroll", update, { passive: true });
})();
