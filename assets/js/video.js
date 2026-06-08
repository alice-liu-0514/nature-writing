// video.js — poster + 點擊播放（lazy：點擊前不載入影片本體）
export function initVideo() {
  const root = document.body.dataset.root || '';
  document.querySelectorAll('.video').forEach((box) => {
    const start = () => {
      if (box.classList.contains('playing')) return;
      const v = document.createElement('video');
      v.controls = true;
      v.playsInline = true;
      v.preload = 'metadata';
      v.autoplay = true;
      if (box.dataset.poster) v.poster = root + box.dataset.poster;
      v.src = root + box.dataset.src;
      box.insertBefore(v, box.firstChild);
      box.classList.add('playing');
      v.play().catch(() => {});
    };
    const btn = box.querySelector('.play');
    if (btn) btn.addEventListener('click', start);
    else box.addEventListener('click', start);
  });
}
