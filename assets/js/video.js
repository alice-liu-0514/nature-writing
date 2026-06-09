// video.js — poster + 點擊播放（lazy：點擊前不載入影片本體）
export function initVideo() {
  const root = document.body.dataset.root || '';
  document.querySelectorAll('.video').forEach((box) => {
    const start = () => {
      if (box.classList.contains('playing')) return;
      const v = document.createElement('video');
      v.controls = true;
      v.playsInline = true;
      v.preload = 'auto';
      // 沿用 poster 的長寬，讓影片框在載入完成前就有正確高度（避免 0 高度 / 版面跳動）
      const posterImg = box.querySelector('.poster');
      const pw = posterImg && posterImg.getAttribute('width');
      const ph = posterImg && posterImg.getAttribute('height');
      if (pw && ph) { v.setAttribute('width', pw); v.setAttribute('height', ph); }
      if (box.dataset.poster) v.poster = root + box.dataset.poster;
      v.src = root + box.dataset.src;
      box.insertBefore(v, box.firstChild);
      box.classList.add('playing');
      // 點擊屬使用者手勢，優先帶聲音播放；若被擋下則改靜音再播（使用者可用控制列開聲音）
      v.play().catch(() => { v.muted = true; v.play().catch(() => {}); });
    };
    const btn = box.querySelector('.play');
    if (btn) btn.addEventListener('click', start);
    else box.addEventListener('click', start);
  });
}
