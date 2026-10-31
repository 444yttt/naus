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
  document.querySelectorAll('.grid li, .steps li, .note, form, main > p, main > .st, dl > *').forEach(el => {
    el.classList.add('fade', 'reveal');
    el.style.setProperty('--d', [...el.parentElement.children].indexOf(el) % 6);
  });

  // buttons: label rolls up on hover
  document.querySelectorAll('.btn, .pill, button').forEach(b => {
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

  // hero: text lags behind the scroll and fades; header turns light over sand sections
  const center = document.getElementById('center'), bar = document.getElementById('bar');
  if (center) {
    const onScroll = () => {
      const s = scrollY / innerHeight;
      center.style.opacity = 1 - cl(s / .7);
      if (!reduce) center.style.transform = `translateY(calc(-54% + ${s * innerHeight * 0.35}px))`;
      center.style.pointerEvents = s > .4 ? 'none' : '';
    };
    addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }

  // header: transparent over the hero; hides while reading down, returns (frosted, in the
  // colour of the section underneath) when scrolling up
  const header = document.querySelector('.bar');
  if (header) {
    const zones = [...document.querySelectorAll('.light, .dark, .hero, main')];
    let last = scrollY;
    const update = () => {
      const y = scrollY, mid = header.getBoundingClientRect().height / 2;
      const z = zones.find(el => { const r = el.getBoundingClientRect(); return r.top <= mid && r.bottom > mid; });
      const zone = !z ? 'hero' : z.classList.contains('dark') ? 'dark' : (z.classList.contains('light') || z.tagName === 'MAIN') ? 'light' : 'hero';
      header.dataset.zone = zone; header.dataset.tone = zone === 'light' ? 'ink' : 'cream';
      header.classList.toggle('solid', y > 40);
      if (!reduce) {
        if (y > last + 6 && y > innerHeight * .5) header.classList.add('hide');
        else if (y < last - 6 || y < innerHeight * .5) header.classList.remove('hide');
      }
      last = y;
    };
    addEventListener('scroll', update, { passive: true }); addEventListener('resize', update); update();
  }

  // consult memo: local only, nothing is sent
  const f = document.getElementById('memo'), out = document.getElementById('out');
  if (f) f.addEventListener('submit', e => {
    e.preventDefault(); const d = new FormData(f);
    out.textContent = `【NAUS 相談メモ】\nお部屋：${d.get('room') || '未入力'}\nご予算の目安：${d.get('budget') || '未入力'}\nご要望：${d.get('wish') || '未入力'}`;
    out.hidden = false;
  });
})();
