(() => {
  const photo = document.getElementById('photo'), center = document.getElementById('center'), bar = document.getElementById('bar');
  const reduce = matchMedia('(prefers-reduced-motion:reduce)').matches;
  const cl = x => Math.max(0, Math.min(1, x));
  const onScroll = () => {
    const s = scrollY / innerHeight;
    center.style.opacity = 1 - cl(s / .6);
    center.style.pointerEvents = s > .4 ? 'none' : '';
    bar.classList.toggle('on-light', s > .92);
    if (!reduce) photo.style.setProperty('--zoom', 1.04 + cl(s) * .06);
  };
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  if (!reduce && matchMedia('(pointer:fine)').matches) {
    addEventListener('pointermove', e => {
      photo.style.setProperty('--px', ((e.clientX / innerWidth - .5) * -18) + 'px');
      photo.style.setProperty('--py', ((e.clientY / innerHeight - .5) * -12) + 'px');
    });
  }
  const f = document.getElementById('memo'), out = document.getElementById('out');
  f.addEventListener('submit', e => {
    e.preventDefault(); const d = new FormData(f);
    out.textContent = `【NAUS 相談メモ】\nお部屋：${d.get('room') || '未入力'}\nご予算の目安：${d.get('budget') || '未入力'}\nご要望：${d.get('wish') || '未入力'}`;
    out.hidden = false;
  });
})();
