// main.js — 進入點。漸進增強：無 JS 也能讀，有 JS 加上克制的互動。
import { initReveal, initProgress, initChapterNav } from './reveal.js';
import { initGallery } from './lightbox.js';
import { initVideo } from './video.js';

initReveal();
initProgress();
initChapterNav();
initVideo();
initGallery().catch((e) => console.warn('[gallery]', e));
