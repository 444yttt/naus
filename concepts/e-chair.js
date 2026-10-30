(() => {
  const cv = document.getElementById('stage'), ctx = cv.getContext('2d');
  const reduce = matchMedia('(prefers-reduced-motion:reduce)').matches;
  const small = innerWidth < 700;
  let seed = 7; const rnd = () => (seed = seed * 16807 % 2147483647) / 2147483647;

  // chair = tilted/straight boxes, sampled on the surface with normals
  // [cx,cy,cz, w,h,d, tiltX]
  const parts = [
    [0, .55, 0, 2.0, .38, 1.9, 0],      // seat
    [0, 1.45, -.95, 2.0, 1.55, .32, -.2], // back
    [-1.08, .95, 0, .22, .5, 1.8, 0],   // arm L
    [1.08, .95, 0, .22, .5, 1.8, 0],    // arm R
    [-.85, .18, -.75, .12, .36, .12, 0], [.85, .18, -.75, .12, .36, .12, 0],
    [-.85, .18, .75, .12, .36, .12, 0], [.85, .18, .75, .12, .36, .12, 0],
  ];
  const N = small ? 9000 : 18000, P = [];
  const vol = parts.map(p => p[3] * p[4] * p[5] ** 0 + 0); // weights by surface area
  const area = parts.map(p => 2 * (p[3] * p[4] + p[4] * p[5] + p[3] * p[5]));
  const tot = area.reduce((a, b) => a + b);
  parts.forEach((p, i) => {
    const n = Math.round(N * area[i] / tot);
    for (let k = 0; k < n; k++) {
      const ax = Math.floor(rnd() * 3), sg = rnd() < .5 ? -1 : 1;
      const d = [p[3], p[4], p[5]];
      let v = [(rnd() - .5) * d[0], (rnd() - .5) * d[1], (rnd() - .5) * d[2]];
      const nm = [0, 0, 0]; v[ax] = sg * d[ax] / 2; nm[ax] = sg;
      const t = p[6], c = Math.cos(t), s = Math.sin(t);
      const rot = a => [a[0], a[1] * c - a[2] * s, a[1] * s + a[2] * c];
      v = rot(v); const n2 = rot(nm);
      P.push({ x: v[0] + p[0], y: v[1] + p[1], z: v[2] + p[2], nx: n2[0], ny: n2[1], nz: n2[2],
        ph: rnd() * 6.28, sx: (rnd() - .5) * 2, sy: (rnd() - .2) * 2, sz: (rnd() - .5) * 2 });
    }
  });

  let W, H, dpr, mx = 0, my = 0, tmx = 0, tmy = 0, prog = 0;
  const resize = () => {
    dpr = Math.min(devicePixelRatio || 1, 2); W = innerWidth; H = innerHeight;
    cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  addEventListener('resize', resize); resize();
  addEventListener('pointermove', e => { tmx = e.clientX / W * 2 - 1; tmy = e.clientY / H * 2 - 1; });
  const onScroll = () => { prog = Math.min(1, scrollY / (H * .9)); };
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  let visible = true;
  document.addEventListener('visibilitychange', () => { visible = !document.hidden; if (visible) requestAnimationFrame(frame); });

  const B = 10, buckets = Array.from({ length: B }, () => []);
  function frame(ms) {
    if (!visible) return;
    const t = reduce ? 0 : ms / 1000;
    mx += (tmx - mx) * .05; my += (tmy - my) * .05;
    ctx.clearRect(0, 0, W, H);
    if (prog >= 1) { if (!reduce) requestAnimationFrame(frame); return; }
    const S = Math.min(W / 5.4, H / 3.4) * (small ? 1.25 : 1) * .75;
    const a = .6 + t * .18 + mx * .5, ca = Math.cos(a), sa = Math.sin(a);
    const tilt = -.32 + my * .12, ct = Math.cos(tilt), st = Math.sin(tilt);
    const lx = mx * .8 + .3, ly = -my * .6 - .5, lz = .7;
    const cx = W / 2, cy = H / 2 + S * .1 - prog * H * .1, ease = prog * prog;
    buckets.forEach(b => b.length = 0);
    for (const p of P) {
      const j = Math.sin(t * .9 + p.ph) * .012; // each dot drifts on its own
      let x = p.x + j + p.sx * ease * 3, y = p.y - 1 + j + p.sy * ease * 3, z = p.z + j * .5 + p.sz * ease * 3;
      let X = x * ca - z * sa, Z = x * sa + z * ca;
      const Y = y * ct - Z * st, Z2 = y * st + Z * ct;
      let nX = p.nx * ca - p.nz * sa, nZ = p.nx * sa + p.nz * ca;
      const nY = p.ny * ct - nZ * st, nZ2 = p.ny * st + nZ * ct;
      const lit = Math.max(0, nX * lx - nY * ly + nZ2 * lz) / 1.2;
      const depth = (Z2 + 3) / 6;
      const v = Math.max(.06, Math.min(1, .12 + lit * .75 + depth * .15)) * (1 - ease);
      const bi = Math.min(B - 1, (v * B) | 0);
      buckets[bi].push(cx + X * S, cy - Y * S, .6 + depth * (small ? .7 : 1));
    }
    for (let i = 0; i < B; i++) {
      const b = buckets[i]; if (!b.length) continue;
      ctx.fillStyle = `rgba(46,38,30,${(i + 1) / B * .85})`; ctx.beginPath();
      for (let k = 0; k < b.length; k += 3) { ctx.moveTo(b[k] + b[k + 2], b[k + 1]); ctx.arc(b[k], b[k + 1], b[k + 2], 0, 6.283); }
      ctx.fill();
    }
    if (!reduce) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  if (reduce) addEventListener('scroll', () => requestAnimationFrame(frame), { passive: true });

  })();