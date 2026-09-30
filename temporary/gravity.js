import * as THREE from 'three';

const viewport=document.querySelector('#viewport');
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x0a1120);
scene.fog=new THREE.FogExp2(0x0a1120,0.019);
const camera=new THREE.PerspectiveCamera(43,innerWidth/innerHeight,.1,100);
camera.position.set(0,5.4,14);
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;viewport.appendChild(renderer.domElement);
scene.add(new THREE.HemisphereLight(0x97b9e5,0x1b2330,2.2));
const keyLight=new THREE.DirectionalLight(0xd6ffe9,3.2);keyLight.position.set(-5,9,8);keyLight.castShadow=true;keyLight.shadow.mapSize.set(1024,1024);scene.add(keyLight);
const rim=new THREE.PointLight(0x8069ff,42,25);rim.position.set(2,3,-4);scene.add(rim);
const floorMat=new THREE.MeshStandardMaterial({color:0x26364c,metalness:.35,roughness:.48});
const edgeMat=new THREE.MeshStandardMaterial({color:0x74e7c0,emissive:0x258f75,emissiveIntensity:1.2,metalness:.4,roughness:.3});
const platformMat=new THREE.MeshStandardMaterial({color:0x25364a,metalness:.35,roughness:.4});
const playerMat=new THREE.MeshStandardMaterial({color:0xc1ffe1,emissive:0x25543e,emissiveIntensity:.45,metalness:.12,roughness:.3});
const world=new THREE.Group();scene.add(world);
function block(x,y,z,w,h,d,material=platformMat,glow=true){const mesh=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),material);mesh.position.set(x,y,z);mesh.castShadow=true;mesh.receiveShadow=true;world.add(mesh);if(glow){const line=new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry),new THREE.LineBasicMaterial({color:0x568d91,transparent:true,opacity:.6}));mesh.add(line);}return mesh;}
// A little mirrored obstacle course in a quiet, endless-looking shaft.
block(0,-3.55,0,34,.5,5,floorMat);block(0,3.55,0,34,.5,5,floorMat);
// luminous rails mark the two gravitational surfaces
for(const y of [-3.28,3.28]){const rail=new THREE.Mesh(new THREE.BoxGeometry(34,.035,5.05),new THREE.MeshBasicMaterial({color:0x284d52,transparent:true,opacity:.32}));rail.position.set(0,y,0);world.add(rail);}
block(4,-2.35,0,2.1,.25,3.2);block(8,-1.22,0,2.2,.25,3.2);block(11.7,-2.05,0,2.4,.25,3.2);
block(-2,2.35,0,2.2,.25,3.2);block(2,1.25,0,2.3,.25,3.2);block(6,2.25,0,2.1,.25,3.2);block(10,1.2,0,2.2,.25,3.2);
// Floating teeth make timing and mid-air flips matter.
block(6,0,0,.45,1.5,2.7,new THREE.MeshStandardMaterial({color:0x3b365c,emissive:0x1a1535,emissiveIntensity:.8,metalness:.4}));
block(12,0,0,.45,1.65,2.7,new THREE.MeshStandardMaterial({color:0x3b365c,emissive:0x1a1535,emissiveIntensity:.8,metalness:.4}));
// Distant graphic debris and subtle stars.
const dustGeo=new THREE.BufferGeometry(),dust=[];for(let i=0;i<230;i++)dust.push((Math.random()-.5)*60,(Math.random()-.5)*32,-8-Math.random()*22);dustGeo.setAttribute('position',new THREE.Float32BufferAttribute(dust,3));const dustCloud=new THREE.Points(dustGeo,new THREE.PointsMaterial({color:0x8fb8cd,size:.035,transparent:true,opacity:.55}));scene.add(dustCloud);
// Player capsule: a glowing core and small direction indicator.
const player=new THREE.Group();world.add(player);
const body=new THREE.Mesh(new THREE.CapsuleGeometry(.34,.55,5,12),playerMat);body.castShadow=true;body.receiveShadow=true;player.add(body);
const visor=new THREE.Mesh(new THREE.BoxGeometry(.34,.095,.41),new THREE.MeshStandardMaterial({color:0x152333,emissive:0x477f78,emissiveIntensity:.9,metalness:.3,roughness:.2}));visor.position.set(.11,.1,.28);player.add(visor);
const pack=new THREE.Mesh(new THREE.BoxGeometry(.2,.38,.22),new THREE.MeshStandardMaterial({color:0x8ba5a7,metalness:.7,roughness:.25}));pack.position.set(-.35,-.02,-.04);player.add(pack);
let x=-13.8,y=-2.8,vy=0,gravity=1,grounded=true,flipCooldown=0,gameState='intro',shards=0,elapsed=0,checkpoint=-13.8;
player.position.set(x,y,0);
const keys=new Set(),collected=new Set();
const shardPositions=[[-7,-2.15],[0,2.2],[4,-2.1],[8,2.0],[11.7,-1.6]];
const shardsMeshes=shardPositions.map(([sx,sy],i)=>{const g=new THREE.Group();g.position.set(sx,sy,0);const gem=new THREE.Mesh(new THREE.OctahedronGeometry(.32,0),new THREE.MeshStandardMaterial({color:0xffd784,emissive:0xffac3e,emissiveIntensity:2,metalness:.25,roughness:.2}));gem.rotation.z=Math.PI/4;g.add(gem);const halo=new THREE.Mesh(new THREE.TorusGeometry(.49,.018,6,32),new THREE.MeshBasicMaterial({color:0xffdf9c,transparent:true,opacity:.56}));g.add(halo);g.userData.gem=gem;world.add(g);return g;});
// Exit portal at the far end.
const portal=new THREE.Group();portal.position.set(14.4,0,0);const portalRing=new THREE.Mesh(new THREE.TorusGeometry(.85,.08,12,64),new THREE.MeshStandardMaterial({color:0x9cf8d1,emissive:0x4af9b5,emissiveIntensity:1.9,metalness:.25,roughness:.25}));portal.add(portalRing);const portalCore=new THREE.Mesh(new THREE.CircleGeometry(.75,48),new THREE.MeshBasicMaterial({color:0x54efba,transparent:true,opacity:.16,side:THREE.DoubleSide}));portal.add(portalCore);portal.position.z=0;world.add(portal);
// Side lights deepen the level while keeping the course legible.
for(let i=0;i<9;i++){const lamp=new THREE.PointLight(i%2?0x91a8ff:0x80ffd1,4,6);lamp.position.set(-14+i*3.6,(i%2?1:-1)*4.4,-1);scene.add(lamp);}
let toastTimer=0;
function toast(text){const el=document.querySelector('#toast');el.textContent=text;el.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('show'),1450);}
function setGravity(next){if(gameState!=='playing'||next===gravity)return;gravity=next;grounded=false;vy=gravity*-.85;player.rotation.z=Math.PI;document.querySelector('#gravity-state').textContent=gravity===1?'DOWN':'UP';const fill=document.querySelector('#gravity-fill');fill.style.top=gravity===1?'1px':'50%';fill.style.height='48%';toast(gravity===-1?'GRAVITY REVERSED':'GRAVITY RESTORED');}
function flip(){if(grounded||flipCooldown<=0){setGravity(-gravity);flipCooldown=.24;}}
function start(){gameState='playing';document.querySelector('#start-screen').classList.add('hidden');elapsed=0;}
function restart(){x=checkpoint;y=-2.8;vy=0;gravity=1;grounded=true;flipCooldown=0;player.position.set(x,y,0);player.rotation.z=0;shards=0;collected.clear();shardsMeshes.forEach(s=>s.visible=true);document.querySelector('#shard-count').textContent='00';document.querySelector('#gravity-state').textContent='DOWN';document.querySelector('#gravity-fill').style.top='1px';document.querySelector('#win-screen').classList.add('hidden');document.querySelector('#pause-screen').classList.add('hidden');gameState='playing';elapsed=0;}
function collect(){for(let i=0;i<shardsMeshes.length;i++){if(collected.has(i))continue;const [sx,sy]=shardPositions[i];if(Math.hypot(x-sx,y-sy)<.77){collected.add(i);shards++;shardsMeshes[i].visible=false;document.querySelector('#shard-count').textContent=String(shards).padStart(2,'0');toast(shards===5?'ALL FIVE SHARDS — FIND THE EXIT':'SHARD RECOVERED');if(x>8)checkpoint=9;}}}
function die(){x=checkpoint;y=gravity===1?-2.8:2.8;vy=0;toast('SIGNAL LOST — BACK TO CHECKPOINT');}
function collidePlatforms(prevY,nextY){const surfaces=[[-3.3,3.3],[-2.225,4,1.05],[-1.095,8,1.1],[-1.925,11.7,1.2],[2.475,-2,1.1],[1.375,2,1.15],[2.375,6,1.05],[1.325,10,1.1]];grounded=false;for(const [sy,sx,half] of surfaces){if(Math.abs(x-sx)>half+.28)continue;if(gravity===1&&vy<0&&prevY-.34>=sy-.14&&nextY-.34<=sy+.14){y=sy+.34;vy=0;grounded=true;break;}if(gravity===-1&&vy>0&&prevY+.34<=sy+.14&&nextY+.34>=sy-.14){y=sy-.34;vy=0;grounded=true;break;}}}
function moveX(dx){const next=x+dx;const obstacleYs=[0,0];if(next>5.4&&next<6.6&&y>-1.25&&y<1.25)return;if(next>11.4&&next<12.6&&y>-.9&&y<.9)return;x=THREE.MathUtils.clamp(next,-15.4,15.4);}
let last=performance.now();
function animate(now){requestAnimationFrame(animate);const dt=Math.min((now-last)/1000,.033);last=now;if(gameState==='playing'){elapsed+=dt;flipCooldown=Math.max(0,flipCooldown-dt);const dir=(keys.has('KeyD')||keys.has('ArrowRight')?1:0)-(keys.has('KeyA')||keys.has('ArrowLeft')?1:0);moveX(dir*6.1*dt);if(grounded&&(keys.has('Space')||keys.has('ArrowUp')||keys.has('KeyW'))){vy=gravity*8.3;grounded=false;}const prevY=y;vy-=gravity*18*dt;vy=THREE.MathUtils.clamp(vy,-10,10);y+=vy*dt;collidePlatforms(prevY,y);if(Math.abs(y)>5.2){die();}player.position.set(x,y,0);player.rotation.z=THREE.MathUtils.damp(player.rotation.z,gravity===1?0:Math.PI,dt*9);player.rotation.y=THREE.MathUtils.damp(player.rotation.y,dir*.12,dt*6);collect();if(x>13.7&&shards===5){gameState='won';document.querySelector('#win-shards').textContent=`${String(shards).padStart(2,'0')} / 05`;const sec=Math.floor(elapsed);document.querySelector('#win-time').textContent=`${String(Math.floor(sec/60)).padStart(2,'0')}:${String(sec%60).padStart(2,'0')}`;document.querySelector('#win-screen').classList.remove('hidden');}}
shardsMeshes.forEach((s,i)=>{if(s.visible){s.rotation.y+=dt*1.1;s.rotation.z+=dt*.55;s.position.y=shardPositions[i][1]+Math.sin(now*.0018+i)*.08;}});portalRing.rotation.z+=dt*.35;portalCore.material.opacity=.1+Math.sin(now*.003)*.07;
const target=new THREE.Vector3(x*.67,THREE.MathUtils.clamp(y*.26,-.6,.6),0);camera.position.x=THREE.MathUtils.damp(camera.position.x,target.x,dt*2.7);camera.position.y=THREE.MathUtils.damp(camera.position.y,5.4+target.y,dt*2.4);camera.lookAt(camera.position.x*.18,0,-1.5);renderer.render(scene,camera);}
requestAnimationFrame(animate);
addEventListener('keydown',e=>{if(['Space','ArrowUp','ArrowLeft','ArrowRight'].includes(e.code))e.preventDefault();if(e.repeat)return;keys.add(e.code);if(e.code==='KeyQ'||e.code==='ShiftLeft'||e.code==='ShiftRight')flip();if(e.code==='KeyR'&&gameState!=='intro')restart();if(e.code==='Escape'){if(gameState==='playing'){gameState='paused';document.querySelector('#pause-screen').classList.remove('hidden');}else if(gameState==='paused'){gameState='playing';document.querySelector('#pause-screen').classList.add('hidden');}}});addEventListener('keyup',e=>keys.delete(e.code));
document.querySelector('#start-btn').addEventListener('click',start);document.querySelector('#restart-btn').addEventListener('click',restart);document.querySelector('#play-again-btn').addEventListener('click',restart);document.querySelector('#resume-btn').addEventListener('click',()=>{gameState='playing';document.querySelector('#pause-screen').classList.add('hidden');});document.querySelector('#sound-btn').addEventListener('click',e=>{e.currentTarget.classList.toggle('muted');toast(e.currentTarget.classList.contains('muted')?'SOUND OFF':'SOUND ON');});
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
