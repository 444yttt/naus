import * as THREE from 'three';
import { buildRoom, ROOM } from './room-model.js';

const cv = document.getElementById('stage');
const reduce = matchMedia('(prefers-reduced-motion:reduce)').matches;
let renderer;
try { renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true, alpha: false, powerPreference: 'high-performance' }); } catch (e) { renderer = null; }
if (renderer) {
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.15;
  const scene = new THREE.Scene(); scene.background = new THREE.Color(0xcfe8fb);
  scene.add(buildRoom());

  // lighting: cool daylight from the window, warm cove light, soft fill
  scene.add(new THREE.HemisphereLight(0xf2f3ea, 0xb09a80, 1.5));
  const sun = new THREE.DirectionalLight(0xfff3e0, .9); sun.position.set(1.5, 3, -30); scene.add(sun);

  // glossy-floor environment: a bright window and a warm ceiling
  const env = new THREE.Scene(); env.background = new THREE.Color(0x15110d);
  const box = (w, h, d, c, x, y, z) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshBasicMaterial({ color: c })); m.position.set(x, y, z); env.add(m); };
  box(10, 3, .2, 0xffffff, 0, 0, -9); box(12, .2, 9, 0xff9a50, 0, 1.6, -3);
  const pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(env, .04).texture; scene.environmentIntensity = .9;

  // exterior: a pre-rendered image of the view (railing and mullions removed), hung far outside the window
  const tr = new THREE.TextureLoader().load('img/trees.jpg'); tr.colorSpace = THREE.SRGBColorSpace;
  const D = 45, pxH = 420;   // crop height in photo px (1500-wide space)
  const view = new THREE.Mesh(new THREE.PlaneGeometry(((804 + 520) / 1445) * D, (pxH / 1445) * D), new THREE.MeshBasicMaterial({ map: tr, toneMapped: false }));
  view.position.set(((356 + 1160) / 2 - 750) * D / 1445, (1000 - (850 + 1270) / 2) * D / 1445, -D); scene.add(view);
  const skyBox = new THREE.Mesh(new THREE.PlaneGeometry(400, 200), new THREE.MeshBasicMaterial({ color: 0xcfe8fb, toneMapped: false })); skyBox.position.set(0, 20, -D - 1); scene.add(skyBox);

  const cam = new THREE.PerspectiveCamera(32, 1, .05, 200); cam.position.set(0, 0, 0);
  const resize = () => { const w = innerWidth, h = innerHeight; renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2)); renderer.setSize(w, h, false);
    const A = w / h; cam.aspect = A; cam.fov = A >= .75 ? 2 * Math.atan((1500 / 1.14 / A / 2) / 1445) * 180 / Math.PI : 2 * Math.atan((2000 / 1.1 / 2) / 1445) * 180 / Math.PI; cam.updateProjectionMatrix(); };
  addEventListener('resize', resize); resize();

  let tx = 0, ty = 0, mx = 0, my = 0, sp = 0;
  addEventListener('pointermove', e => { tx = e.clientX / innerWidth * 2 - 1; ty = e.clientY / innerHeight * 2 - 1; });
  addEventListener('scroll', () => { sp = Math.max(0, Math.min(1, scrollY / innerHeight)); }, { passive: true });
  window.__cam = null;
  const fine = matchMedia('(pointer:fine)').matches;
  const draw = ms => {
    const t = ms / 1000, A = innerWidth / innerHeight;
    let ax = tx, ay = ty; if (!fine) { ax = Math.sin(t * .25) * .8; ay = Math.sin(t * .19) * .5; } if (reduce) { ax = 0; ay = 0; }
    mx += (ax - mx) * .04; my += (ay - my) * .04;
    let cx = mx * .24, cy = -my * .10, cz = -sp * .6; if (window.__cam) [cx, cy, cz] = window.__cam;
    cam.position.set(cx, cy, cz);
    cam.lookAt(0, A >= .75 ? .97 : 0, ROOM.WALLZ);
    renderer.render(scene, cam);
    if (!document.hidden) requestAnimationFrame(draw);
  };
  document.addEventListener('visibilitychange', () => { if (!document.hidden) requestAnimationFrame(draw); });
  cv.classList.add('on'); requestAnimationFrame(draw);
}
