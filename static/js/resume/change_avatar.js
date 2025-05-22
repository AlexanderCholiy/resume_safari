document.addEventListener('DOMContentLoaded', () => {
  const avatar = document.getElementById('default-avatar');
  if (!avatar) return;

  function updateDefaultAvatar() {
    const light = avatar.dataset.avatarLight;
    const dark = avatar.dataset.avatarDark;
    const isDark = document.body.classList.contains('dark');
    const newSrc = isDark ? dark : light;

    if (avatar.src.endsWith(newSrc)) return;

    avatar.style.opacity = 0;

    setTimeout(() => {
      avatar.src = newSrc;
      avatar.onload = () => {
        avatar.style.opacity = 1;
      };
    }, 100);
  }

  updateDefaultAvatar();

  const observer = new MutationObserver(() => {
    updateDefaultAvatar();
  });

  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ['class']
  });
});