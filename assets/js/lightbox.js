// lightbox.js — 由 manifest.json 建相簿縮圖格 + 原生 <dialog> 燈箱
// 內文 figure（data-lightbox="slug"）與相簿縮圖共用同一個燈箱。

let manifest = null;
async function getManifest(root) {
  if (manifest) return manifest;
  const res = await fetch(`${root}assets/img/manifest.json`);
  if (!res.ok) throw new Error('manifest 載入失敗');
  manifest = await res.json();
  return manifest;
}

function createLightbox(m, root) {
  let items = [], idx = 0, essay = '';
  const dlg = document.createElement('dialog');
  dlg.className = 'lightbox';
  dlg.innerHTML = `
    <div class="lb-stage">
      <picture><source class="lb-src" type="image/webp"><img class="lb-img" alt=""></picture>
      <p class="lb-cap"></p>
    </div>
    <div class="lb-count" aria-hidden="true"></div>
    <button class="lb-btn lb-prev" type="button" aria-label="上一張">‹</button>
    <button class="lb-btn lb-next" type="button" aria-label="下一張">›</button>
    <button class="lb-close" type="button" aria-label="關閉">✕</button>`;
  document.body.appendChild(dlg);
  const img = dlg.querySelector('.lb-img');
  const src = dlg.querySelector('.lb-src');
  const cap = dlg.querySelector('.lb-cap');
  const cnt = dlg.querySelector('.lb-count');

  const show = () => {
    const it = items[idx];
    const b = `${root}assets/img/${essay}/${it.slug}`;
    src.srcset = `${b}-1600.webp`;
    img.src = `${b}-1600.jpg`;
    img.alt = it.alt || '';
    cap.textContent = it.caption || it.alt || '';
    cnt.textContent = `${idx + 1} / ${items.length}`;
  };
  const go = (d) => { idx = (idx + d + items.length) % items.length; show(); };

  dlg.querySelector('.lb-prev').addEventListener('click', () => go(-1));
  dlg.querySelector('.lb-next').addEventListener('click', () => go(1));
  dlg.querySelector('.lb-close').addEventListener('click', () => dlg.close());
  dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); }); // 點背景關閉
  dlg.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') go(-1);
    else if (e.key === 'ArrowRight') go(1);
  });

  return {
    open(e, i) { essay = e; items = m[e] || []; idx = i; show(); if (!dlg.open) dlg.showModal(); }
  };
}

export async function initGallery() {
  const root = document.body.dataset.root || '';
  const galleries = document.querySelectorAll('[data-gallery]');
  const inlines = document.querySelectorAll('[data-lightbox]');
  if (!galleries.length && !inlines.length) return;

  const m = await getManifest(root);
  const lb = createLightbox(m, root);

  galleries.forEach((c) => {
    const essay = c.dataset.gallery;
    const items = m[essay] || [];
    const frag = document.createDocumentFragment();
    items.forEach((it, i) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.setAttribute('aria-label', `放大：${it.alt || it.slug}`);
      btn.innerHTML =
        `<picture><source type="image/webp" srcset="${root}assets/img/${essay}/thumbs/${it.slug}-400.webp">` +
        `<img src="${root}assets/img/${essay}/thumbs/${it.slug}-400.jpg" width="${it.thumb.w}" height="${it.thumb.h}" ` +
        `loading="lazy" decoding="async" alt="${it.alt || ''}"></picture>`;
      btn.addEventListener('click', () => lb.open(essay, i));
      frag.appendChild(btn);
    });
    c.appendChild(frag);
  });

  inlines.forEach((fig) => {
    const slug = fig.dataset.lightbox;
    let hit = null;
    for (const essay in m) {
      const i = m[essay].findIndex((x) => x.slug === slug);
      if (i >= 0) { hit = [essay, i]; break; }
    }
    if (!hit) return;
    fig.style.cursor = 'zoom-in';
    fig.addEventListener('click', () => lb.open(hit[0], hit[1]));
  });
}
