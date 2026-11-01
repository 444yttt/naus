(() => {
  const reduce = matchMedia('(prefers-reduced-motion:reduce)').matches;
  const cl = x => Math.max(0, Math.min(1, x));

  // smooth scrolling (wheel only; touch keeps native scrolling)
  let lenis = null;
  if (!reduce && window.Lenis) {
    lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
    const raf = t => { lenis.raf(t); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
  }
  document.querySelectorAll('a[href^="#"]').forEach(a => a.addEventListener('click', e => {
    const id = a.getAttribute('href'), el = id.length > 1 && document.querySelector(id);
    if (!lenis || !el) return;
    e.preventDefault(); lenis.scrollTo(el, { duration: 1.6 });
  }));

  // hero / page titles: letters rise from a mask
  document.querySelectorAll('[data-split]').forEach(el => {
    const nodes = [...el.childNodes]; el.textContent = ''; let i = 0;
    nodes.forEach(n => {
      if (n.nodeType === 3) [...n.textContent].forEach(c => { const s = document.createElement('span'); s.className = 'ch'; s.textContent = c; s.style.setProperty('--i', i++); s.setAttribute('aria-hidden', 'true'); el.append(s); });
      else { n.classList.add('ch'); n.style.setProperty('--i', i++); n.setAttribute('aria-hidden', 'true'); el.append(n); }
    });
  });

  // section headings: the English line rises from a mask, the Japanese line fades in after it
  document.querySelectorAll('h2').forEach(h => {
    const t = h.firstChild; if (!t || t.nodeType !== 3) return;
    const m = document.createElement('span'); m.className = 'mask';
    const i = document.createElement('span'); i.className = 'mi'; i.textContent = t.textContent;
    m.append(i); h.replaceChild(m, t); h.classList.add('reveal');
    const sub = h.querySelector('.sub'); if (sub) { sub.classList.add('fade'); sub.style.setProperty('--d', 3); }
  });
  document.querySelectorAll('.grid li, .steps li, .note, form, main > p, main > .st, dl > *, .blk > p, .blk li').forEach(el => {
    el.classList.add('fade', 'reveal');
    el.style.setProperty('--d', [...el.parentElement.children].indexOf(el) % 6);
  });

  // buttons: label rolls up on hover
  document.querySelectorAll('.btn, .pill').forEach(b => {
    const t = b.textContent.trim(); b.textContent = '';
    const r = document.createElement('span'); r.className = 'roll';
    r.innerHTML = '<span></span><span aria-hidden="true"></span>';
    r.children[0].textContent = t; r.children[1].textContent = t; b.append(r);
  });

  const items = document.querySelectorAll('.reveal, .fade');
  if ('IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in'); e.target.querySelectorAll('.fade').forEach(f => f.classList.add('in')); io.unobserve(e.target);
    }), { rootMargin: '0px 0px -10% 0px' });
    items.forEach(el => io.observe(el));
  } else items.forEach(el => el.classList.add('in'));

  // intro starts as soon as fonts are ready (never waits more than 600ms)
  const go = () => document.body.classList.add('ready');
  const fonts = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
  Promise.race([fonts, new Promise(r => setTimeout(r, 600))]).then(() => requestAnimationFrame(go));
  addEventListener('pageshow', e => { if (e.persisted) document.body.classList.remove('leaving'); });

  // short fade when leaving for another page on this site
  document.querySelectorAll('a[href]').forEach(a => a.addEventListener('click', e => {
    const u = new URL(a.href, location.href);
    if (reduce || u.origin !== location.origin || u.pathname === location.pathname || e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault(); document.body.classList.add('leaving'); setTimeout(() => { location.href = u.href; }, 380);
  }));

  // hero: text fades and lags behind the scroll (desktop only; on touch devices the
  // bounce and the collapsing address bar would make it jump, so it only fades there)
  const center = document.getElementById('center');
  if (center) {
    const fine = matchMedia('(pointer:fine)').matches;
    let vh = innerHeight, vw = innerWidth;
    addEventListener('resize', () => { if (innerWidth !== vw) { vw = innerWidth; vh = innerHeight; } });
    let queued = false;
    const apply = () => {
      queued = false;
      const s = cl(scrollY / vh);
      center.style.opacity = 1 - cl(s / .7);
      if (fine && !reduce) center.style.transform = `translate3d(0, calc(-54% + ${(s * vh * 0.35).toFixed(1)}px), 0)`;
      center.style.pointerEvents = s > .4 ? 'none' : '';
    };
    addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(apply); } }, { passive: true });
    apply();
  }

  // iOS edges: status-bar strip and page edge take the colour of what is at the top/bottom edge
  const strip = document.querySelector('.sb');
  if (strip) {
    const tone = el => !el ? '#c3bdb2' : el.closest('.dark, footer') ? '#2a241d' : el.closest('.light, main') ? '#efebe3' : '#c3bdb2';
    const at = y => document.elementsFromPoint(innerWidth / 2, y).find(el => !el.closest('.bar, .sb'));
    let queued = false;
    const paint = () => {
      queued = false;
      const top = parseFloat(getComputedStyle(strip).height) || 0;
      strip.style.background = tone(at(top + 1));
      const nearEnd = scrollY + innerHeight > document.documentElement.scrollHeight - innerHeight / 2;
      document.documentElement.style.background = tone(nearEnd ? document.querySelector('footer, main') : document.querySelector('.hero, main'));
    };
    addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(paint); } }, { passive: true });
    addEventListener('resize', paint); paint();
  }

  // consult form: one question at a time, sent to /api/consult
  const cf = document.getElementById('cf');
  if (cf) {
    const steps = [...cf.querySelectorAll('.cf-step')], order = ['room', 'timing', 'budget', 'plan', 'wish', 'contact'];
    const $ = id => document.getElementById(id);
    const next = $('cf-next'), back = $('cf-back'), msg = $('cf-msg');
    const data = { room: '', timing: '', budget: '', wish: '', name: '', email: '' };
    const KEY = 'naus-consult-draft';
    let i = 0, busy = false;
    try { Object.assign(data, JSON.parse(localStorage.getItem(KEY) || '{}')); } catch (e) {}
    const save = () => { try { localStorage.setItem(KEY, JSON.stringify(data)); } catch (e) {} };

    // choices: a dot appears and an underline is drawn under the picked one
    cf.querySelectorAll('.cf-choices').forEach(group => {
      const key = group.closest('.cf-step').dataset.step;
      const paint = () => group.querySelectorAll('button').forEach(b => b.setAttribute('aria-checked', String(b.dataset.v === data[key])));
      group.addEventListener('click', e => {
        const b = e.target.closest('button'); if (!b) return;
        data[key] = b.dataset.v; paint(); save(); msg.textContent = '';
      });
      paint();
    });

    // budget: rolling digits like the survey's amount readout
    const SCALE = [300, 500, 700, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4000], range = $('cf-range'), out = $('cf-amount'), und = $('cf-undecided');
    const label = n => n === SCALE.length - 1 ? '4,000万円以上' : SCALE[n].toLocaleString('en-US') + '万円';
    let shown = '';
    const roll = text => {
      if (!/\d/.test(text)) { out.innerHTML = '<span class="cf-dash">—</span>'; shown = ''; return; }
      const [num, unit] = [text.replace(/[^\d,]/g, ''), text.replace(/[\d,]/g, '')];
      if (!shown || shown.replace(/[^\d,]/g, '').length !== num.length) {
        out.innerHTML = [...num].map(ch => ch === ',' ? '<span class="cf-punct">,</span>' : '<span class="cf-digit"><span class="cf-strip">' + Array.from({ length: 10 }, (_, k) => '<span>' + k + '</span>').join('') + '</span></span>').join('') + '<span class="cf-unit">' + unit + '</span>';
        out.querySelectorAll('.cf-strip').forEach(s => { s.style.transition = 'none'; s.style.transform = 'translateY(0)'; void s.offsetHeight; s.style.transition = ''; });
      } else out.querySelector('.cf-unit').textContent = unit;
      const strips = out.querySelectorAll('.cf-strip'); let d = 0;
      [...num].forEach(ch => { if (ch !== ',') strips[d++].style.transform = 'translateY(' + (-1.05 * +ch) + 'em)'; });
      out.setAttribute('aria-label', text); shown = text;
    };
    const setBudget = n => {
      n = Math.max(0, Math.min(SCALE.length - 1, n)); range.value = n;
      range.style.setProperty('--fill', n / (SCALE.length - 1) * 100 + '%');
      data.budget = label(n); und.setAttribute('aria-pressed', 'false'); roll(data.budget); save(); msg.textContent = '';
    };
    range.addEventListener('input', () => setBudget(+range.value));
    range.addEventListener('pointerdown', () => { if (!data.budget || data.budget === 'まだ決めていない') setBudget(+range.value); });
    cf.querySelectorAll('.cf-nudge').forEach(b => b.addEventListener('click', () => setBudget((data.budget && data.budget !== 'まだ決めていない' ? +range.value : 0) + (data.budget && data.budget !== 'まだ決めていない' ? +b.dataset.d : 0))));
    und.addEventListener('click', () => { const on = data.budget !== 'まだ決めていない'; data.budget = on ? 'まだ決めていない' : ''; und.setAttribute('aria-pressed', String(on)); roll(''); range.style.setProperty('--fill', '0%'); save(); msg.textContent = ''; });
    if (data.budget && data.budget !== 'まだ決めていない') { const n = SCALE.findIndex((_, k) => label(k) === data.budget); if (n >= 0) setBudget(n); } else if (data.budget) und.setAttribute('aria-pressed', 'true');

    // floor plan: image is shrunk on the device (this also drops photo metadata), then tapped to place numbered pins
    const plan = { image: '', pins: [] }, MAXPINS = 8;
    const drop = $('pl-drop'), file = $('pl-file'), board = $('pl-board'), canvas = $('pl-canvas'), img = $('pl-img'), list = $('pl-list');
    const drawPins = () => {
      canvas.querySelectorAll('.pin').forEach(p => p.remove());
      list.innerHTML = '';
      plan.pins.forEach((p, k) => {
        const dot = document.createElement('span'); dot.className = 'pin'; dot.textContent = k + 1;
        dot.style.left = p.x * 100 + '%'; dot.style.top = p.y * 100 + '%'; canvas.append(dot);
        const li = document.createElement('li');
        li.innerHTML = '<b>' + (k + 1) + '</b><input maxlength="120" placeholder="例：ここにソファを置きたい"><button type="button" aria-label="印を消す">×</button>';
        const input = li.querySelector('input'); input.value = p.note;
        input.addEventListener('input', () => { p.note = input.value; });
        input.addEventListener('focus', () => dot.classList.add('on')); input.addEventListener('blur', () => dot.classList.remove('on'));
        li.querySelector('button').addEventListener('click', () => { plan.pins.splice(k, 1); drawPins(); });
        list.append(li);
      });
      $('pl-hint').textContent = plan.pins.length >= MAXPINS ? '印は' + MAXPINS + 'か所までです' : '図の上をタップして、気になる場所に印を付けてください';
    };
    const shrink = f => new Promise((ok, ng) => {
      const url = URL.createObjectURL(f), im = new Image();
      im.onload = () => {
        const s = Math.min(1, 1800 / Math.max(im.naturalWidth, im.naturalHeight)), c = document.createElement('canvas');
        c.width = Math.round(im.naturalWidth * s); c.height = Math.round(im.naturalHeight * s);
        const g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, c.width, c.height); g.drawImage(im, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url); ok(c.toDataURL('image/jpeg', .82));
      };
      im.onerror = () => { URL.revokeObjectURL(url); ng(new Error('この画像は読み込めませんでした')); };
      im.src = url;
    });
    const load = async f => {
      if (!f) return;
      if (!/^image\//.test(f.type)) { msg.textContent = '画像ファイルを選んでください'; return; }
      try {
        plan.image = await shrink(f); plan.pins = []; img.src = plan.image;
        drop.hidden = true; board.hidden = false; board.classList.remove('arrive'); void board.offsetWidth; board.classList.add('arrive');
        drawPins(); msg.textContent = '';
      } catch (x) { msg.textContent = x.message; }
    };
    file.addEventListener('change', () => load(file.files[0]));
    ['dragover', 'dragenter'].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.add('over'); }));
    ['dragleave', 'drop'].forEach(t => drop.addEventListener(t, () => drop.classList.remove('over')));
    drop.addEventListener('drop', e => { e.preventDefault(); load(e.dataTransfer.files[0]); });
    canvas.addEventListener('click', e => {
      if (e.target.closest('.pin') || plan.pins.length >= MAXPINS) return;
      const r = img.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      if (x < 0 || x > 1 || y < 0 || y > 1) return;
      plan.pins.push({ x: Math.round(x * 1000) / 1000, y: Math.round(y * 1000) / 1000, note: '' }); drawPins();
      const inputs = list.querySelectorAll('input'); inputs[inputs.length - 1].focus({ preventScroll: true });
    });
    $('pl-change').addEventListener('click', () => { file.value = ''; file.click(); });

    // text fields
    ['wish', 'name', 'email'].forEach(k => { const el = cf.elements[k]; el.value = data[k] || ''; el.addEventListener('input', () => { data[k] = el.value; save(); msg.textContent = ''; }); });

    const view = (n, dir) => {
      const from = steps.find(s => !s.hidden), to = cf.querySelector('[data-step="' + (order[n] || 'done') + '"]');
      const show = () => {
        if (from) { from.hidden = true; from.classList.remove('leave', 'back'); }
        to.hidden = false; to.classList.remove('arrive', 'back'); void to.offsetWidth; to.classList.add('arrive'); if (dir < 0) to.classList.add('back');
        i = n; const done = n >= order.length;
        $('cf-count').textContent = done ? 'DONE' : String(n + 1).padStart(2, '0') + ' / ' + String(order.length).padStart(2, '0');
        $('cf-bar').parentElement.style.setProperty('--p', done ? 1 : (n + 1) / order.length);
        $('cf-bar').style.setProperty('--p', done ? 1 : (n + 1) / order.length);
        back.hidden = n === 0 || done; next.hidden = done;
        next.textContent = n === order.length - 1 ? 'Send' : 'Next';
        busy = false;
      };
      if (from && from !== to && !reduce) { busy = true; from.classList.add('leave'); if (dir < 0) from.classList.add('back'); setTimeout(show, 200); } else show();
    };
    const check = () => {
      const k = order[i];
      if (k === 'room' && !data.room) return 'お部屋を選んでください';
      if (k === 'timing' && !data.timing) return '時期を選んでください';
      if (k === 'budget' && !data.budget) return 'スライダーで選ぶか、まだ決めていないを選んでください';
      if (k === 'contact') {
        if (!data.name.trim()) return 'お名前を入力してください';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email.trim())) return 'メールアドレスを確認してください';
      }
      return '';
    };
    back.addEventListener('click', () => { if (!busy) view(i - 1, -1); });
    cf.addEventListener('submit', async e => {
      e.preventDefault(); if (busy) return;
      const err = check(); if (err) { msg.textContent = err; return; }
      if (i < order.length - 1) { view(i + 1, 1); return; }
      busy = true; next.disabled = true; next.textContent = 'Sending'; msg.textContent = '';
      try {
        const r = await fetch('/api/consult', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ ...data, plan: plan.image, pins: plan.image ? plan.pins.map(p => ({ x: p.x, y: p.y, note: p.note.trim().slice(0, 120) })) : [], website: cf.elements.website.value }) });
        const j = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(j.error || '送信できませんでした、時間をおいてもう一度お試しください');
        try { localStorage.removeItem(KEY); } catch (e) {}
        next.disabled = false; busy = false; view(order.length, 1);
      } catch (x) { msg.textContent = x.message; next.disabled = false; next.textContent = 'Send'; busy = false; }
    });
    view(0, 1);
  }
})();
