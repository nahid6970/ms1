import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { ADDITION, SUBTRACTION, INTERSECTION, Evaluator, Brush } from 'three-bvh-csg';
window.__formaStarted = true;

const $ = (s) => document.querySelector(s);
const viewport = $('#viewport');
const scene = new THREE.Scene(); scene.background = new THREE.Color(0xeef0f4);
const camera = new THREE.PerspectiveCamera(45, 1, .1, 1000); camera.position.set(7, 5.5, 8);
const renderer = new THREE.WebGLRenderer({ antialias:true, preserveDrawingBuffer:true });
renderer.setPixelRatio(Math.min(devicePixelRatio,2)); renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap;
viewport.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping=true; controls.target.set(0,1,0);
const transform = new TransformControls(camera, renderer.domElement);
scene.add(transform);
let gizmoPointerDown=false;
transform.addEventListener('dragging-changed', e => controls.enabled=!e.value);
transform.addEventListener('mouseDown', () => { gizmoPointerDown=true; });
transform.addEventListener('mouseUp', () => { gizmoPointerDown=false; });
transform.addEventListener('objectChange', syncInspector);
transform.addEventListener('objectChange', () => { if(tool==='cut') updateCutPlanes(); });

scene.add(new THREE.HemisphereLight(0xffffff,0x9ea7b5,2.2));
const key=new THREE.DirectionalLight(0xffffff,3); key.position.set(5,9,4); key.castShadow=true; scene.add(key);
const grid = new THREE.GridHelper(20,20,0xc7cad3,0xdfe1e7); grid.position.y=-.01; scene.add(grid);
const ground = new THREE.Mesh(new THREE.PlaneGeometry(20,20),new THREE.ShadowMaterial({opacity:.09}));
ground.rotation.x=-Math.PI/2; ground.receiveShadow=true; scene.add(ground);

let selected=null, selected2=null, tool='select', idCounter=1, clipboard=null;
const objects=[];
const colors=['#6f6cff','#ff7b58','#55b5a1','#e8ad58','#d975aa'];
const geometryFor = type => ({box:new THREE.BoxGeometry(1.5,1.5,1.5),sphere:new THREE.SphereGeometry(1,32,20),cylinder:new THREE.CylinderGeometry(.8,.8,1.7,32),torus:new THREE.TorusGeometry(.75,.28,16,40)})[type];

function addObject(type='box', data={}) {
  const material=new THREE.MeshStandardMaterial({color:data.color||colors[(objects.length)%colors.length],metalness:data.metalness??.2,roughness:data.roughness??.4});
  const geometry=data.geometry ? new THREE.BufferGeometryLoader().parse(data.geometry) : geometryFor(type);
  if(!geometry) throw new Error(`Unsupported object geometry: ${type}`);
  const mesh=new THREE.Mesh(geometry,material);
  mesh.name=data.name||`${type[0].toUpperCase()+type.slice(1)} ${idCounter++}`;
  mesh.castShadow=true; mesh.receiveShadow=true; mesh.userData.type=type;
  mesh.position.set(...(data.position||[0,type==='box'?0.75:1,0]));
  if(data.rotation) mesh.rotation.set(...data.rotation.map(v=>THREE.MathUtils.degToRad(v)));
  if(data.scale) mesh.scale.set(...data.scale);
  scene.add(mesh); objects.push(mesh); select(mesh); updateScene(); return mesh;
}

function select(obj, additive=false) {
  if(additive && selected && obj && obj!==selected){selected2=obj;}
  else{selected=obj; selected2=null;}
  transform.detach();
  if(selected && tool!=='select' && tool!=='cut') transform.attach(selected);
  syncInspector(); updateScene(); updateBoolUI();
  if(tool==='cut' && selected){ initCutPanel(); transform.setMode(cutGizmoMode); transform.attach(cutFrame); }
}

function updateBoolUI() {
  const two=selected&&selected2;
  ['bool-subtract','bool-union','bool-intersect'].forEach(id=>{const b=document.getElementById(id);if(b)b.disabled=!two;});
  const hint=document.getElementById('bool-hint');
  if(hint) hint.textContent=two?`A = ${selected.name}  ·  B = ${selected2.name}`:'Select 2 objects (Shift+click B)';
}

function setTool(next) {
  tool=next;
  document.querySelectorAll('.tool-card').forEach(b=>b.classList.toggle('active',b.dataset.tool===next));
  if(next==='cut'){
    transform.detach();
    if(selected){ initCutPanel(); transform.setMode(cutGizmoMode); transform.attach(cutFrame); } else toast('Select an object first');
  } else {
    hideCutPlane();
    document.getElementById('cut-context').classList.add('hidden');
    if(selected&&next!=='select'){transform.setMode(next==='translate'?'translate':next==='rotate'?'rotate':'scale');transform.attach(selected);}
    else transform.detach();
  }
}

function syncInspector() {
  const has=!!selected;
  $('#empty-inspector').classList.toggle('hidden',has);
  $('#inspector-content').classList.toggle('hidden',!has);
  $('#selection-label').textContent=has?'OBJECT':'NONE SELECTED';
  if(!has) return;
  $('#object-name').value=selected.name;
  $('#selected-shape').style.background=selected.material.color.getStyle();
  const vals={position:{x:selected.position.x,y:selected.position.y,z:selected.position.z},rotation:{x:THREE.MathUtils.radToDeg(selected.rotation.x),y:THREE.MathUtils.radToDeg(selected.rotation.y),z:THREE.MathUtils.radToDeg(selected.rotation.z)},scale:{x:selected.scale.x,y:selected.scale.y,z:selected.scale.z}};
  document.querySelectorAll('[data-transform]').forEach(input=>{const [a,b]=input.dataset.transform.split('.');input.value=Number(vals[a][b].toFixed(2));});
  $('#object-color').value='#'+selected.material.color.getHexString();
  $('#color-value').textContent=$('#object-color').value.toUpperCase();
  $('#object-metalness').value=selected.material.metalness;
  $('#metalness-value').textContent=selected.material.metalness.toFixed(2);
  $('#object-roughness').value=selected.material.roughness;
  $('#roughness-value').textContent=selected.material.roughness.toFixed(2);
}

function updateScene() {
  const tree=$('#scene-tree');
  tree.innerHTML=objects.length?'':`<div class="tree-empty">Your scene is empty</div>`;
  objects.forEach(o=>{
    const row=document.createElement('button');
    const isSel=o===selected||o===selected2;
    row.className=`tree-row ${isSel?'selected':''}`;
    if(o===selected2) row.style.opacity='0.7';
    row.innerHTML=`<span class="tree-icon"></span><span class="tree-name">${o.name}</span><span class="tree-type">${o.userData.type}</span>`;
    row.onclick=(e)=>select(o,e.shiftKey); tree.appendChild(row);
  });
  $('#object-count').textContent=`${objects.length} object${objects.length===1?'':'s'}`;
  $('#viewport-empty').style.display=objects.length?'none':'flex';
}

function removeSelected() {
  if(!selected) return;
  scene.remove(selected); selected.geometry.dispose(); selected.material.dispose();
  objects.splice(objects.indexOf(selected),1); select(objects.at(-1)||null); toast('Object deleted');
}

function serialize() {
  return {version:1,name:$('#project-name').value,objects:objects.map(o=>({name:o.name,type:o.userData.type,geometry:['sliced','boolean'].includes(o.userData.type)?o.geometry.toJSON():undefined,position:o.position.toArray(),rotation:[o.rotation.x,o.rotation.y,o.rotation.z].map(THREE.MathUtils.radToDeg),scale:o.scale.toArray(),color:'#'+o.material.color.getHexString(),metalness:o.material.metalness,roughness:o.material.roughness}))};
}
function download(filename,data,type='application/json') {
  const a=document.createElement('a'); a.href=URL.createObjectURL(new Blob([data],{type})); a.download=filename; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href),500);
}
function save() {
  const data=serialize(); localStorage.setItem('forma-project',JSON.stringify(data));
  $('#save-status').textContent='Saved locally · '+new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
  toast('Project saved to this browser');
}
function load(data) {
  objects.slice().forEach(o=>scene.remove(o)); objects.length=0; idCounter=1;
  $('#project-name').value=data.name||'Untitled structure';
  (data.objects||[]).forEach(o=>addObject(o.type,o)); select(null); updateScene();
}
function toast(msg) {
  const t=$('#toast'); t.textContent=msg; t.classList.add('show');
  clearTimeout(window.__toast); window.__toast=setTimeout(()=>t.classList.remove('show'),2200);
}
function frame() {
  if(!selected) return;
  const box=new THREE.Box3().setFromObject(selected),center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3()).length();
  controls.target.copy(center); camera.position.copy(center).add(new THREE.Vector3(size*.9,size*.65,size*.9)); camera.lookAt(center);
}
function copySelected() {
  if(!selected) return;
  clipboard={type:selected.userData.type,geometry:['sliced','boolean'].includes(selected.userData.type)?selected.geometry.toJSON():undefined,position:selected.position.toArray(),rotation:[selected.rotation.x,selected.rotation.y,selected.rotation.z].map(THREE.MathUtils.radToDeg),scale:selected.scale.toArray(),color:'#'+selected.material.color.getHexString(),metalness:selected.material.metalness,roughness:selected.material.roughness};
  toast('Copied — Ctrl+V to paste');
}
function pasteObject() {
  if(!clipboard) return; addObject(clipboard.type,{...clipboard,name:undefined}); toast('Pasted');
}

// ── Cut / Slice ───────────────────────────────────────────────────────────
let cutAxis='y', cutMode='slice', cutPos=0, cutGap=0.3;
let cutBBox=null; // world bbox of selected when cut panel opened
let cutGizmoMode='translate', cutObjectCenter=new THREE.Vector3(), cutSliderMin=0, cutSliderMax=1, cutBaseFootprint=1;
const cutFootprint=new THREE.Vector2(1,1);
const cutFrame=new THREE.Object3D(); cutFrame.name='Cut plane modifier'; scene.add(cutFrame);

// Compact cutter box: the only cut preview shown in the viewport.
const cutHandleMat = new THREE.MeshStandardMaterial({color:0x6f6cff,transparent:true,opacity:0.22,roughness:0.35,metalness:0.05,side:THREE.DoubleSide,depthWrite:false});
const cutHandle = new THREE.Mesh(new THREE.BoxGeometry(1,1,1),cutHandleMat);
const cutHandleEdges = new THREE.LineSegments(new THREE.EdgesGeometry(cutHandle.geometry),new THREE.LineBasicMaterial({color:0x6f6cff,transparent:true,opacity:0.95}));
cutHandle.add(cutHandleEdges); cutHandle.renderOrder=998; cutHandle.visible=false; cutFrame.add(cutHandle);

function initCutPanel() {
  if(!selected) return;
  selected.updateMatrixWorld(true);
  cutBBox = new THREE.Box3().setFromObject(selected);
  const size = cutBBox.getSize(new THREE.Vector3());
  // auto-pick longest axis
  cutAxis = size.x>=size.y&&size.x>=size.z ? 'x' : size.z>=size.y ? 'z' : 'y';
  cutObjectCenter.copy(cutBBox.getCenter(new THREE.Vector3()));
  setCutFrameAxis(cutAxis, false);
  const objectSize=cutBBox.getSize(new THREE.Vector3());
  const handleSize=Math.max(objectSize.x,objectSize.y,objectSize.z)*1.12;
  cutBaseFootprint=handleSize;
  cutFrame.scale.set(1,1,1);
  cutHandle.scale.set(handleSize,handleSize,Math.max(0.04,handleSize*0.035));

  const min = cutAxis==='y'?cutBBox.min.y : cutAxis==='x'?cutBBox.min.x : cutBBox.min.z;
  const max = cutAxis==='y'?cutBBox.max.y : cutAxis==='x'?cutBBox.max.x : cutBBox.max.z;
  cutPos = (min+max)/2;

  // update axis pills
  document.querySelectorAll('[data-cut-axis]').forEach(b=>b.classList.toggle('active',b.dataset.cutAxis===cutAxis));

  // configure slider range to match object extent with padding
  const pad=(max-min)*0.1;
  const slider=document.getElementById('cut-pos-slider');
  cutSliderMin=min-pad; cutSliderMax=max+pad;
  slider.min=cutSliderMin.toFixed(3);
  slider.max=cutSliderMax.toFixed(3);
  slider.step=((max-min)/200).toFixed(4);
  slider.value=cutPos.toFixed(3);

  // gap slider
  const gapSlider=document.getElementById('cut-gap-slider');
  const objSize=max-min;
  gapSlider.min='0.02';
  gapSlider.max=(objSize*0.8).toFixed(3);
  gapSlider.step=(objSize/200).toFixed(4);
  gapSlider.value=Math.min(cutGap,objSize*0.5).toFixed(3);
  cutGap=parseFloat(gapSlider.value);

  updateCutReadouts();
  updateCutPlanes();
  document.getElementById('cut-context').classList.remove('hidden');
}

function hideCutPlane() {
  cutHandle.visible=false;
  transform.detach();
}

function setCutFrameAxis(axis, keepPosition=false) {
  if(!selected) return;
  selected.updateMatrixWorld(true);
  const bbox=new THREE.Box3().setFromObject(selected);
  const center=bbox.getCenter(new THREE.Vector3());
  const min=axis==='y'?bbox.min.y:axis==='x'?bbox.min.x:bbox.min.z;
  const max=axis==='y'?bbox.max.y:axis==='x'?bbox.max.x:bbox.max.z;
  const normal=new THREE.Vector3(axis==='x'?1:0,axis==='y'?1:0,axis==='z'?1:0);
  cutFrame.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),normal);
  if(!keepPosition) cutFrame.position.copy(center);
  else cutFrame.position.copy(center).add(normal.multiplyScalar(cutPos-((min+max)/2)));
  cutPos=cutFrame.position.dot(normal);
}

function updateCutPlanes() {
  if(!cutBBox) return;
  refreshCutFootprint();
  cutHandle.visible=true;
  const handleDepth=Math.max(0.04,cutMode==='band'?cutGap:cutHandle.scale.x*0.035);
  cutHandle.scale.z=handleDepth;
  // gap controls visibility
  document.getElementById('cut-gap-row').classList.toggle('hidden', cutMode!=='band');
  updateCutReadouts();
}

function updateCutReadouts() {
  document.getElementById('cut-pos-val').textContent = cutPos.toFixed(2);
  document.getElementById('cut-gap-val').textContent = cutGap.toFixed(2);
  document.getElementById('cut-pos-slider').value = cutPos;
  document.getElementById('cut-gap-slider').value = cutGap;
}

function setCutAxis(axis) {
  cutAxis=axis;
  document.querySelectorAll('[data-cut-axis]').forEach(b=>b.classList.toggle('active',b.dataset.cutAxis===axis));
  if(selected){ setCutFrameAxis(axis); updateCutPlanes(); }
}

function setCutMode(m) {
  cutMode=m;
  document.querySelectorAll('.cut-ctx-mode').forEach(b=>b.classList.remove('active'));
  document.getElementById(m==='slice'?'ctx-mode-slice':'ctx-mode-band').classList.add('active');
  updateCutPlanes();
}

function setCutGizmoMode(mode) {
  cutGizmoMode=mode;
  const buttonId=mode==='translate'?'move':mode==='rotate'?'rotate':'scale';
  document.querySelectorAll('.cut-gizmo-mode').forEach(b=>b.classList.toggle('active',b.id===`cut-gizmo-${buttonId}`));
  if(tool==='cut' && selected){
    transform.enabled=true;
    transform.setSpace('world');
    transform.setMode(mode);
    transform.attach(cutFrame);
    toast(mode==='rotate'?'Rotate gizmo active — drag a colored ring':mode==='scale'?'Scale gizmo active — resize the cutter':'Move gizmo active — drag an arrow');
  }
}

function getCutterSize() {
  // CSG dimensions are local to the cutter frame. Using world-axis scale
  // would swap the cutter footprint with its thin cutting depth when the
  // plane is aligned to X or Z.
  refreshCutFootprint();
  return new THREE.Vector3(
    cutFootprint.x,
    cutFootprint.y,
    Math.abs(cutHandle.scale.z*cutFrame.scale.z)
  );
}

function refreshCutFootprint() {
  cutFrame.updateMatrixWorld(true);
  cutFootprint.set(
    Math.abs(cutHandle.scale.x*cutFrame.scale.x),
    Math.abs(cutHandle.scale.y*cutFrame.scale.y)
  );
}

// ── CSG helpers ──────────────────────────────────────────────────────────
function toBakedBrush(mesh) {
  const geo=mesh.geometry.clone();
  mesh.updateMatrixWorld(true); geo.applyMatrix4(mesh.matrixWorld);
  const b=new Brush(geo,mesh.material); b.updateMatrixWorld(true); return b;
}
function csgSubtractBox(targetMesh, wx,wy,wz, cx,cy,cz, quaternion=null) {
  try {
    const brushA=toBakedBrush(targetMesh);
    const brushB=new Brush(new THREE.BoxGeometry(wx,wy,wz), new THREE.MeshStandardMaterial());
    brushB.position.set(cx,cy,cz); if(quaternion) brushB.quaternion.copy(quaternion); brushB.updateMatrixWorld(true);
    const result=(new Evaluator()).evaluate(brushA,brushB,SUBTRACTION);
    result.castShadow=result.receiveShadow=true;
    result.material=new THREE.MeshStandardMaterial({color:targetMesh.material.color.getHex(),metalness:targetMesh.material.metalness,roughness:targetMesh.material.roughness});
    return result;
  } catch(e) { console.error('CSG:',e); toast('Cut failed: '+e.message); return null; }
}
function removeObj(obj) {
  scene.remove(obj); const i=objects.indexOf(obj); if(i>-1) objects.splice(i,1);
  obj.geometry.dispose(); obj.material.dispose();
}

function performApply() {
  if(cutMode==='slice') performSlice(); else performBand();
}

function performSlice() {
  if(!selected){toast('Select an object first');return;}
  selected.updateMatrixWorld(true);
  const bbox=new THREE.Box3().setFromObject(selected);
  const normal=new THREE.Vector3(0,0,1).applyQuaternion(cutFrame.quaternion).normalize();
  const plane=cutFrame.position.clone(), BIG=500;
  const cutterSize=getCutterSize();
  const partial=Math.abs(cutterSize.x-cutBaseFootprint)>0.001||Math.abs(cutterSize.y-cutBaseFootprint)>0.001;
  let resA, resB;
  if(partial){
    const result=csgSubtractBox(selected,cutterSize.x,cutterSize.y,BIG,plane.x,plane.y,plane.z,cutFrame.quaternion);
    if(!result) return;
    result.name=selected.name+' (partial slice)'; result.userData.type='sliced';
    const old=selected; selected=null; selected2=null; hideCutPlane();
    document.getElementById('cut-context').classList.add('hidden');
    removeObj(old); scene.add(result); objects.push(result); select(result); updateScene(); setTool('select');
    toast('Partial slice applied'); return;
  }
  const positive=plane.clone().addScaledVector(normal,BIG/2);
  const negative=plane.clone().addScaledVector(normal,-BIG/2);
  resA=csgSubtractBox(selected,BIG,BIG,BIG,positive.x,positive.y,positive.z,cutFrame.quaternion);
  resB=csgSubtractBox(selected,BIG,BIG,BIG,negative.x,negative.y,negative.z,cutFrame.quaternion);
  if(!resA||!resB) return;
  const g=0.12;
  resA.position.addScaledVector(normal,g); resB.position.addScaledVector(normal,-g);
  const nb=selected.name; resA.name=nb+' A'; resA.userData.type='sliced'; resB.name=nb+' B'; resB.userData.type='sliced';
  const old=selected; selected=null; selected2=null; hideCutPlane();
  document.getElementById('cut-context').classList.add('hidden');
  removeObj(old);
  scene.add(resA); objects.push(resA); scene.add(resB); objects.push(resB);
  select(resA); updateScene(); setTool('select'); toast('Sliced — W to move pieces apart');
}

function performBand() {
  if(!selected){toast('Select an object first');return;}
  selected.updateMatrixWorld(true);
  const bbox=new THREE.Box3().setFromObject(selected);
  const cutterSize=getCutterSize();
  // Use the cutter's final visible thickness, including any Scale gizmo
  // adjustment, instead of only the raw Gap slider value.
  const gap=Math.max(0.01,cutterSize.z), plane=cutFrame.position;
  const result=csgSubtractBox(selected,cutterSize.x,cutterSize.y,gap,plane.x,plane.y,plane.z,cutFrame.quaternion);
  if(!result) return;
  result.name=selected.name+' (cut)'; result.userData.type='sliced';
  const old=selected; selected=null; hideCutPlane();
  document.getElementById('cut-context').classList.add('hidden');
  removeObj(old);
  scene.add(result); objects.push(result); select(result); updateScene(); setTool('select'); toast('Band removed');
}

// ── Boolean ops ──────────────────────────────────────────────────────────
function performBool(op) {
  if(!selected||!selected2){toast('Select two objects first');return;}
  try {
    const opConst=op==='subtract'?SUBTRACTION:op==='union'?ADDITION:INTERSECTION;
    const brushA=new Brush(selected.geometry.clone(),selected.material);
    brushA.position.copy(selected.position); brushA.rotation.copy(selected.rotation); brushA.scale.copy(selected.scale); brushA.updateMatrixWorld(true);
    const brushB=new Brush(selected2.geometry.clone(),selected2.material);
    brushB.position.copy(selected2.position); brushB.rotation.copy(selected2.rotation); brushB.scale.copy(selected2.scale); brushB.updateMatrixWorld(true);
    const result=(new Evaluator()).evaluate(brushA,brushB,opConst);
    result.material=new THREE.MeshStandardMaterial({color:selected.material.color.getHex(),metalness:selected.material.metalness,roughness:selected.material.roughness});
    result.castShadow=result.receiveShadow=true;
    result.name=`${op[0].toUpperCase()+op.slice(1)} ${idCounter++}`; result.userData.type='boolean';
    scene.add(result); objects.push(result);
    [selected,selected2].forEach(o=>{scene.remove(o);o.geometry.dispose();o.material.dispose();objects.splice(objects.indexOf(o),1);});
    selected2=null; select(result); updateScene(); toast(`Boolean ${op} applied`);
  } catch(err) { toast('Boolean op failed: '+err.message); console.error(err); }
}

// ── Event wiring ─────────────────────────────────────────────────────────
document.querySelectorAll('[data-tool]').forEach(b=>b.onclick=()=>setTool(b.dataset.tool));
document.querySelectorAll('[data-add]').forEach(b=>b.onclick=()=>addObject(b.dataset.add));
document.querySelectorAll('[data-bool]').forEach(b=>b.onclick=()=>performBool(b.dataset.bool));

// Cut axis pills
document.querySelectorAll('[data-cut-axis]').forEach(b=>b.onclick=()=>setCutAxis(b.dataset.cutAxis));
document.getElementById('cut-gizmo-move').onclick=()=>setCutGizmoMode('translate');
document.getElementById('cut-gizmo-rotate').onclick=()=>setCutGizmoMode('rotate');
document.getElementById('cut-gizmo-scale').onclick=()=>setCutGizmoMode('scale');
// Cut mode
document.getElementById('ctx-mode-slice').onclick=()=>setCutMode('slice');
document.getElementById('ctx-mode-band').onclick=()=>setCutMode('band');
// Cut position slider
document.getElementById('cut-pos-slider').oninput=e=>{
  cutPos=parseFloat(e.target.value);
  const normal=new THREE.Vector3(0,0,1).applyQuaternion(cutFrame.quaternion).normalize();
  cutFrame.position.copy(cutObjectCenter).addScaledVector(normal,cutPos-cutObjectCenter.dot(normal));
  updateCutPlanes();
};
// Cut gap slider
document.getElementById('cut-gap-slider').oninput=e=>{
  cutGap=parseFloat(e.target.value);
  updateCutPlanes();
};
// Apply
document.getElementById('ctx-apply-btn').onclick=performApply;

document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('[data-view]').forEach(x=>x.classList.remove('active')); b.classList.add('active');
  const v=b.dataset.view;
  if(v==='top') camera.position.set(0,10,.01); else if(v==='front') camera.position.set(0,2,10); else camera.position.set(7,5.5,8);
  controls.target.set(0,1,0);
});

$('#save-btn').onclick=save;
$('#load-btn').onclick=()=>$('#load-input').click();
$('#export-btn').onclick=()=>{ download(`${$('#project-name').value||'forma-project'}.json`,JSON.stringify(serialize(),null,2)); toast('Scene JSON exported'); };
$('#clear-btn').onclick=()=>{ if(objects.length&&confirm('Clear the whole scene?')){ objects.slice().forEach(o=>scene.remove(o)); objects.length=0; select(null); updateScene(); }};
$('#delete-btn').onclick=removeSelected;
$('#focus-btn').onclick=frame;
$('#grid-btn').onclick=()=>grid.visible=!grid.visible;
$('#camera-btn').onclick=()=>{ const d=renderer.domElement.toDataURL('image/png'); const a=document.createElement('a'); a.href=d; a.download='forma-viewport.png'; a.click(); };

$('#object-name').oninput=e=>{ if(selected){selected.name=e.target.value||'Object'; updateScene();}};
document.querySelectorAll('[data-transform]').forEach(input=>input.oninput=e=>{
  if(!selected) return;
  const [a,b]=input.dataset.transform.split('.');
  let val=Number(e.target.value)||0;
  if(a==='rotation') val=THREE.MathUtils.degToRad(val);
  selected[a][b]=val;
});
$('#object-color').oninput=e=>{ if(selected){selected.material.color.set(e.target.value); syncInspector();}};
['metalness','roughness'].forEach(k=>$('#object-'+k).oninput=e=>{
  if(selected){ selected.material[k]=Number(e.target.value); $(`#${k}-value`).textContent=Number(e.target.value).toFixed(2); }
});

renderer.domElement.addEventListener('pointerdown', e=>{
  // Objects remain selectable while using Move/Rotate/Scale so the gizmo
  // always follows the object the user just clicked. Cut uses its own box.
  if(tool==='cut' || gizmoPointerDown) return;
  const rect=renderer.domElement.getBoundingClientRect();
  const mouse=new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);
  const ray=new THREE.Raycaster(); ray.setFromCamera(mouse,camera);
  const hit=ray.intersectObjects(objects)[0];
  select(hit?.object||null, e.shiftKey);
});

document.addEventListener('keydown', e=>{
  if(e.target.tagName==='INPUT') return;
  if(e.ctrlKey&&e.key.toLowerCase()==='c'){copySelected();return;}
  if(e.ctrlKey&&e.key.toLowerCase()==='v'){pasteObject();return;}
  if(tool==='cut' && e.key.toLowerCase()==='r'){setCutGizmoMode('rotate');return;}
  if(tool==='cut' && e.key.toLowerCase()==='s'){setCutGizmoMode('scale');return;}
  const map={q:'select',w:'translate',e:'rotate',r:'scale',t:'cut'};
  if(map[e.key.toLowerCase()]) setTool(map[e.key.toLowerCase()]);
  if(e.key==='Escape'&&tool==='cut') setTool('select');
  if(e.key.toLowerCase()==='f') frame();
  if(e.key==='Delete'||e.key==='Backspace') removeSelected();
  if(e.key==='1') addObject('box');
  if(e.key==='2') addObject('sphere');
  if(e.key==='3') addObject('cylinder');
  if(e.key==='4') addObject('torus');
});

$('#load-input').onchange=e=>{
  const file=e.target.files[0]; if(!file) return;
  const reader=new FileReader();
  reader.onload=()=>{try{load(JSON.parse(reader.result));toast('Project loaded');}catch{toast('That file is not a Forma project');}};
  reader.readAsText(file);
};

const stored=localStorage.getItem('forma-project');
if(stored) try{load(JSON.parse(stored));}catch{}

function resize(){const r=viewport.getBoundingClientRect();camera.aspect=r.width/r.height;camera.updateProjectionMatrix();renderer.setSize(r.width,r.height,false);}
window.addEventListener('resize',resize); resize();
function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);}
animate(); updateScene();
