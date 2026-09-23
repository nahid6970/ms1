import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { ADDITION, SUBTRACTION, INTERSECTION, Evaluator, Brush } from 'three-bvh-csg';
window.__formaStarted = true;

const $ = (s) => document.querySelector(s);
const viewport = $('#viewport');
const scene = new THREE.Scene(); scene.background = new THREE.Color(0xeef0f4);
const camera = new THREE.PerspectiveCamera(45, 1, .1, 1000); camera.position.set(7, 5.5, 8);
const renderer = new THREE.WebGLRenderer({ antialias:true, preserveDrawingBuffer:true }); renderer.setPixelRatio(Math.min(devicePixelRatio,2)); renderer.shadowMap.enabled=true; renderer.shadowMap.type=THREE.PCFSoftShadowMap; viewport.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping=true; controls.target.set(0,1,0);
const transform = new TransformControls(camera, renderer.domElement); scene.add(transform); transform.addEventListener('dragging-changed', e => controls.enabled=!e.value); transform.addEventListener('objectChange', syncInspector);
scene.add(new THREE.HemisphereLight(0xffffff,0x9ea7b5,2.2)); const key=new THREE.DirectionalLight(0xffffff,3); key.position.set(5,9,4); key.castShadow=true; scene.add(key);
const grid = new THREE.GridHelper(20,20,0xc7cad3,0xdfe1e7); grid.position.y=-.01; scene.add(grid);
const ground = new THREE.Mesh(new THREE.PlaneGeometry(20,20),new THREE.ShadowMaterial({opacity:.09})); ground.rotation.x=-Math.PI/2; ground.receiveShadow=true; scene.add(ground);
let selected=null, selected2=null, tool='select', idCounter=1, clipboard=null; const objects=[];
function copySelected(){if(!selected)return;clipboard={type:selected.userData.type,position:selected.position.toArray(),rotation:[selected.rotation.x,selected.rotation.y,selected.rotation.z].map(THREE.MathUtils.radToDeg),scale:selected.scale.toArray(),color:'#'+selected.material.color.getHexString(),metalness:selected.material.metalness,roughness:selected.material.roughness};toast('Copied — Ctrl+V to paste');}
function pasteObject(){if(!clipboard)return;addObject(clipboard.type,{...clipboard,name:undefined});toast('Pasted');}
const colors=['#6f6cff','#ff7b58','#55b5a1','#e8ad58','#d975aa'];
const geometryFor = type => ({box:new THREE.BoxGeometry(1.5,1.5,1.5),sphere:new THREE.SphereGeometry(1,32,20),cylinder:new THREE.CylinderGeometry(.8,.8,1.7,32),torus:new THREE.TorusGeometry(.75,.28,16,40)})[type];
function addObject(type='box', data={}) { const material=new THREE.MeshStandardMaterial({color:data.color||colors[(objects.length)%colors.length],metalness:data.metalness??.2,roughness:data.roughness??.4}); const mesh=new THREE.Mesh(geometryFor(type),material); mesh.name=data.name||`${type[0].toUpperCase()+type.slice(1)} ${idCounter++}`; mesh.castShadow=true; mesh.receiveShadow=true; mesh.userData.type=type; mesh.position.set(...(data.position||[0, type==='box'?0.75:1,0])); if(data.rotation) mesh.rotation.set(...data.rotation.map(v=>THREE.MathUtils.degToRad(v))); if(data.scale) mesh.scale.set(...data.scale); scene.add(mesh); objects.push(mesh); select(mesh); updateScene(); return mesh; }
function select(obj, additive=false){ if(additive && selected && obj && obj!==selected){selected2=obj;}else{selected=obj;selected2=null;} transform.detach(); if(selected && tool!=='select') transform.attach(selected); syncInspector(); updateScene(); updateBoolUI(); }
function updateBoolUI(){ const two=selected&&selected2; ['bool-subtract','bool-union','bool-intersect'].forEach(id=>{const b=document.getElementById(id);if(b)b.disabled=!two;}); const hint=document.getElementById('bool-hint'); if(hint)hint.textContent=two?`A = ${selected.name}  ·  B = ${selected2.name}`:'Select 2 objects (Shift+click B)'; }
function setTool(next){ tool=next; document.querySelectorAll('.tool-card').forEach(b=>b.classList.toggle('active',b.dataset.tool===next)); if(next==='cut'){transform.detach();if(selected)showCutGizmo();else toast('Select an object first');}else{hideCutGizmo();if(selected&&next!=='select'){transform.setMode(next==='translate'?'translate':next==='rotate'?'rotate':'scale');transform.attach(selected)}else transform.detach();} }
function syncInspector(){ const has=!!selected; $('#empty-inspector').classList.toggle('hidden',has); $('#inspector-content').classList.toggle('hidden',!has); $('#selection-label').textContent=has?'OBJECT':'NONE SELECTED'; if(!has)return; $('#object-name').value=selected.name; $('#selected-shape').style.background=selected.material.color.getStyle(); const vals={position:{x:selected.position.x,y:selected.position.y,z:selected.position.z},rotation:{x:THREE.MathUtils.radToDeg(selected.rotation.x),y:THREE.MathUtils.radToDeg(selected.rotation.y),z:THREE.MathUtils.radToDeg(selected.rotation.z)},scale:{x:selected.scale.x,y:selected.scale.y,z:selected.scale.z}}; document.querySelectorAll('[data-transform]').forEach(input=>{const [a,b]=input.dataset.transform.split('.');input.value=Number(vals[a][b].toFixed(2));}); $('#object-color').value='#'+selected.material.color.getHexString();$('#color-value').textContent=$('#object-color').value.toUpperCase();$('#object-metalness').value=selected.material.metalness;$('#metalness-value').textContent=selected.material.metalness.toFixed(2);$('#object-roughness').value=selected.material.roughness;$('#roughness-value').textContent=selected.material.roughness.toFixed(2); }
function updateScene(){ const tree=$('#scene-tree'); tree.innerHTML=objects.length?'':`<div class="tree-empty">Your scene is empty</div>`; objects.forEach(o=>{const row=document.createElement('button');const isSel=o===selected||o===selected2;row.className=`tree-row ${isSel?'selected':''}`;if(o===selected2)row.style.opacity='0.7';row.innerHTML=`<span class="tree-icon"></span><span class="tree-name">${o.name}</span><span class="tree-type">${o.userData.type}</span>`;row.onclick=(e)=>select(o,e.shiftKey);tree.appendChild(row)});$('#object-count').textContent=`${objects.length} object${objects.length===1?'':'s'}`;$('#viewport-empty').style.display=objects.length?'none':'flex'; }
function removeSelected(){if(!selected)return; scene.remove(selected);selected.geometry.dispose();selected.material.dispose();objects.splice(objects.indexOf(selected),1);select(objects.at(-1)||null);toast('Object deleted');}
function serialize(){return {version:1,name:$('#project-name').value,objects:objects.map(o=>({name:o.name,type:o.userData.type,position:o.position.toArray(),rotation:[o.rotation.x,o.rotation.y,o.rotation.z].map(THREE.MathUtils.radToDeg),scale:o.scale.toArray(),color:'#'+o.material.color.getHexString(),metalness:o.material.metalness,roughness:o.material.roughness}))};}
function download(filename,data,type='application/json'){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([data],{type}));a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500);}
function save(){const data=serialize();localStorage.setItem('forma-project',JSON.stringify(data));$('#save-status').textContent='Saved locally · '+new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});toast('Project saved to this browser');}
function load(data){objects.slice().forEach(o=>scene.remove(o));objects.length=0;idCounter=1;$('#project-name').value=data.name||'Untitled structure';(data.objects||[]).forEach(o=>addObject(o.type,o));select(null);updateScene();}
function toast(msg){const t=$('#toast');t.textContent=msg;t.classList.add('show');clearTimeout(window.__toast);window.__toast=setTimeout(()=>t.classList.remove('show'),2200)}
function frame(){if(!selected)return;const box=new THREE.Box3().setFromObject(selected),center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3()).length();controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(size*.9,size*.65,size*.9));camera.lookAt(center);}

let cutAxis='y';

// ── Cut plane gizmo ────────────────────────────────────────────────────────
const cutPlaneMat = new THREE.MeshBasicMaterial({color:0x6f6cff, transparent:true, opacity:0.25, side:THREE.DoubleSide, depthWrite:false});
const cutPlaneGeo = new THREE.PlaneGeometry(20,20);
const cutPlaneMesh = new THREE.Mesh(cutPlaneGeo, cutPlaneMat);
cutPlaneMesh.renderOrder=999;
// invisible drag handle — a thin box the TransformControls attaches to
const cutHandle = new THREE.Mesh(new THREE.BoxGeometry(0.01,0.01,0.01), new THREE.MeshBasicMaterial({visible:false}));
scene.add(cutHandle);

const cutTransform = new TransformControls(camera, renderer.domElement);
cutTransform.setMode('translate');
cutTransform.setSpace('world');
scene.add(cutTransform);
cutTransform.addEventListener('dragging-changed', e=>{ controls.enabled=!e.value; });
cutTransform.addEventListener('objectChange', ()=>{
  const pos = cutAxis==='y'?cutHandle.position.y : cutAxis==='x'?cutHandle.position.x : cutHandle.position.z;
  syncCutPlane(pos);
  document.getElementById('cut-ov-pos').textContent = pos.toFixed(2);
  // also sync the sidebar input
  const pi = document.getElementById('cut-position'); if(pi) pi.value=pos.toFixed(2);
});

function syncCutPlane(pos){
  if(cutAxis==='y'){
    cutPlaneMesh.rotation.set(0,0,0); cutPlaneMesh.position.set(0,pos,0);
    cutHandle.position.set(0,pos,0); cutTransform.showX=false; cutTransform.showY=true; cutTransform.showZ=false;
  } else if(cutAxis==='x'){
    cutPlaneMesh.rotation.set(0,Math.PI/2,0); cutPlaneMesh.position.set(pos,0,0);
    cutHandle.position.set(pos,0,0); cutTransform.showX=true; cutTransform.showY=false; cutTransform.showZ=false;
  } else {
    cutPlaneMesh.rotation.set(Math.PI/2,0,0); cutPlaneMesh.position.set(0,0,pos);
    cutHandle.position.set(0,0,pos); cutTransform.showX=false; cutTransform.showY=false; cutTransform.showZ=true;
  }
}

function showCutGizmo(){
  if(!selected) return;
  selected.updateMatrixWorld(true);
  const bbox=new THREE.Box3().setFromObject(selected);
  const center=bbox.getCenter(new THREE.Vector3());
  const pos=cutAxis==='y'?center.y:cutAxis==='x'?center.x:center.z;
  scene.add(cutPlaneMesh);
  cutTransform.attach(cutHandle);
  syncCutPlane(pos);
  document.getElementById('cut-ov-pos').textContent=pos.toFixed(2);
  const pi=document.getElementById('cut-position'); if(pi) pi.value=pos.toFixed(2);
  document.getElementById('cut-overlay').classList.remove('hidden');
}

function hideCutGizmo(){
  scene.remove(cutPlaneMesh);
  cutTransform.detach();
  document.getElementById('cut-overlay').classList.add('hidden');
}

// Override setTool to handle cut mode
const _origSetTool = setTool; // forward ref — we'll redefine below

// ── Bake + CSG helpers ────────────────────────────────────────────────────
// Bake world transform into geometry so Brush can work at identity position
function toBakedBrush(mesh){
  const geo=mesh.geometry.clone();
  mesh.updateMatrixWorld(true);
  geo.applyMatrix4(mesh.matrixWorld);
  const b=new Brush(geo, mesh.material);
  b.updateMatrixWorld(true);
  return b;
}

// Subtract a world-space box from a mesh, returns result Brush or null
function csgSubtractBox(targetMesh, wx,wy,wz, cx,cy,cz){
  try{
    const brushA=toBakedBrush(targetMesh);
    const cutGeo=new THREE.BoxGeometry(wx,wy,wz);
    const brushB=new Brush(cutGeo, new THREE.MeshStandardMaterial());
    brushB.position.set(cx,cy,cz);
    brushB.updateMatrixWorld(true);
    const result=(new Evaluator()).evaluate(brushA, brushB, SUBTRACTION);
    result.castShadow=true; result.receiveShadow=true;
    result.material=new THREE.MeshStandardMaterial({color:targetMesh.material.color.getHex(),metalness:targetMesh.material.metalness,roughness:targetMesh.material.roughness});
    return result;
  }catch(e){console.error('CSG error:',e);toast('Cut failed: '+e.message);return null;}
}

// Remove original object from scene+objects array
function removeObj(obj){
  scene.remove(obj);
  const idx=objects.indexOf(obj);
  if(idx>-1)objects.splice(idx,1);
  obj.geometry.dispose();
  obj.material.dispose();
}

function getCutPos(){
  return cutAxis==='y'?cutHandle.position.y:cutAxis==='x'?cutHandle.position.x:cutHandle.position.z;
}

function performSlice(){
  if(!selected){toast('Select an object first');return;}
  selected.updateMatrixWorld(true);
  const bbox=new THREE.Box3().setFromObject(selected);
  const center=bbox.getCenter(new THREE.Vector3());
  const pos=getCutPos();
  const BIG=500;

  let resTop, resBot;
  if(cutAxis==='y'){
    const topH=bbox.max.y-pos+BIG; resTop=csgSubtractBox(selected,BIG,topH,BIG,center.x,pos+topH/2,center.z);
    const botH=pos-bbox.min.y+BIG; resBot=csgSubtractBox(selected,BIG,botH,BIG,center.x,pos-botH/2,center.z);
  } else if(cutAxis==='x'){
    const rH=bbox.max.x-pos+BIG; resTop=csgSubtractBox(selected,rH,BIG,BIG,pos+rH/2,center.y,center.z);
    const lH=pos-bbox.min.x+BIG; resBot=csgSubtractBox(selected,lH,BIG,BIG,pos-lH/2,center.y,center.z);
  } else {
    const fH=bbox.max.z-pos+BIG; resTop=csgSubtractBox(selected,BIG,BIG,fH,center.x,center.y,pos+fH/2);
    const bH=pos-bbox.min.z+BIG; resBot=csgSubtractBox(selected,BIG,BIG,bH,center.x,center.y,pos-bH/2);
  }
  if(!resTop||!resBot) return;

  const gap=0.12;
  if(cutAxis==='y'){resTop.position.y+=gap;resBot.position.y-=gap;}
  else if(cutAxis==='x'){resTop.position.x+=gap;resBot.position.x-=gap;}
  else{resTop.position.z+=gap;resBot.position.z-=gap;}

  const nameBase=selected.name;
  resTop.name=nameBase+' A'; resTop.userData.type='sliced';
  resBot.name=nameBase+' B'; resBot.userData.type='sliced';
  const old=selected; selected=null; selected2=null;
  hideCutGizmo();
  removeObj(old);
  scene.add(resTop); objects.push(resTop);
  scene.add(resBot); objects.push(resBot);
  select(resTop); updateScene(); toast('Sliced — press W to move pieces apart');
}

function performBand(){
  if(!selected){toast('Select an object first');return;}
  selected.updateMatrixWorld(true);
  const bbox=new THREE.Box3().setFromObject(selected);
  const center=bbox.getCenter(new THREE.Vector3());
  const pos=getCutPos();
  const thickness=Math.max(0.01,Number(document.getElementById('ov-thickness').value)||0.3);
  const BIG=500;

  let result;
  if(cutAxis==='y')      result=csgSubtractBox(selected,BIG,thickness,BIG,center.x,pos,center.z);
  else if(cutAxis==='x') result=csgSubtractBox(selected,thickness,BIG,BIG,pos,center.y,center.z);
  else                   result=csgSubtractBox(selected,BIG,BIG,thickness,center.x,center.y,pos);

  if(!result) return;
  result.name=selected.name+' (cut)'; result.userData.type='sliced';
  const old=selected; selected=null;
  hideCutGizmo();
  removeObj(old);
  scene.add(result); objects.push(result);
  select(result); updateScene(); toast('Band removed');
}
function performBool(op){
  if(!selected||!selected2){toast('Select two objects first');return;}
  try{
    const opConst=op==='subtract'?SUBTRACTION:op==='union'?ADDITION:INTERSECTION;
    const brushA=new Brush(selected.geometry.clone(), selected.material);
    brushA.position.copy(selected.position); brushA.rotation.copy(selected.rotation); brushA.scale.copy(selected.scale);
    brushA.updateMatrixWorld(true);
    const brushB=new Brush(selected2.geometry.clone(), selected2.material);
    brushB.position.copy(selected2.position); brushB.rotation.copy(selected2.rotation); brushB.scale.copy(selected2.scale);
    brushB.updateMatrixWorld(true);
    const evaluator=new Evaluator();
    const result=evaluator.evaluate(brushA, brushB, opConst);
    result.material=new THREE.MeshStandardMaterial({color:selected.material.color.getHex(),metalness:selected.material.metalness,roughness:selected.material.roughness});
    result.castShadow=true; result.receiveShadow=true;
    result.name=`${op[0].toUpperCase()+op.slice(1)} ${idCounter++}`;
    result.userData.type='boolean';
    scene.add(result); objects.push(result);
    [selected,selected2].forEach(o=>{scene.remove(o);o.geometry.dispose();o.material.dispose();objects.splice(objects.indexOf(o),1);});
    selected2=null; select(result); updateScene(); toast(`Boolean ${op} applied`);
  }catch(err){toast('Boolean op failed: '+err.message);console.error(err);}
}
document.querySelectorAll('[data-tool]').forEach(b=>b.onclick=()=>setTool(b.dataset.tool));document.querySelectorAll('[data-add]').forEach(b=>b.onclick=()=>addObject(b.dataset.add));
document.querySelectorAll('[data-bool]').forEach(b=>b.onclick=()=>performBool(b.dataset.bool));
// sidebar axis pills (legacy panel)
document.querySelectorAll('.axis-pill').forEach(b=>b.onclick=()=>{document.querySelectorAll('.axis-pill').forEach(p=>p.classList.remove('active'));b.classList.add('active');cutAxis=b.dataset.axis;if(tool==='cut'&&selected)showCutGizmo();});
// overlay axis pills
document.querySelectorAll('[data-cut-axis]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-cut-axis]').forEach(p=>p.classList.remove('active'));b.classList.add('active');cutAxis=b.dataset.cutAxis;if(selected)showCutGizmo();});
$('#slice-half-btn').onclick=performSlice;
$('#slice-band-btn').onclick=performBand;
document.getElementById('ov-slice-btn').onclick=performSlice;
document.getElementById('ov-band-btn').onclick=performBand;
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-view]').forEach(x=>x.classList.remove('active'));b.classList.add('active');const v=b.dataset.view;if(v==='top')camera.position.set(0,10,.01);else if(v==='front')camera.position.set(0,2,10);else camera.position.set(7,5.5,8);controls.target.set(0,1,0);});
$('#save-btn').onclick=save;$('#load-btn').onclick=()=>$('#load-input').click();$('#export-btn').onclick=()=>{download(`${$('#project-name').value||'forma-project'}.json`,JSON.stringify(serialize(),null,2));toast('Scene JSON exported');};$('#clear-btn').onclick=()=>{if(objects.length&&confirm('Clear the whole scene?')){objects.slice().forEach(o=>scene.remove(o));objects.length=0;select(null);updateScene();}};$('#delete-btn').onclick=removeSelected;$('#focus-btn').onclick=frame;$('#grid-btn').onclick=()=>grid.visible=!grid.visible;$('#camera-btn').onclick=()=>{const dataUrl=renderer.domElement.toDataURL('image/png');const a=document.createElement('a');a.href=dataUrl;a.download='forma-viewport.png';a.click();};
$('#object-name').oninput=e=>{if(selected){selected.name=e.target.value||'Object';updateScene();}};document.querySelectorAll('[data-transform]').forEach(input=>input.oninput=e=>{if(!selected)return;const [a,b]=input.dataset.transform.split('.');let val=Number(e.target.value)||0;if(a==='rotation')val=THREE.MathUtils.degToRad(val);selected[a][b]=val;});$('#object-color').oninput=e=>{if(selected){selected.material.color.set(e.target.value);syncInspector();}};['metalness','roughness'].forEach(k=>$('#object-'+k).oninput=e=>{if(selected){selected.material[k]=Number(e.target.value);$(`#${k}-value`).textContent=Number(e.target.value).toFixed(2);}});
renderer.domElement.addEventListener('pointerdown',e=>{if(tool!=='select')return;const rect=renderer.domElement.getBoundingClientRect(),mouse=new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1),ray=new THREE.Raycaster();ray.setFromCamera(mouse,camera);const hit=ray.intersectObjects(objects)[0];select(hit?.object||null, e.shiftKey);});
document.addEventListener('keydown',e=>{if(e.target.tagName==='INPUT')return;if(e.ctrlKey&&e.key.toLowerCase()==='c'){copySelected();return;}if(e.ctrlKey&&e.key.toLowerCase()==='v'){pasteObject();return;}const map={q:'select',w:'translate',e:'rotate',r:'scale',t:'cut'};if(map[e.key.toLowerCase()])setTool(map[e.key.toLowerCase()]);if(e.key==='Escape'&&tool==='cut')setTool('select');if(e.key.toLowerCase()==='f')frame();if(e.key==='Delete'||e.key==='Backspace')removeSelected();if(e.key==='1')addObject('box');if(e.key==='2')addObject('sphere');if(e.key==='3')addObject('cylinder');if(e.key==='4')addObject('torus');});
$('#load-input').onchange=e=>{const file=e.target.files[0];if(!file)return;const reader=new FileReader();reader.onload=()=>{try{load(JSON.parse(reader.result));toast('Project loaded')}catch{toast('That file is not a Forma project')}};reader.readAsText(file);};
const stored=localStorage.getItem('forma-project');if(stored)try{load(JSON.parse(stored));}catch{};function resize(){const r=viewport.getBoundingClientRect();camera.aspect=r.width/r.height;camera.updateProjectionMatrix();renderer.setSize(r.width,r.height,false)}window.addEventListener('resize',resize);resize();
function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera)}animate();updateScene();
