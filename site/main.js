(() => {
  const reduce = matchMedia('(prefers-reduced-motion:reduce)').matches;
  const cl = x => Math.max(0, Math.min(1, x));

  // split marked headings into characters (keeps inline elements such as the kerning span)
  document.querySelectorAll('[data-split]').forEach(el => {
    const nodes = [...el.childNodes]; el.textContent = ''; let i = 0;
    nodes.forEach(n => {
      if (n.nodeType === 3) [...n.textContent].forEach(c => { const s = document.createElement('span'); s.className = 'ch'; s.textContent = c; s.style.setProperty('--i', i++); s.setAttribute('aria-hidden', 'true'); el.append(s); });
      else { n.classList.add('ch'); n.style.setProperty('--i', i++); n.setAttribute('aria-hidden', 'true'); el.append(n); }
    });
  });

  // reveal on scroll, staggered within each parent
  const targets = document.querySelectorAll('h2, .grid li, .steps li, .note, form, main > p, main > .st, dl > *');
  targets.forEach(el => { el.classList.add('reveal'); el.style.setProperty('--d', [...el.parentElement.children].indexOf(el) % 6); });
  if ('IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -12% 0px' });
    targets.forEach(el => io.observe(el));
  } else targets.forEach(el => el.classList.add('in'));

  // page in: wait for fonts so the letters don't jump
  const ready = () => document.body.classList.add('ready');
  (document.fonts && document.fonts.ready ? Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 1200))]) : Promise.resolve()).then(() => requestAnimationFrame(ready));
  addEventListener('pageshow', e => { if (e.persisted) { document.body.classList.remove('leaving'); ready(); } });

  // page out: fade before following links to other pages
  document.querySelectorAll('a[href]').forEach(a => a.addEventListener('click', e => {
    const u = new URL(a.href, location.href);
    if (reduce || u.origin !== location.origin || (u.pathname === location.pathname && u.hash) || e.metaKey || e.ctrlKey) return;
    e.preventDefault(); document.body.classList.add('leaving'); setTimeout(() => { location.href = u.href; }, 320);
  }));

  // hero: fade and drift up while scrolling away
  const center = document.getElementById('center'), bar = document.getElementById('bar');
  if (center) {
    const onScroll = () => {
      const s = scrollY / innerHeight;
      center.style.opacity = 1 - cl(s / .6);
      center.style.transform = reduce ? '' : `translateY(calc(-54% - ${s * 90}px))`;
      center.style.pointerEvents = s > .4 ? 'none' : '';
      if (bar) bar.classList.toggle('on-light', s > .92);
    };
    addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }

  // consult memo: local only, nothing is sent
  const f = document.getElementById('memo'), out = document.getElementById('out');
  if (f) f.addEventListener('submit', e => {
    e.preventDefault(); const d = new FormData(f);
    out.textContent = `【NAUS 相談メモ】\nお部屋：${d.get('room') || '未入力'}\nご予算の目安：${d.get('budget') || '未入力'}\nご要望：${d.get('wish') || '未入力'}`;
    out.hidden = false;
  });
})();
