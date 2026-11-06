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
    const steps = [...cf.querySelectorAll('.cf-step')], order = ['room', 'timing', 'budget', 'plan', 'taste', 'story', 'contact'];
    const $ = id => document.getElementById(id);
    const next = $('cf-next'), back = $('cf-back'), msg = $('cf-msg');
    const data = { room: '', timing: '', budget: '', materials: [], styles: [], concerns: [], links: '', wish: '', name: '', email: '' };
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

    // floor plan: image is shrunk on the device (this also drops photo metadata), then tapped to place numbered pins.
    // Known sample sheets pause on a scan, then mark those rooms on the drawing. planRooms on submit is label + size only.
    // poly is the room outline as fractions of that sheet; at is the label. The two crops do not share a poly.
    const room = (label, size, at, poly) => ({ label, size, at, poly });
    const sheet = (src, name, rooms) => ({ src, name, rooms });
    const SAMPLES = {
      'harajuku-3ldk': sheet('/media/plans/harajuku-3ldk.jpg', '原宿 3LDK', [
        room('Living Dining', '約30.3帖', [.22, .64], [[.128, .432], [.118, .5], [.1, .56], [.088, .64], [.068, .72], [.048, .8], [.036, .855], [.44, .855], [.44, .555], [.38, .555], [.38, .488], [.348, .488], [.348, .432]]),
        room('Kitchen', '約12.6帖', [.24, .3], [[.182, .18], [.296, .18], [.296, .32], [.348, .32], [.348, .432], [.128, .432], [.14, .37], [.155, .3], [.168, .23]]),
        room('Bedroom 1（WICあり）', '約11.5帖', [.844, .72], [[.736, .555], [.958, .555], [.958, .855], [.736, .855]]),
        room('Bedroom 2', '約8.7帖', [.518, .72], [[.448, .555], [.588, .555], [.588, .855], [.448, .855]]),
        room('Bedroom 3', '約7.5帖', [.662, .72], [[.598, .555], [.726, .555], [.726, .855], [.598, .855]])
      ]),
      'harajuku-3ldk-tight': sheet('/media/plans/harajuku-3ldk-tight.jpg', '原宿 3LDK（別図）', [
        room('Living Dining', '約30.3帖', [.22, .60], [[.148, .448], [.12, .53], [.092, .6], [.064, .67], [.036, .745], [.418, .745], [.418, .558], [.36, .558], [.36, .505], [.328, .505], [.328, .448]]),
        room('Kitchen', '約12.6帖', [.245, .34], [[.18, .222], [.302, .222], [.302, .33], [.33, .33], [.33, .448], [.148, .448], [.158, .38], [.168, .3]]),
        room('Bedroom 1（WICあり）', '約11.5帖', [.816, .655], [[.706, .558], [.94, .558], [.94, .745], [.706, .745]]),
        room('Bedroom 2', '約8.7帖', [.493, .655], [[.42, .558], [.56, .558], [.56, .745], [.42, .745]]),
        room('Bedroom 3', '約7.5帖', [.633, .655], [[.572, .558], [.694, .558], [.694, .745], [.572, .745]])
      ])
    };
    const plan = { image: '', pins: [], sample: '', rooms: null }, MAXPINS = 8, MAXROOMS = 12, READ_MS = 2500;
    const drop = $('pl-drop'), file = $('pl-file'), pick = $('pl-pick'), board = $('pl-board'), canvas = $('pl-canvas'), img = $('pl-img'), list = $('pl-list');
    const roomsEl = $('pl-rooms'), roomList = $('pl-room-list'), roomAdd = $('pl-room-add'), readEl = $('pl-read'), scanEl = $('pl-scan'), hint = $('pl-hint');
    let planToken = 0, readTimer = 0, reading = false, onRoom = -1;
    const copyRoom = r => ({ label: r.label, size: r.size, at: r.at ? r.at.slice() : null, poly: r.poly ? r.poly.map(p => p.slice()) : null });
    const setOn = (k) => {
      onRoom = k;
      roomList.querySelectorAll('li').forEach(li => li.classList.toggle('on', li.dataset.i === String(k)));
      canvas.querySelectorAll('.pl-mark, .pl-tag').forEach(m => m.classList.toggle('on', m.dataset.i === String(k)));
    };
    const clearMarks = () => canvas.querySelectorAll('.pl-mark, .pl-tag, svg.pl-map').forEach(m => m.remove());
    const paintMark = (m, r) => {
      m.querySelector('b').textContent = r.label.trim() || '部屋';
      m.querySelector('small').textContent = r.size.trim();
      m.setAttribute('aria-label', (r.label.trim() || '部屋') + (r.size.trim() ? ' ' + r.size.trim() : ''));
    };
    const bindMark = (el, k) => {
      const pick = () => {
        const input = roomList.querySelector('li[data-i="' + k + '"] .pl-room-name');
        if (input) input.focus({ preventScroll: true });
        setOn(k);
      };
      el.addEventListener('click', e => { e.stopPropagation(); pick(); });
      el.addEventListener('mouseenter', () => setOn(k));
      el.addEventListener('mouseleave', () => { if (onRoom === k && !roomList.querySelector('li[data-i="' + k + '"] input:focus')) setOn(-1); });
    };
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
      hint.hidden = reading;
      if (!reading) hint.textContent = plan.pins.length >= MAXPINS ? '印は' + MAXPINS + 'か所までです' : '図の上をタップして、気になる場所に印を付けてください';
    };
    const drawMarks = (animate) => {
      clearMarks();
      if (!plan.sample || !Array.isArray(plan.rooms)) return;
      const ns = 'http://www.w3.org/2000/svg';
      const svg = document.createElementNS(ns, 'svg');
      svg.classList.add('pl-map');
      svg.setAttribute('viewBox', '0 0 1 1');
      svg.setAttribute('preserveAspectRatio', 'none');
      svg.setAttribute('aria-hidden', 'true');
      canvas.append(svg);
      plan.rooms.forEach((r, k) => {
        if (!r.poly || r.poly.length < 3) return;
        const m = document.createElementNS(ns, 'polygon');
        m.setAttribute('points', r.poly.map(p => p[0] + ',' + p[1]).join(' '));
        m.classList.add('pl-mark'); m.dataset.i = String(k);
        const midY = r.poly.reduce((s, p) => s + p[1], 0) / r.poly.length;
        if (animate && !reduce) {
          m.style.setProperty('--d', (0.28 + midY * 1.25).toFixed(2) + 's');
          m.classList.add('in');
        }
        bindMark(m, k);
        svg.append(m);
        const tag = document.createElement('button');
        tag.type = 'button'; tag.className = 'pl-tag'; tag.dataset.i = String(k);
        const at = r.at || [r.poly.reduce((s, p) => s + p[0], 0) / r.poly.length, midY];
        tag.style.left = at[0] * 100 + '%'; tag.style.top = at[1] * 100 + '%';
        tag.innerHTML = '<b></b><small></small>';
        paintMark(tag, r);
        if (animate && !reduce) {
          tag.style.setProperty('--d', (0.28 + midY * 1.25).toFixed(2) + 's');
          tag.classList.add('in');
        }
        bindMark(tag, k);
        canvas.append(tag);
      });
      if (onRoom >= 0) setOn(onRoom);
    };
    const drawRooms = () => {
      roomList.innerHTML = '';
      if (!plan.sample || !Array.isArray(plan.rooms)) { roomsEl.hidden = true; board.classList.remove('has-rooms'); clearMarks(); return; }
      const first = roomsEl.hidden;
      roomsEl.hidden = false; board.classList.add('has-rooms');
      if (first) {
        roomsEl.classList.remove('arrive'); void roomsEl.offsetWidth; roomsEl.classList.add('arrive');
        roomsEl.scrollIntoView({ block: 'nearest', behavior: reduce ? 'auto' : 'smooth' });
      }
      plan.rooms.forEach((r, k) => {
        const li = document.createElement('li'); li.dataset.i = String(k);
        li.innerHTML = '<input class="pl-room-name" maxlength="80" aria-label="部屋の名前" placeholder="部屋の名前" autocomplete="off"><input class="pl-room-size" maxlength="24" aria-label="広さ" placeholder="広さ" autocomplete="off"><button type="button" aria-label="この部屋を消す">×</button>';
        const name = li.querySelector('.pl-room-name'), size = li.querySelector('.pl-room-size');
        name.value = r.label; size.value = r.size;
        const sync = () => { r.label = name.value; r.size = size.value; const tag = canvas.querySelector('.pl-tag[data-i="' + k + '"]'); if (tag) paintMark(tag, r); };
        name.addEventListener('input', sync); size.addEventListener('input', sync);
        li.addEventListener('focusin', () => setOn(k));
        li.addEventListener('focusout', () => setTimeout(() => { if (!document.activeElement || !document.activeElement.closest('#pl-room-list li')) setOn(-1); }, 0));
        li.addEventListener('mouseenter', () => setOn(k));
        li.addEventListener('mouseleave', () => { if (onRoom === k && !li.contains(document.activeElement)) setOn(-1); });
        li.querySelector('button').addEventListener('click', () => { plan.rooms.splice(k, 1); if (onRoom === k) onRoom = -1; drawRooms(); drawMarks(false); });
        roomList.append(li);
      });
      roomAdd.hidden = plan.rooms.length >= MAXROOMS;
      if (onRoom >= 0) setOn(onRoom);
    };
    const shrink = (f, max = 1800) => new Promise((ok, ng) => {
      const url = URL.createObjectURL(f), im = new Image();
      im.onload = () => {
        const s = Math.min(1, max / Math.max(im.naturalWidth, im.naturalHeight)), c = document.createElement('canvas');
        c.width = Math.round(im.naturalWidth * s); c.height = Math.round(im.naturalHeight * s);
        const g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, c.width, c.height); g.drawImage(im, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url); ok(c.toDataURL('image/jpeg', .82));
      };
      im.onerror = () => { URL.revokeObjectURL(url); ng(new Error('この画像は読み込めませんでした')); };
      im.src = url;
    });
    const stopRead = () => { clearTimeout(readTimer); reading = false; readEl.hidden = true; scanEl.hidden = true; canvas.classList.remove('reading'); };
    const resetPlan = () => {
      planToken++; stopRead(); onRoom = -1; clearMarks();
      plan.image = ''; plan.pins = []; plan.sample = ''; plan.rooms = null;
      file.value = ''; img.removeAttribute('src'); img.alt = '間取り図';
      roomsEl.hidden = true; board.classList.remove('has-rooms'); canvas.classList.remove('ready'); board.hidden = true; pick.hidden = false;
      drawPins();
    };
    const openBoard = (withRead) => {
      clearMarks(); onRoom = -1;
      pick.hidden = true; board.hidden = false; roomsEl.hidden = true; board.classList.remove('has-rooms', 'arrive');
      canvas.classList.remove('ready');
      void board.offsetWidth; board.classList.add('arrive');
      if (!withRead) { stopRead(); drawPins(); return; }
      reading = true; readEl.hidden = false; canvas.classList.add('reading'); drawPins(); drawMarks(true);
      if (!reduce) { scanEl.hidden = false; scanEl.style.animation = 'none'; void scanEl.offsetWidth; scanEl.style.animation = ''; }
      const token = planToken;
      readTimer = setTimeout(() => {
        if (token !== planToken) return;
        reading = false; readEl.hidden = true; scanEl.hidden = true; canvas.classList.remove('reading'); canvas.classList.add('ready');
        drawPins(); drawRooms();
      }, reduce ? 480 : READ_MS);
    };
    const load = async f => {
      if (!f) return;
      if (!/^image\//.test(f.type)) { msg.textContent = '画像ファイルを選んでください'; return; }
      const token = ++planToken; stopRead();
      try {
        const jpeg = await shrink(f);
        if (token !== planToken) return;
        plan.image = jpeg; plan.pins = []; plan.sample = ''; plan.rooms = null;
        img.alt = 'アップロードした間取り図'; img.src = jpeg;
        openBoard(false); msg.textContent = '';
      } catch (x) { if (token === planToken) msg.textContent = x.message; }
    };
    const useSample = async (id) => {
      const sample = SAMPLES[id]; if (!sample) return;
      const token = ++planToken; stopRead(); msg.textContent = '';
      const btn = pick.querySelector('[data-sample="' + id + '"]'); if (btn) btn.setAttribute('aria-busy', 'true');
      try {
        const res = await fetch(sample.src);
        if (!res.ok) throw new Error('図面を開けませんでした');
        const jpeg = await shrink(new File([await res.blob()], 'plan.jpg', { type: 'image/jpeg' }));
        if (token !== planToken) return;
        plan.sample = id; plan.rooms = sample.rooms.map(copyRoom); plan.pins = []; plan.image = jpeg;
        img.alt = sample.name + 'の間取り図'; img.src = jpeg;
        openBoard(true);
      } catch (x) {
        if (token !== planToken) return;
        resetPlan(); msg.textContent = x.message || '図面を開けませんでした';
      } finally { if (btn) btn.removeAttribute('aria-busy'); }
    };
    file.addEventListener('change', () => load(file.files[0]));
    ['dragover', 'dragenter'].forEach(t => drop.addEventListener(t, e => { e.preventDefault(); drop.classList.add('over'); }));
    ['dragleave', 'drop'].forEach(t => drop.addEventListener(t, () => drop.classList.remove('over')));
    drop.addEventListener('drop', e => { e.preventDefault(); load(e.dataTransfer.files[0]); });
    pick.querySelectorAll('.pl-sample').forEach(b => b.addEventListener('click', () => useSample(b.dataset.sample)));
    canvas.addEventListener('click', e => {
      if (reading || e.target.closest('.pin') || e.target.closest('.pl-mark') || e.target.closest('.pl-tag') || plan.pins.length >= MAXPINS) return;
      const r = img.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      if (x < 0 || x > 1 || y < 0 || y > 1) return;
      plan.pins.push({ x: Math.round(x * 1000) / 1000, y: Math.round(y * 1000) / 1000, note: '' }); drawPins();
      const inputs = list.querySelectorAll('input'); inputs[inputs.length - 1].focus({ preventScroll: true });
    });
    roomAdd.addEventListener('click', () => {
      if (!Array.isArray(plan.rooms) || plan.rooms.length >= MAXROOMS) return;
      plan.rooms.push({ label: '', size: '', poly: null, at: null }); drawRooms(); drawMarks(false);
      const inputs = roomList.querySelectorAll('.pl-room-name'); inputs[inputs.length - 1].focus({ preventScroll: true });
    });
    $('pl-change').addEventListener('click', () => { resetPlan(); msg.textContent = ''; });

    // text fields
    // taste and concerns: tap to toggle (swatch tiles and word chips)
    cf.querySelectorAll('.sw-grid, .chips').forEach(group => {
      const key = group.dataset.key; if (!Array.isArray(data[key])) data[key] = [];
      const paint = () => group.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(data[key].includes(b.dataset.v))));
      group.addEventListener('click', e => {
        const b = e.target.closest('button'); if (!b) return;
        const v = b.dataset.v; data[key] = data[key].includes(v) ? data[key].filter(x => x !== v) : [...data[key], v];
        paint(); save();
      });
      paint();
    });

    // reference photos: up to 3, shrunk on the device like the floor plan
    const refs = [], MAXREFS = 3, refBox = $('refs'), refAdd = $('ref-add'), refFile = $('ref-file');
    const drawRefs = () => {
      refBox.querySelectorAll('.ref').forEach(r => r.remove());
      refs.forEach((src, k) => {
        const d = document.createElement('div'); d.className = 'ref';
        d.innerHTML = '<img alt="参考写真"><button type="button" aria-label="写真を外す">×</button>';
        d.querySelector('img').src = src;
        d.querySelector('button').addEventListener('click', () => { refs.splice(k, 1); drawRefs(); });
        refBox.insertBefore(d, refAdd);
      });
      refAdd.hidden = refs.length >= MAXREFS;
    };
    refFile.addEventListener('change', async () => {
      for (const f of [...refFile.files].slice(0, MAXREFS - refs.length)) {
        if (!/^image\//.test(f.type)) continue;
        try { refs.push(await shrink(f, 1400)); } catch (x) { msg.textContent = x.message; }
      }
      refFile.value = ''; drawRefs();
    });

    ['links', 'wish', 'name', 'email'].forEach(k => { const el = cf.elements[k]; el.value = data[k] || ''; el.addEventListener('input', () => { data[k] = el.value; save(); msg.textContent = ''; }); });

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
        const body = { ...data, refs, plan: plan.image, pins: plan.image ? plan.pins.map(p => ({ x: p.x, y: p.y, note: p.note.trim().slice(0, 120) })) : [], website: cf.elements.website.value };
        if (plan.sample && Array.isArray(plan.rooms)) body.planRooms = plan.rooms.map(r => ({ label: r.label.trim().slice(0, 80), size: r.size.trim().slice(0, 24) })).filter(r => r.label || r.size);
        const r = await fetch('/api/consult', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
        const j = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(j.error || '送信できませんでした、時間をおいてもう一度お試しください');
        try { localStorage.removeItem(KEY); } catch (e) {}
        next.disabled = false; busy = false; view(order.length, 1);
      } catch (x) { msg.textContent = x.message; next.disabled = false; next.textContent = 'Send'; busy = false; }
    });
    view(0, 1);
  }
})();
