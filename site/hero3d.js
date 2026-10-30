// Camera-projection "2.5D" room: the photo is projected onto a box that matches
// the room, so a slightly moving camera gives real parallax. Photo-camera = origin.
(() => {
  const cv = document.getElementById('stage');
  if (!cv) return;
  const gl = cv.getContext('webgl', { antialias: true, alpha: false });
  if (!gl) return;                                   // fallback: CSS photo behind
  const reduce = matchMedia('(prefers-reduced-motion:reduce)').matches;
  const F = 1445, CX = 750, CY = 1000, ZB = 7;       // focal (px @1500w), principal pt, back-wall depth (m)
  const px2x = p => (p - CX) * ZB / F, py2y = p => (CY - p) * ZB / F;
  const XL = px2x(214), XR = px2x(1290), YT = py2y(800), WX = 3.12, FY = -1.22, CYh = 1.18, ZN = .3, ZBAL = 9.3;

  const V = [];
  const quad = (L, a, b, c, d) => [a, b, c, a, c, d].forEach(p => V.push(p[0], p[1], p[2], L));
  quad(0, [-WX, FY, ZN], [WX, FY, ZN], [WX, FY, ZB], [-WX, FY, ZB]);                 // floor
  quad(0, [XL, FY, ZB], [XR, FY, ZB], [XR, FY, ZBAL], [XL, FY, ZBAL]);               // balcony floor
  quad(0, [-WX, CYh, ZN], [WX, CYh, ZN], [WX, CYh, ZB], [-WX, CYh, ZB]);             // ceiling
  quad(0, [XL, YT, ZB], [XR, YT, ZB], [XR, YT, ZBAL], [XL, YT, ZBAL]);               // balcony ceiling
  quad(0, [-WX, FY, ZN], [-WX, FY, ZB], [-WX, CYh, ZB], [-WX, CYh, ZN]);             // left wall
  quad(0, [WX, FY, ZN], [WX, FY, ZB], [WX, CYh, ZB], [WX, CYh, ZN]);                 // right wall
  quad(0, [XL, FY, ZB], [XL, FY, ZBAL], [XL, YT, ZBAL], [XL, YT, ZB]);               // balcony side L
  quad(0, [XR, FY, ZB], [XR, FY, ZBAL], [XR, YT, ZBAL], [XR, YT, ZB]);               // balcony side R
  quad(0, [-WX, FY, ZB], [XL, FY, ZB], [XL, CYh, ZB], [-WX, CYh, ZB]);               // back wall L
  quad(0, [XR, FY, ZB], [WX, FY, ZB], [WX, CYh, ZB], [XR, CYh, ZB]);                 // back wall R
  quad(0, [XL, YT, ZB], [XR, YT, ZB], [XR, CYh, ZB], [XL, CYh, ZB]);                 // back wall top
  quad(1, [-40, -14, 30], [40, -14, 30], [40, 14, 30], [-40, 14, 30]);               // far plane (trees, sky)
  [[394, 22], [634, 14], [866, 14], [1102, 24]].forEach(([c, hw]) => {                // mullions
    const a = px2x(c - hw), b = px2x(c + hw);
    quad(2, [a, FY, ZB], [b, FY, ZB], [b, YT, ZB], [a, YT, ZB]);
  });

  const vs = `attribute vec4 a;uniform vec3 uC,uR,uU,uF;uniform vec4 uP;uniform vec2 uFN;varying vec3 vW;varying float vL;
  void main(){vec3 d=a.xyz-uC;vec3 v=vec3(dot(d,uR),dot(d,uU),dot(d,uF));vW=a.xyz;vL=a.w;
  float z=max(v.z,.01);float nx=(uP.x*v.x/z-uP.z)/(uP.x*0.0+uP.y*.5);
  gl_Position=vec4(nx*z,((uP.x*v.y/z)-uP.w)/(uFN.y*.5)*z,(v.z*(uFN.x+.05)-2.*uFN.x*.05)/(uFN.x-.05),z);}`;
  // nx uses uP.y as width px; ny uses uFN.y as height px
  const fs = `precision mediump float;uniform sampler2D t0,t1;uniform float uF2;varying vec3 vW;varying float vL;
  void main(){float z=vW.z;float px=750.+uF2*vW.x/z,py=1000.-uF2*vW.y/z;vec2 uv=clamp(vec2(px/1500.,py/2000.),0.002,.998);
  vec4 c=texture2D(t0,uv);if(vL>.5&&vL<1.5)c=texture2D(t1,uv);
  if(vL>1.5){float l=dot(c.rgb,vec3(.3,.59,.11));float al=1.-smoothstep(.16,.34,l);if(al<.02)discard;c.rgb*=1.;}
  gl_FragColor=vec4(c.rgb,1.);}`;
  const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw gl.getShaderInfoLog(o); return o; };
  const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(pr); gl.useProgram(pr);
  const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(V), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(pr, 'a'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 4, gl.FLOAT, false, 16, 0);
  const U = n => gl.getUniformLocation(pr, n);
  const uC = U('uC'), uR = U('uR'), uU = U('uU'), uF = U('uF'), uP = U('uP'), uFN = U('uFN');
  gl.uniform1f(U('uF2'), F); gl.uniform1i(U('t0'), 0); gl.uniform1i(U('t1'), 1);
  gl.enable(gl.DEPTH_TEST);

  let ready = 0;
  const load = (src, unit) => { const im = new Image(); im.onload = () => {
    const t = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, t);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, im);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    if (++ready === 2) { cv.classList.add('on'); }
  }; im.src = src; };
  load('img/room.jpg', 0); load('img/room-bg.jpg', 1);

  let W, H, dpr;
  const resize = () => { dpr = Math.min(devicePixelRatio || 1, 2); W = innerWidth; H = innerHeight; cv.width = W * dpr; cv.height = H * dpr; gl.viewport(0, 0, cv.width, cv.height); };
  addEventListener('resize', resize); resize();

  let tx = 0, ty = 0, mx = 0, my = 0, scrollP = 0;
  addEventListener('pointermove', e => { tx = e.clientX / W * 2 - 1; ty = e.clientY / H * 2 - 1; });
  const onScroll = () => { scrollP = Math.max(0, Math.min(1, scrollY / innerHeight)); };
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  window.__cam = null;

  const norm = v => { const l = Math.hypot(...v); return v.map(x => x / l); };
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const draw = ms => {
    const t = ms / 1000, A = W / H;
    let ax = tx, ay = ty;
    if (!matchMedia('(pointer:fine)').matches) { ax = Math.sin(t * .25) * .8; ay = Math.sin(t * .19) * .5; }
    if (reduce) { ax = 0; ay = 0; }
    mx += (ax - mx) * .04; my += (ay - my) * .04;
    let cx = mx * .24, cy = -my * .10, cz = scrollP * .6;
    if (window.__cam) [cx, cy, cz] = window.__cam;
    const c = [cx, cy, cz], f = norm([0 - cx, 0 - cy, ZB - cz]);
    const r = norm(cross([0, 1, 0], f)), u = cross(f, r);
    // visible window in photo-pixel space (cover, with margin for parallax)
    let h = A >= .75 ? 1500 / 1.14 / A : 2000 / 1.1, w = h * A;
    const ccx = CX, ccy = A >= .75 ? 800 : 1010;
    gl.uniform3fv(uC, c); gl.uniform3fv(uR, r); gl.uniform3fv(uU, u); gl.uniform3fv(uF, f);
    gl.uniform4f(uP, F, w, ccx - CX, CY - ccy); gl.uniform2f(uFN, 60, h);
    gl.clearColor(.16, .14, .11, 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    if (ready === 2) gl.drawArrays(gl.TRIANGLES, 0, V.length / 4);
    if (!document.hidden) requestAnimationFrame(draw);
  };
  document.addEventListener('visibilitychange', () => { if (!document.hidden) requestAnimationFrame(draw); });
  requestAnimationFrame(draw);
})();
