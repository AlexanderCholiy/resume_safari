document.addEventListener('DOMContentLoaded', () => {
  const styles = ['classic', 'modern'];
  const styleToggle = document.getElementById('style-toggle');
  const styleIcon = document.getElementById('style-icon');
  const body = document.body;
  const main = document.querySelector('main');

  const styleIcons = {
    classic: 'bx-font',
    modern: 'bx-bold'
  };

  const styleTitles = {
    classic: 'Классический стиль',
    modern: 'Современный стиль'
  };

  const styleFonts = {
    classic: '/static/css/fonts_classic.css',
    modern: '/static/css/fonts_modern.css'
  };

  let currentFontLink = null;

  function applyStyle(style) {
    styles.forEach(s => {
      body.classList.remove(`${s}-style`);
      main?.classList.remove(`${s}-style`);
    });

    body.classList.add(`${style}-style`);
    main?.classList.add(`${style}-style`);

    styleIcon.className = 'bx ' + styleIcons[style];
    styleToggle.title = styleTitles[style];

    if (currentFontLink) {
      currentFontLink.remove();
    }

    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = styleFonts[style];
    document.head.appendChild(link);
    currentFontLink = link;
  }

  function getSavedStyle() {
    return localStorage.getItem('style') || 'modern';
  }

  function setStyle(style) {
    localStorage.setItem('style', style);
    applyStyle(style);
  }

  function nextStyle(current) {
    const index = styles.indexOf(current);
    return styles[(index + 1) % styles.length];
  }

  styleToggle?.addEventListener('click', () => {
    const currentStyle = getSavedStyle();
    const newStyle = nextStyle(currentStyle);
    setStyle(newStyle);
  });

  const savedStyle = getSavedStyle();
  setStyle(savedStyle);
});