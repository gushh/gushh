(() => {
  'use strict';

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } },
  };

  /* ------------------------------------------------------------ sound */
  // Tiny square-wave synth. Muted until the visitor turns it on.
  let audio = null;
  let soundOn = store.get('gus-sound') === 'on';
  function tone(freq, start, dur, type = 'square', vol = 0.06) {
    const o = audio.createOscillator();
    const g = audio.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, start);
    g.gain.setValueAtTime(vol, start);
    g.gain.exponentialRampToValueAtTime(0.0001, start + dur);
    o.connect(g).connect(audio.destination);
    o.start(start);
    o.stop(start + dur + 0.02);
  }
  function sfx(name) {
    if (!soundOn) return;
    audio = audio || new (window.AudioContext || window.webkitAudioContext)();
    const t = audio.currentTime + 0.01;
    const songs = {
      move: [[880, 0, 0.05]],
      select: [[660, 0, 0.06], [990, 0.06, 0.09]],
      coin: [[988, 0, 0.08], [1319, 0.08, 0.3]],
      achievement: [[523, 0, 0.1], [659, 0.1, 0.1], [784, 0.2, 0.1], [1047, 0.3, 0.3]],
      secret: [[392, 0, .1], [523, .1, .1], [659, .2, .1], [784, .3, .1], [659, .4, .1], [784, .5, .4]],
      tick: [[440, 0, 0.04, 'triangle', 0.08]],
    };
    (songs[name] || []).forEach(([f, s, d, type, vol]) => tone(f, t + s, d, type, vol));
  }

  const soundBtn = $('#sound-toggle');
  function paintSound() {
    soundBtn.setAttribute('aria-pressed', String(soundOn));
    $('.lbl', soundBtn).textContent = soundOn ? 'ON' : 'OFF';
  }
  soundBtn.addEventListener('click', () => {
    soundOn = !soundOn;
    store.set('gus-sound', soundOn ? 'on' : 'off');
    paintSound();
    sfx('select');
  });
  paintSound();

  /* ------------------------------------------------------------ theme */
  // <picture> sources follow the chosen theme instead of the OS setting.
  function applyTheme(t) {
    root.dataset.theme = t;
    $$('picture source[media]').forEach((s) => {
      if (!s.dataset.q) s.dataset.q = s.media;
      s.media = t === 'dark' ? 'all' : 'not all';
    });
    $('meta[name="theme-color"]').content = t === 'dark' ? '#0b0a1f' : '#e6f2ff';
    $('#theme-toggle').setAttribute('aria-label', t === 'dark' ? 'Cambiar a modo día' : 'Cambiar a modo noche');
  }
  $('#theme-toggle').addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    store.set('gus-theme', next);
    applyTheme(next);
    sfx('select');
  });
  applyTheme(root.dataset.theme);

  /* ------------------------------------------------------------ start */
  // "Insertá tu idea": jump straight to level 1, the idea form
  const wipe = $('#wipe');
  function start() {
    sfx('coin');
    const go = () => {
      $('#idea').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
      setTimeout(() => $('#idea textarea').focus({ preventScroll: true }), reduced ? 0 : 500);
    };
    if (reduced) return go();
    wipe.classList.remove('go');
    void wipe.offsetWidth;
    wipe.classList.add('go');
    setTimeout(go, 320);
  }
  $('#start').addEventListener('click', start);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && window.scrollY < innerHeight * 0.5 && document.activeElement === document.body) start();
  });

  /* ------------------------------------------------ level 1: the idea */
  const form = $('#idea');
  const fields = { nombre: form.elements.nombre, idea: form.elements.idea, para: form.elements.para };
  const fill = $('#xp-fill');
  const rank = $('#xp-rank');
  const RANKS = [[0, 'SIN EMPEZAR'], [1, 'CHISPA'], [80, 'BOCETO'], [180, 'BUENA IDEA'], [320, '¡LEGENDARIA!']];
  let lastRank = '';
  function draft() {
    return {
      nombre: fields.nombre.value, idea: fields.idea.value, para: fields.para.value,
      plazo: (form.querySelector('input[name="plazo"]:checked') || {}).value || '',
    };
  }
  function paintXP() {
    const n = fields.idea.value.trim().length + (fields.para.value.trim() ? 40 : 0) + (draft().plazo ? 30 : 0);
    fill.style.width = Math.min(100, (n / 320) * 100) + '%';
    const r = RANKS.filter(([min]) => n >= min).pop()[1];
    if (r !== lastRank) {
      if (lastRank && n > 0) sfx('move');
      lastRank = r;
      rank.textContent = r;
    }
  }
  function save() { store.set('gus-idea-draft', JSON.stringify(draft())); }
  try {
    const d = JSON.parse(store.get('gus-idea-draft') || '{}');
    ['nombre', 'idea', 'para'].forEach((k) => { if (d[k]) fields[k].value = d[k]; });
    if (d.plazo) { const r = form.querySelector(`input[name="plazo"][value="${CSS.escape(d.plazo)}"]`); if (r) r.checked = true; }
  } catch (e) { /* ignore a broken draft */ }
  form.addEventListener('input', () => { paintXP(); save(); fields.idea.removeAttribute('aria-invalid'); $('#quest-error').textContent = ''; });
  paintXP();

  function brief() {
    const d = draft();
    const lines = ['¡Hola Gus!', '', '💡 Mi idea:', d.idea.trim(), ''];
    if (d.para.trim()) lines.push('👥 Para quién es:', d.para.trim(), '');
    if (d.plazo) lines.push('📅 Para cuándo:', d.plazo, '');
    lines.push(d.nombre.trim() ? '¡Gracias! ' + d.nombre.trim() : '¡Gracias!');
    return lines.join('\n');
  }
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!fields.idea.value.trim()) {
      fields.idea.setAttribute('aria-invalid', 'true');
      $('#quest-error').textContent = '¡FALTA LA IDEA! CONTAME AUNQUE SEA EN UNA LÍNEA.';
      fields.idea.focus();
      sfx('move');
      return;
    }
    const name = fields.nombre.value.trim();
    const subject = 'Tengo una idea 💡' + (name ? ' — ' + name : '');
    location.href = 'mailto:gus@trece.ar?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(brief());
    $('#quest-done').hidden = false;
    sfx('achievement');
    popup('NIVEL 1 COMPLETADO', 'PRÓXIMO: PRESUPUESTO');
  });
  $('#copy-idea').addEventListener('click', async (e) => {
    const btn = e.currentTarget;
    const text = 'Para: gus@trece.ar\n\n' + brief();
    try { await navigator.clipboard.writeText(text); btn.textContent = '¡COPIADA!'; } catch (err) {
      fields.idea.select();
      btn.textContent = 'COPIALA A MANO';
    }
    sfx('select');
  });

  /* --------------------------------------------------------- dialogue */
  const dialog = $('#dialog');
  const dText = $('.dialog-text', dialog);
  const paragraphs = $$('.sr-only p', dialog).map((p) => p.innerHTML);
  let typing = null;
  function finishDialog() {
    clearInterval(typing);
    dText.innerHTML = paragraphs.map((h) => `<p>${h}</p>`).join('');
    dialog.classList.add('done');
  }
  function typeDialog() {
    if (reduced) return finishDialog();
    // type characters while keeping inline tags (<strong>) intact
    const tokens = [];
    paragraphs.forEach((html, i) => {
      tokens.push({ open: '<p>' });
      html.split(/(<[^>]+>)/).forEach((part) => {
        if (!part) return;
        if (part.startsWith('<')) tokens.push({ tag: part });
        else [...part].forEach((ch) => tokens.push({ ch }));
      });
      tokens.push({ close: '</p>', pause: i < paragraphs.length - 1 });
    });
    let out = '';
    let i = 0;
    let wait = 0;
    typing = setInterval(() => {
      if (wait > 0) { wait--; return; }
      while (i < tokens.length && !tokens[i].ch) {
        const t = tokens[i++];
        out += t.open || t.tag || t.close || '';
        if (t.pause) { wait = 18; break; }
      }
      if (i < tokens.length && tokens[i].ch) {
        out += tokens[i++].ch;
        if (i % 3 === 0) sfx('tick');
      }
      dText.innerHTML = out;
      if (i >= tokens.length) finishDialog();
    }, 22);
  }
  dialog.addEventListener('click', finishDialog);
  $('.dialog-skip', dialog).addEventListener('click', (e) => { e.stopPropagation(); finishDialog(); });
  once(dialog, typeDialog);

  /* -------------------------------------------------------- inventory */
  const grid = $('#inv-grid');
  const slots = [];
  let current = 0;
  function select(i, focus) {
    current = (i + slots.length) % slots.length;
    slots.forEach((s, k) => {
      s.el.setAttribute('aria-selected', String(k === current));
      s.el.tabIndex = k === current ? 0 : -1;
    });
    const s = slots[current];
    $('#inv-img').src = s.item.sprite;
    $('#inv-img').alt = s.item.name;
    $('#inv-name').textContent = s.item.name;
    $('#inv-cat').textContent = s.cat.category;
    $('#inv-type').textContent = s.cat.type.toUpperCase();
    $('#inv-color').textContent = s.item.color.toUpperCase();
    $('#inv-swatch').style.background = s.item.color;
    if (focus) s.el.focus();
  }
  fetch('gen/stack.json')
    .then((r) => r.json())
    .then((stack) => {
      stack.forEach((cat) => {
        const box = document.createElement('div');
        box.className = 'inv-cat';
        box.setAttribute('role', 'group');
        box.setAttribute('aria-label', cat.category);
        box.innerHTML = `<h3 aria-hidden="true">${cat.category}</h3><div class="inv-items"></div>`;
        cat.items.forEach((item) => {
          const b = document.createElement('div');
          b.className = 'slot';
          b.setAttribute('role', 'option');
          b.innerHTML = `<img src="${item.sprite}" alt="" width="36" height="36"><span>${item.name}</span>`;
          const idx = slots.length;
          b.addEventListener('click', () => { select(idx, true); sfx('select'); });
          b.addEventListener('mouseenter', () => { if (idx !== current) { select(idx); sfx('move'); } });
          $('.inv-items', box).appendChild(b);
          slots.push({ el: b, item, cat });
        });
        grid.appendChild(box);
      });
      $('#inv-count').textContent = slots.length;
      select(0);
    })
    .catch(() => {
      // offline or file:// without a server: fall back to the static SVG inventory
      $('.inventory').outerHTML = $('noscript').textContent;
    });
  grid.addEventListener('keydown', (e) => {
    const map = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1, Home: -Infinity, End: Infinity };
    if (!(e.key in map)) return;
    e.preventDefault();
    const d = map[e.key];
    select(d === -Infinity ? 0 : d === Infinity ? slots.length - 1 : current + d, true);
    sfx('move');
  });

  /* ----------------------------------------------------- achievements */
  $$('.achievement').forEach((a, i) => {
    if (reduced) return;
    a.classList.add('hidden');
    once(a, () => {
      setTimeout(() => {
        a.classList.remove('hidden');
        a.classList.add('shown');
        sfx('achievement');
      }, i * 120);
    }, 0.35);
  });

  /* --------------------------------------------------------- continue */
  const cd = $('#countdown');
  const label = $('#continue-label');
  once($('#continue'), () => {
    let n = 9;
    cd.textContent = n;
    const timer = setInterval(() => {
      n--;
      if (n >= 0) { cd.textContent = n; sfx('tick'); }
      if (n < 0) {
        clearInterval(timer);
        label.textContent = 'GAME OVER';
        cd.textContent = '';
        setTimeout(() => { label.textContent = 'LAS BUENAS IDEAS NO TIENEN GAME OVER'; }, 2200);
      }
    }, 1000);
  }, 0.6);

  /* ------------------------------------------------------ konami code */
  const code = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
  let pos = 0;
  document.addEventListener('keydown', (e) => {
    const k = e.key.length === 1 ? e.key.toLowerCase() : e.key;
    pos = k === code[pos] ? pos + 1 : (k === code[0] ? 1 : 0);
    if (pos === code.length) { pos = 0; secret(); }
  });
  let taps = 0;
  let tapTimer;
  $('#footer-art').addEventListener('click', () => {
    taps++;
    clearTimeout(tapTimer);
    tapTimer = setTimeout(() => { taps = 0; }, 1200);
    if (taps >= 5) { taps = 0; secret(); }
  });
  function popup(title, sub) {
    const p = $('#popup');
    p.innerHTML = `<small>${sub}</small>${title}`;
    p.classList.add('on');
    setTimeout(() => p.classList.remove('on'), 3200);
  }
  function secret() {
    sfx('secret');
    popup('¡DESFILE DE ELEPHPANTS!', 'CÓDIGO SECRETO');
    if (reduced) return;
    const parade = $('#parade');
    for (let i = 0; i < 7; i++) {
      const e = document.createElement('div');
      e.className = 'ele';
      e.style.animationDelay = `${i * 0.45}s, 0s`;
      parade.appendChild(e);
      setTimeout(() => e.remove(), 7000 + i * 450 + 200);
      const h = document.createElement('div');
      h.className = 'heart';
      h.textContent = '♥';
      h.style.left = `${10 + Math.random() * 80}%`;
      h.style.animationDelay = `${i * 0.3}s`;
      parade.appendChild(h);
      setTimeout(() => h.remove(), 2600 + i * 300);
    }
  }

  /* ---------------------------------------------------------- helpers */
  function once(el, fn, threshold = 0.3) {
    if (!('IntersectionObserver' in window)) return fn();
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { io.disconnect(); fn(); }
      });
    }, { threshold });
    io.observe(el);
  }
})();
