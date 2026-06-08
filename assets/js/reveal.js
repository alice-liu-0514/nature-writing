// reveal.js — 克制的滾動揭露、閱讀進度、章節導覽、颱風褪色
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

// 段落揭露：只做極小位移，進入即顯示後不再觀察
export function initReveal() {
  const els = document.querySelectorAll('[data-reveal]');
  if (!els.length) return;
  const showAll = () => els.forEach(e => e.classList.add('is-visible'));
  if (reduce || !('IntersectionObserver' in window)) { showAll(); return; }
  const io = new IntersectionObserver((entries) => {
    for (const en of entries) {
      if (en.isIntersecting) { en.target.classList.add('is-visible'); io.unobserve(en.target); }
    }
  }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
  els.forEach(e => io.observe(e));
}

// 頂部閱讀進度條（依文章捲動比例）
export function initProgress() {
  const bar = document.querySelector('.progress');
  const art = document.querySelector('[data-progress]') || document.querySelector('.essay-article');
  if (!bar || !art) return;
  let ticking = false;
  const update = () => {
    const rect = art.getBoundingClientRect();
    const total = art.offsetHeight - innerHeight;
    const passed = Math.min(Math.max(-rect.top, 0), Math.max(total, 1));
    bar.style.transform = `scaleX(${total > 0 ? passed / total : 0})`;
    ticking = false;
  };
  addEventListener('scroll', () => { if (!ticking) { requestAnimationFrame(update); ticking = true; } }, { passive: true });
  addEventListener('resize', update, { passive: true });
  update();
}

// 左側章節圓點：scroll-spy 高亮目前段落
export function initChapterNav() {
  const nav = document.querySelector('.chapter-nav');
  if (!nav) return;
  const links = [...nav.querySelectorAll('a')];
  const map = new Map();
  links.forEach(a => {
    const sec = document.getElementById(a.getAttribute('href').slice(1));
    if (sec) map.set(sec, a);
  });
  if (!map.size) return;
  const io = new IntersectionObserver((entries) => {
    for (const en of entries) {
      if (en.isIntersecting) {
        links.forEach(l => l.classList.remove('is-active'));
        map.get(en.target)?.classList.add('is-active');
      }
    }
  }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
  map.forEach((_, sec) => io.observe(sec));
}

// 颱風褪色：滾入視窗即轉灰（一次性，色彩不再回來）
export function initDestash() {
  const els = document.querySelectorAll('.destash');
  if (!els.length) return;
  const io = new IntersectionObserver((entries) => {
    for (const en of entries) {
      if (en.isIntersecting && en.intersectionRatio >= 0.35) {
        en.target.classList.add('is-grey');
        io.unobserve(en.target);
      }
    }
  }, { threshold: [0, 0.35, 0.7] });
  els.forEach(e => io.observe(e));
}
