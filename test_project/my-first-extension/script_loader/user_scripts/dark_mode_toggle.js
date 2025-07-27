if (document.body) {
  const style = document.createElement('style');
  style.id = 'dark-mode-style';
  style.textContent = `
    html {
      filter: invert(100%) hue-rotate(180deg);
      background-color: #000 !important;
    }
    body {
      background-color: #000 !important;
    }
    img, video, iframe {
      filter: invert(100%) hue-rotate(180deg);
    }
  `;
  document.head.appendChild(style);
  console.log('Dark mode script injected.');
} else {
  console.log('Dark mode script: document.body not ready.');
}