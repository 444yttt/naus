// Living room 3D model (metres). Origin = eye position, -z = into the room, floor y = -1.22.
// Dimensions are estimated from photos (room ~6.2 w x 7 d x 2.4 h, window wall 5.2 w).
import * as THREE from 'three';

const FY = -1.22, CEIL = 1.18, COFFER = 1.33, WALLZ = -7, HW = 3.12, OX = 2.62, WTOP = .97, BALZ = -9.3;

const canvasTex = (w, h, draw, rep, srgb = true) => {
  const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; if (rep) t.repeat.set(...rep);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
};
let seed = 11; const rnd = () => (seed = seed * 16807 % 2147483647) / 2147483647;

const woodTex = () => canvasTex(1024, 1024, (g, w, h) => {
  const rows = 8, rh = h / rows;
  for (let r = 0; r < rows; r++) {
    const joint = rnd() * w, cuts = [0, joint, w].sort((a, b) => a - b);
    for (let k = 0; k < 2; k++) {
      const x0 = cuts[k], x1 = cuts[k + 1], l = 17 + rnd() * 6;
      g.fillStyle = `hsl(${18 + rnd() * 6},${28 + rnd() * 8}%,${l}%)`; g.fillRect(x0, r * rh, x1 - x0, rh);
      for (let i = 0; i < 26; i++) { g.strokeStyle = `rgba(${rnd() < .5 ? '10,5,3' : '90,60,45'},${.05 + rnd() * .1})`; g.lineWidth = .6 + rnd() * 1.4;
        const y = r * rh + rnd() * rh; g.beginPath(); g.moveTo(x0, y); g.bezierCurveTo(x0 + (x1 - x0) * .3, y + rnd() * 4 - 2, x0 + (x1 - x0) * .7, y + rnd() * 4 - 2, x1, y + rnd() * 3 - 1.5); g.stroke(); }
    }
    g.fillStyle = 'rgba(0,0,0,.55)'; g.fillRect(0, r * rh, w, 2); g.fillRect(joint, r * rh, 2, rh);
  }
}, [6.24 / 2.4, 7 / 1.6]);
const graniteTex = () => canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#8c8984'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 9000; i++) { const v = 80 + rnd() * 120 | 0; g.fillStyle = `rgba(${v},${v - 2},${v - 6},${.25 + rnd() * .4})`; g.fillRect(rnd() * w, rnd() * h, 1 + rnd() * 2.2, 1 + rnd() * 2.2); }
  g.strokeStyle = 'rgba(30,30,30,.5)'; g.lineWidth = 2; g.strokeRect(0, 0, w, h);
}, [1, 1]);
const tileTex = () => canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#7d8082'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 4000; i++) { const v = 100 + rnd() * 50 | 0; g.fillStyle = `rgba(${v},${v + 2},${v + 4},.18)`; g.fillRect(rnd() * w, rnd() * h, 2, 2); }
  g.strokeStyle = '#4b4d4f'; g.lineWidth = 4; g.strokeRect(0, 0, w, h);
}, [2.62 * 2 / .6, 2.3 / .6]);
const wallTex = () => canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#e6dcc8'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 14000; i++) { const v = rnd() * 40 - 20; g.fillStyle = `rgba(${v > 0 ? 255 : 90},${v > 0 ? 250 : 80},${v > 0 ? 235 : 60},${Math.abs(v) / 400})`; g.fillRect(rnd() * w, rnd() * h, 1, 1 + rnd() * 6); }
}, [3, 1.2]);
const coveTex = () => canvasTex(512, 512, (g, w, h) => {  // warm wash, brightest along the four edges of the coffer
  g.fillStyle = '#4a3220'; g.fillRect(0, 0, w, h);
  const e = (x0, y0, x1, y1, rx, ry, rw, rh) => { const gr = g.createLinearGradient(x0, y0, x1, y1); gr.addColorStop(0, 'rgba(255,170,80,.95)'); gr.addColorStop(1, 'rgba(255,170,80,0)'); g.fillStyle = gr; g.fillRect(rx, ry, rw, rh); };
  e(0, 0, 150, 0, 0, 0, 150, h); e(w, 0, w - 150, 0, w - 150, 0, 150, h); e(0, 0, 0, 150, 0, 0, w, 150); e(0, h, 0, h - 150, 0, h - 150, w, 150);
}, null);
const canopyTex = () => canvasTex(1024, 1024, (g, w, h) => {
  g.fillStyle = '#4d7a22'; g.fillRect(0, 0, w, h);
  const greens = ['#a8cf4e', '#8fbd3f', '#79a935', '#6a9a2c', '#bfdc66', '#5b8a26'];
  for (let i = 0; i < 5200; i++) { const x = rnd() * w, y = rnd() * h, r = 4 + rnd() * 20;
    g.fillStyle = 'rgba(25,45,10,.35)'; g.beginPath(); g.arc(x + r * .25, y + r * .35, r, 0, 7); g.fill();
    g.fillStyle = greens[(rnd() * greens.length) | 0]; g.beginPath(); g.arc(x, y, r * .92, 0, 7); g.fill(); }
}, [10, 10]);
export { canopyTex };

export function buildRoom() {
  const root = new THREE.Group(); root.name = 'ChidorigafuchiLiving';
  const add = (m, name) => { m.name = name || m.name; root.add(m); return m; };
  const mesh = (geo, mat, x, y, z, name) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); if (name) m.name = name; root.add(m); return m; };
  const plane = (w, h, mat, pos, rot, name) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat); m.position.set(...pos); m.rotation.set(...rot); m.name = name; root.add(m); return m; };

  const M = {
    floor: new THREE.MeshStandardMaterial({ map: woodTex(), color: 0x6e5f58, roughness: .32, metalness: 0, name: 'WalnutFloor' }),
    wall: new THREE.MeshStandardMaterial({ map: wallTex(), roughness: .92, name: 'Wall' }),
    ceil: new THREE.MeshStandardMaterial({ color: 0xf0e4cf, emissive: 0x5a3a1c, emissiveIntensity: .35, roughness: .95, name: 'Ceiling' }),
    cove: new THREE.MeshStandardMaterial({ color: 0x1a0f06, emissive: 0xffffff, emissiveMap: coveTex(), emissiveIntensity: 1.6, roughness: 1, name: 'CoveGlow' }),
    coveEdge: new THREE.MeshStandardMaterial({ color: 0x20120a, emissive: 0xff8a30, emissiveIntensity: .75, roughness: 1, name: 'CoveEdge' }),
    frame: new THREE.MeshStandardMaterial({ color: 0x151517, metalness: .55, roughness: .38, name: 'AluminiumFrame' }),
    granite: new THREE.MeshStandardMaterial({ map: graniteTex(), roughness: .6, name: 'Granite' }),
    tile: new THREE.MeshStandardMaterial({ map: tileTex(), roughness: .7, name: 'BalconyTile' }),
    soffit: new THREE.MeshStandardMaterial({ color: 0x8a8c88, roughness: .9, name: 'BalconySoffit' }),
    steel: new THREE.MeshStandardMaterial({ color: 0xb9bcc0, metalness: .9, roughness: .3, name: 'Steel' }),
    glass: new THREE.MeshPhysicalMaterial({ color: 0xcfe3df, transparent: true, opacity: .12, roughness: .05, metalness: 0, side: THREE.DoubleSide, name: 'Glass' }),
    light: new THREE.MeshBasicMaterial({ color: 0xffe2b0, name: 'Downlight' }),
    ac: new THREE.MeshStandardMaterial({ color: 0xe9e6df, roughness: .5, name: 'AirCon' }),
    vent: new THREE.MeshStandardMaterial({ color: 0x3b3b3c, roughness: .6, name: 'Vent' }),
  };

  // floor / ceiling
  plane(HW * 2, 7, M.floor, [0, FY, -3.5], [-Math.PI / 2, 0, 0], 'Floor');
  // ceiling = soffit ring around the raised coffer (so the coffer is open to view)
  plane(HW - 1.8, 7, M.ceil, [-(HW + 1.8) / 2, CEIL, -3.5], [Math.PI / 2, 0, 0], 'SoffitL');
  plane(HW - 1.8, 7, M.ceil, [(HW + 1.8) / 2, CEIL, -3.5], [Math.PI / 2, 0, 0], 'SoffitR');
  plane(3.6, 2.3, M.ceil, [0, CEIL, -5.85], [Math.PI / 2, 0, 0], 'SoffitBack');
  // raised coffer (x +-1.8, from behind the camera to z=-4.7) with glowing cove
  const cw = 3.6, cd = 8.7, cz = -4.7 + cd / 2;
  plane(cw, cd, M.cove, [0, COFFER, cz], [Math.PI / 2, 0, 0], 'CofferCeiling');
  mesh(new THREE.BoxGeometry(.04, COFFER - CEIL, cd), M.coveEdge, -1.8, (CEIL + COFFER) / 2, cz, 'CoffStepL');
  mesh(new THREE.BoxGeometry(.04, COFFER - CEIL, cd), M.coveEdge, 1.8, (CEIL + COFFER) / 2, cz, 'CoffStepR');
  mesh(new THREE.BoxGeometry(cw, COFFER - CEIL, .04), M.coveEdge, 0, (CEIL + COFFER) / 2, -4.7, 'CoffStepBack');

  // walls: side walls, back wall with window opening
  plane(7, CEIL - FY, M.wall, [-HW, (CEIL + FY) / 2, -3.5], [0, Math.PI / 2, 0], 'WallLeft');
  plane(7, CEIL - FY, M.wall, [HW, (CEIL + FY) / 2, -3.5], [0, -Math.PI / 2, 0], 'WallRight');
  plane(HW - OX, CEIL - FY, M.wall, [-(HW + OX) / 2, (CEIL + FY) / 2, WALLZ], [0, 0, 0], 'BackWallL');
  plane(HW - OX, CEIL - FY, M.wall, [(HW + OX) / 2, (CEIL + FY) / 2, WALLZ], [0, 0, 0], 'BackWallR');
  plane(OX * 2, CEIL - WTOP, M.wall, [0, (CEIL + WTOP) / 2, WALLZ], [0, 0, 0], 'BackWallTop');

  // window wall: frames + mullions
  const bx = (w, h, d, x, y, z, n) => mesh(new THREE.BoxGeometry(w, h, d), M.frame, x, y, z, n);
  const H = WTOP - FY;
  [-1.72, -.56, .56, 1.7].forEach((x, i) => bx(.075, H, .1, x, FY + H / 2, WALLZ, 'Mullion' + i));
  [-OX, OX].forEach((x, i) => bx(.1, H, .14, x, FY + H / 2, WALLZ, 'FrameSide' + i));
  bx(OX * 2, .1, .14, 0, WTOP, WALLZ, 'FrameTop'); bx(OX * 2, .04, .14, 0, FY + .02, WALLZ, 'FrameSill');
  plane(OX * 2, H, M.glass, [0, FY + H / 2, WALLZ + .02], [0, 0, 0], 'WindowGlass');

  // balcony
  plane(OX * 2, 2.3, M.tile, [0, FY + .01, (WALLZ + BALZ) / 2], [-Math.PI / 2, 0, 0], 'BalconyFloor');
  plane(OX * 2, 2.3, M.soffit, [0, WTOP, (WALLZ + BALZ) / 2], [Math.PI / 2, 0, 0], 'BalconySoffit');
  plane(2.3, WTOP - FY, M.granite, [-OX, (WTOP + FY) / 2, (WALLZ + BALZ) / 2], [0, Math.PI / 2, 0], 'BalconySideL');
  plane(2.3, WTOP - FY, M.granite, [OX, (WTOP + FY) / 2, (WALLZ + BALZ) / 2], [0, -Math.PI / 2, 0], 'BalconySideR');
  // railing: glass panels, posts, top rail
  const RH = 1.0, rz = BALZ;
  for (let i = 0; i <= 4; i++) mesh(new THREE.BoxGeometry(.05, RH, .05), M.steel, -OX + i * OX * .5, FY + RH / 2, rz, 'RailPost' + i);
  mesh(new THREE.CylinderGeometry(.025, .025, OX * 2, 12), M.steel, 0, FY + RH, rz, 'RailTop').rotation.z = Math.PI / 2;
  plane(OX * 2, RH - .1, M.glass, [0, FY + RH / 2 - .02, rz], [0, 0, 0], 'RailGlass');
  mesh(new THREE.BoxGeometry(OX * 2, .08, .2), M.steel, 0, FY + .04, rz, 'RailBase');

  // ceiling details (downlights, air-conditioner cassette from the photos)
  [[-1.58, -5.5], [.02, -5.5], [1.64, -5.5], [-2.7, -3.1], [2.7, -3.1]].forEach(([x, z], i) => {
    const m = mesh(new THREE.CircleGeometry(.05, 24), M.light, x, CEIL - .005, z, 'Downlight' + i); m.rotation.x = Math.PI / 2;
  });
  mesh(new THREE.BoxGeometry(.5, .16, 1.15), M.ac, -2.25, CEIL - .08, -1.8, 'AirCon');
  mesh(new THREE.BoxGeometry(.36, .02, .95), M.vent, -2.25, CEIL - .165, -1.8, 'AirConVent');
  return root;
}

export const ROOM = { FY, CEIL, COFFER, WALLZ, HW, OX, WTOP, BALZ };
