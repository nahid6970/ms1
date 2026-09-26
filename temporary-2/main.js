import * as THREE from 'three';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.164.1/examples/jsm/controls/OrbitControls.js';

const host = document.querySelector('#scene');
const scene = new THREE.Scene();
scene.background = null;

const camera = new THREE.PerspectiveCamera(33, 1, 0.1, 100);
camera.position.set(7.2, 5.5, 10.5);
camera.lookAt(0, 3.25, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.16;
host.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 3.2, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.055;
controls.minDistance = 7;
controls.maxDistance = 18;
controls.maxPolarAngle = Math.PI * 0.48;

scene.add(new THREE.HemisphereLight(0xdce3c4, 0x303b2d, 2.0));
const key = new THREE.DirectionalLight(0xffe8c4, 4.1);
key.position.set(-5, 10, 7);
key.castShadow = true;
key.shadow.mapSize.set(1024, 1024);
key.shadow.bias = -0.0003;
scene.add(key);
const rim = new THREE.DirectionalLight(0xc9dba2, 2.0);
rim.position.set(5, 6, -5);
scene.add(rim);

const bark = new THREE.MeshStandardMaterial({ color: 0x795943, roughness: 0.94 });
const oldBark = new THREE.MeshStandardMaterial({ color: 0xa48a68, roughness: 0.92 });
const potMat = new THREE.MeshStandardMaterial({ color: 0x738078, roughness: 0.56, metalness: 0.05 });
const soilMat = new THREE.MeshStandardMaterial({ color: 0x302b22, roughness: 1 });
const stoneMat = new THREE.MeshStandardMaterial({ color: 0x757969, roughness: 1 });
const groundMat = new THREE.MeshStandardMaterial({ color: 0x1c281e, roughness: 1 });
const bonsai = new THREE.Group();
scene.add(bonsai);

function branch(start, end, radius, material = bark, endRadius = radius * 0.5) {
  const a = new THREE.Vector3(...start), b = new THREE.Vector3(...end);
  const delta = b.clone().sub(a);
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(endRadius, radius, delta.length(), 8), material);
  mesh.position.copy(a).add(b).multiplyScalar(0.5);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), delta.normalize());
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  bonsai.add(mesh);
  return mesh;
}

// Tapered, softly bending trunk with exposed, sculptural root flares.
const trunk = [
  [[0, 0.48, 0], [-0.38, 0.92, 0.04], 0.31],
  [[-0.38, 0.92, 0.04], [-0.67, 1.48, 0.1], 0.245],
  [[-0.67, 1.48, 0.1], [-0.62, 2.05, 0.11], 0.185],
  [[-0.62, 2.05, 0.11], [-0.13, 2.55, 0.12], 0.145],
  [[-0.13, 2.55, 0.12], [0.45, 2.89, 0.13], 0.11],
  [[0.45, 2.89, 0.13], [0.78, 3.38, 0.12], 0.083],
  [[0.78, 3.38, 0.12], [0.66, 3.91, 0.06], 0.054],
  [[0.66, 3.91, 0.06], [0.93, 4.31, 0.02], 0.035],
];
trunk.forEach((part, i) => branch(part[0], part[1], part[2], i % 3 === 1 ? oldBark : bark, part[2] * 0.78));
const roots = [
  [[-0.15, 0.55, 0], [-0.77, 0.48, 0.38], 0.13], [[-0.16, 0.54, 0.02], [-0.63, 0.47, -0.49], 0.12],
  [[-0.05, 0.52, 0], [0.57, 0.46, 0.36], 0.13], [[-0.08, 0.52, 0], [0.48, 0.46, -0.47], 0.115],
  [[-0.25, 0.55, 0.04], [-0.35, 0.46, 0.59], 0.09], [[-0.24, 0.55, 0.05], [-0.44, 0.46, -0.56], 0.09],
];
roots.forEach(r => branch(r[0], r[1], r[2], oldBark, r[2] * 0.25));

// Layered, asymmetrical branches lead the eye through the classic windswept silhouette.
const limbs = [
  [[-0.65, 1.58, 0.1], [-1.42, 2.05, 0.07], 0.13], [[-1.42, 2.05, 0.07], [-2.3, 2.19, 0], 0.075], [[-2.3, 2.19, 0], [-2.95, 2.48, -0.06], 0.038],
  [[-1.56, 2.09, 0.07], [-1.86, 2.62, 0.05], 0.055], [[-0.58, 1.75, 0.1], [-1.06, 1.97, 0.62], 0.07], [[-1.06, 1.97, 0.62], [-1.65, 2.04, 0.85], 0.038],
  [[-0.39, 2.3, 0.1], [0.1, 1.98, 0.14], 0.105], [[0.1, 1.98, 0.14], [0.85, 1.89, 0.08], 0.065], [[0.85, 1.89, 0.08], [1.44, 2.13, 0.02], 0.036],
  [[0.38, 1.95, 0.1], [0.55, 1.54, 0.48], 0.048], [[-0.14, 2.51, 0.1], [-0.7, 2.87, 0.05], 0.095], [[-0.7, 2.87, 0.05], [-1.28, 3.08, 0.02], 0.06],
  [[-1.28, 3.08, 0.02], [-1.86, 3.21, -0.07], 0.032], [[-0.74, 2.89, 0.05], [-1.13, 3.36, -0.03], 0.045], [[0.13, 2.66, 0.12], [0.67, 2.53, 0.38], 0.078],
  [[0.67, 2.53, 0.38], [1.3, 2.72, 0.49], 0.043], [[1.3, 2.72, 0.49], [1.77, 2.95, 0.45], 0.025], [[0.52, 2.59, 0.32], [0.62, 3.02, 0.56], 0.045],
  [[0.51, 2.94, 0.12], [-0.05, 3.25, 0.06], 0.068], [[-0.05, 3.25, 0.06], [-0.57, 3.43, 0.09], 0.04], [[0.7, 3.38, 0.12], [1.16, 3.28, -0.03], 0.047],
  [[1.16, 3.28, -0.03], [1.53, 3.48, -0.05], 0.026], [[0.7, 3.47, 0.12], [0.19, 3.72, 0.05], 0.043], [[0.19, 3.72, 0.05], [-0.17, 3.96, 0], 0.024],
  [[0.78, 3.93, 0.07], [1.2, 4.09, 0.03], 0.025],
];
limbs.forEach((l, i) => branch(l[0], l[1], l[2], i % 5 === 0 ? oldBark : bark, l[2] * 0.58));

// Fine twigs use a muted warm bark so they remain visible among the needles.
const twigTips = [
  [-2.9,2.47,-.06],[-2.45,2.18,.04],[-1.87,2.61,.05],[-1.72,2.06,.84],[-1.8,3.2,-.07],[-1.08,3.37,-.03],[-.56,3.43,.09],[-.18,3.97,0],[1.76,2.94,.45],[1.46,2.15,.02],[.57,1.53,.49],[1.5,3.47,-.05],[1.18,4.09,.03],[.95,4.35,.02]
];
const twigRoots = [
  [-2.55,2.2,0],[-2.08,2.18,.02],[-1.7,2.24,.03],[-1.22,2.08,.06],[-1.28,2.77,.05],[-.93,3.01,.05],[-1.32,3.19,.01],[-.93,3.29,.02],[-.37,3.11,.07],[.03,3.19,.08],[-.42,3.74,.03],[-.08,3.83,.02],[.65,3.12,.1],[.92,3.29,.02],[1.39,3.33,-.04],[.99,3.5,0],[1.04,2.65,.45],[1.45,2.82,.46],[.75,2.27,.25],[1.05,1.92,.06],[1.3,2.03,.03],[-1.43,1.97,.45],[-1.5,2.35,.36],[.3,2.94,.23]
];
twigRoots.forEach((p, i) => {
  const t = twigTips[i % twigTips.length];
  const spread = (i % 3 - 1) * 0.22;
  const end = [t[0] + spread, t[1] + (i % 2 ? 0.12 : -0.07), t[2] + (i % 2 ? 0.1 : -0.1)];
  branch(p, end, 0.025, i % 3 === 0 ? oldBark : bark, 0.008);
});

// Small hand-shaped pads of soft needled foliage, instanced for a light, responsive scene.
const foliage = new THREE.Group();
bonsai.add(foliage);
const padMat = [0x526441, 0x65734d, 0x77815a, 0x43583e, 0x818765, 0x586b48].map(color => new THREE.MeshStandardMaterial({ color, roughness: 0.89 }));
const padGeometry = new THREE.IcosahedronGeometry(1, 2);
let seed = 13;
function random() { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; }
const clusters = [
  [-2.45,2.42,.01,.96],[-2.04,2.12,.04,.76],[-1.63,2.73,.04,.82],[-1.95,2.27,.74,.7],[-1.45,2.02,.84,.65],
  [-1.25,3.44,-.03,.72],[-1.65,3.22,-.04,.75],[-1.27,3.02,.01,.79],[-.82,3.54,.02,.7],[-.58,3.72,.02,.78],[-.16,4.02,-.01,.59],[-.26,3.37,.04,.78],[-.48,3.15,.08,.7],
  [.4,3.83,.03,.76],[.84,4.07,.03,.65],[1.38,4.2,.02,.56],[1.28,3.6,-.04,.8],[1.62,3.58,-.05,.7],[.9,3.43,-.01,.77],
  [1.53,3.04,.45,.65],[1.05,2.86,.47,.77],[.7,2.8,.43,.82],[.2,3.02,.17,.68],[.98,2.03,.05,.71],[1.42,2.24,.03,.7],[.45,1.79,.36,.76],[.83,2.14,.28,.64],[-1.05,2.18,.38,.58],[-1.57,2.18,.65,.6]
];
const padCount = 290;
const foliageMeshes = padMat.map(mat => { const m = new THREE.InstancedMesh(padGeometry, mat, padCount); m.castShadow = true; m.receiveShadow = true; foliage.add(m); return m; });
const temp = new THREE.Object3D();
const counts = new Array(foliageMeshes.length).fill(0);
for (let i = 0; i < padCount; i++) {
  const cluster = clusters[Math.floor(random() * clusters.length)];
  const [cx, cy, cz, width] = cluster;
  const angle = random() * Math.PI * 2, radial = Math.sqrt(random());
  const scale = width * (0.15 + random() * 0.19);
  temp.position.set(cx + Math.cos(angle) * radial * width * 0.84, cy + Math.sin(angle) * radial * width * 0.37, cz + (random() - 0.5) * width * 0.88);
  temp.rotation.set((random() - .5) * .55, random() * Math.PI, (random() - .5) * .55);
  temp.scale.set(scale * (1.15 + random() * .7), scale * (.52 + random() * .34), scale * (.8 + random() * .58));
  temp.updateMatrix();
  const index = Math.floor(random() * foliageMeshes.length), local = counts[index]++;
  foliageMeshes[index].setMatrixAt(local, temp.matrix);
}
foliageMeshes.forEach((mesh, i) => { mesh.count = counts[i]; mesh.instanceMatrix.needsUpdate = true; });

// The shallow, hand-thrown rectangular pot has softly rounded-looking bevels and a rolled lip.
function box(w, h, d, material, x, y, z, bevel = 0) {
  const geometry = bevel ? new THREE.BoxGeometry(w, h, d, 1, 1, 1) : new THREE.BoxGeometry(w, h, d);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(x, y, z);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  bonsai.add(mesh);
  return mesh;
}
box(3.55,.55,2.28,potMat,0,.02,0);
box(3.68,.11,2.4,potMat,0,.29,0);
box(3.24,.10,1.97,soilMat,0,.36,0);
box(3.35,.12,2.08,oldBark,0,-.29,0);
for (const x of [-1.32, 1.32]) box(.42,.12,.2,potMat,x,-.37,.83);
for (let i = 0; i < 20; i++) {
  const pebble = new THREE.Mesh(new THREE.DodecahedronGeometry(.055 + random() * .055, 0), i % 3 === 0 ? stoneMat : soilMat);
  pebble.position.set((random() - .5) * 2.85,.44,(random() - .5) * 1.55);
  pebble.scale.set(1.4,.52,.9);
  pebble.castShadow = true;
  bonsai.add(pebble);
}

const floor = new THREE.Mesh(new THREE.CircleGeometry(200, 64), groundMat);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -.47;
floor.receiveShadow = true;
scene.add(floor);
const shadowDisc = new THREE.Mesh(new THREE.CircleGeometry(2.4, 64), new THREE.MeshBasicMaterial({ color: 0x0b100d, transparent: true, opacity: .34 }));
shadowDisc.rotation.x = -Math.PI / 2;
shadowDisc.position.y = -.455;
shadowDisc.scale.set(1.3, .78, 1);
scene.add(shadowDisc);

function resize() {
  const width = host.clientWidth, height = host.clientHeight;
  if (!width || !height) return;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height, false);
}
new ResizeObserver(resize).observe(host);
resize();

document.querySelector('#reset-view').addEventListener('click', () => {
  controls.reset();
  camera.position.set(7.2, 5.5, 10.5);
  controls.target.set(0, 3.2, 0);
  controls.update();
});

const clock = new THREE.Clock();
function render() {
  requestAnimationFrame(render);
  const t = clock.getElapsedTime();
  foliage.rotation.z = Math.sin(t * .7) * .004;
  controls.update();
  renderer.render(scene, camera);
}
render();
