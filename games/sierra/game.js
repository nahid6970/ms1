const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

canvas.width = 1200;
canvas.height = 600;

const GAME = {
    running: false, // Start false for menu
    paused: true,
    gravity: 0.5,
    cameraX: 0,
    player: null,
    enemies: [],
    bullets: [],
    walls: [],
    particles: [],
    missionComplete: false,
    death: false,
    editorMode: false,
    editorItem: 'WALL',
    editorClass: 'ASSAULT'
};

const keys = {};
let mouse = { x: 0, y: 0, pressed: false };

window.addEventListener('keydown', e => keys[e.code] = true);
window.addEventListener('keyup', e => keys[e.code] = false);
window.addEventListener('mousemove', e => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
});
window.addEventListener('mousedown', () => mouse.pressed = true);
window.addEventListener('mouseup', () => mouse.pressed = false);

const WEAPONS = {
    SNIPER_RIFLE: { name: 'M24 SNIPER', fireRate: 1500, ammo: 5, magSize: 5, totalAmmo: 20, damage: 100, reloadTime: 2500, recoil: 0.5, spread: 0.005 },
    ASSAULT_RIFLE: { name: 'HK416 ASSAULT', fireRate: 150, ammo: 30, magSize: 30, totalAmmo: 120, damage: 20, reloadTime: 1800, recoil: 0.08, spread: 0.04 },
    SMG: { name: 'MP7 MERCENARY', fireRate: 80, ammo: 40, magSize: 40, totalAmmo: 160, damage: 12, reloadTime: 1200, recoil: 0.05, spread: 0.1 },
    LMG: { name: 'M249 HEAVY', fireRate: 60, ammo: 100, magSize: 100, totalAmmo: 200, damage: 18, reloadTime: 4000, recoil: 0.12, spread: 0.15 }
};

const CLASSES = {
    SNIPER: { weapon: WEAPONS.SNIPER_RIFLE, health: 80, speed: 3.5, color: '#3e4a3e' },
    ASSAULT: { weapon: WEAPONS.ASSAULT_RIFLE, health: 100, speed: 4.5, color: '#2c3e50' },
    MERCENARY: { weapon: WEAPONS.SMG, health: 90, speed: 5.5, color: '#7f8c8d' },
    HEAVY: { weapon: WEAPONS.LMG, health: 150, speed: 2.5, color: '#444' }
};

const DEFAULT_MAPS = {
    "1: CQB TRAINING": {
        walls: [
            { x: -100, y: 550, w: 2000, h: 100, health: 1000, destructible: false },
            { x: 300, y: 350, w: 20, h: 200, health: 1000, destructible: false },
            { x: 600, y: 350, w: 20, h: 200, health: 1000, destructible: false },
            { x: 300, y: 350, w: 320, h: 20, health: 1000, destructible: false },
            { x: 450, y: 480, w: 50, h: 70, health: 60, destructible: true }
        ],
        enemies: [{ x: 500, y: 450, className: 'ASSAULT' }, { x: 350, y: 450, className: 'ASSAULT' }]
    },
    "2: WAREHOUSE ASSAULT": {
        walls: [
            { x: -100, y: 550, w: 3000, h: 100, health: 1000, destructible: false },
            { x: 500, y: 480, w: 50, h: 70, health: 60, destructible: true },
            { x: 550, y: 480, w: 50, h: 70, health: 60, destructible: true },
            { x: 525, y: 410, w: 50, h: 70, health: 60, destructible: true },
            { x: 1000, y: 480, w: 50, h: 70, health: 60, destructible: true },
            { x: 1050, y: 480, w: 50, h: 70, health: 60, destructible: true },
            { x: 1400, y: 350, w: 400, h: 30, health: 1000, destructible: false }
        ],
        enemies: [
            { x: 600, y: 500, className: 'MERCENARY' },
            { x: 1100, y: 500, className: 'MERCENARY' },
            { x: 1500, y: 300, className: 'ASSAULT' },
            { x: 2000, y: 500, className: 'HEAVY' }
        ]
    },
    "3: SNIPER'S NEST": {
        walls: [
            { x: -100, y: 550, w: 4000, h: 100, health: 1000, destructible: false },
            { x: 400, y: 350, w: 200, h: 20, health: 1000, destructible: false },
            { x: 800, y: 250, w: 200, h: 20, health: 1000, destructible: false },
            { x: 1200, y: 150, w: 200, h: 20, health: 1000, destructible: false },
            { x: 1600, y: 250, w: 200, h: 20, health: 1000, destructible: false }
        ],
        enemies: [
            { x: 450, y: 300, className: 'SNIPER' },
            { x: 850, y: 200, className: 'SNIPER' },
            { x: 1250, y: 100, className: 'SNIPER' },
            { x: 1650, y: 200, className: 'SNIPER' }
        ]
    },
    "4: THE HEAVY BUNKER": {
        walls: [
            { x: -100, y: 550, w: 3000, h: 100, health: 1000, destructible: false },
            { x: 0, y: 100, w: 4000, h: 20, health: 1000, destructible: false }, // Low ceiling
            { x: 500, y: 300, w: 20, h: 250, health: 1000, destructible: false },
            { x: 1000, y: 120, w: 20, h: 250, health: 1000, destructible: false },
            { x: 1500, y: 300, w: 20, h: 250, health: 1000, destructible: false },
            { x: 2000, y: 120, w: 20, h: 430, health: 1000, destructible: false } // Exit gate
        ],
        enemies: [
            { x: 700, y: 500, className: 'HEAVY' },
            { x: 1200, y: 300, className: 'HEAVY' },
            { x: 1800, y: 500, className: 'ASSAULT' }
        ]
    },
    "5: COMPOUND BREACH": {
        walls: [
            { x: -100, y: 550, w: 4000, h: 100, health: 1000, destructible: false },
            { x: 400, y: 400, w: 600, h: 20, health: 200, destructible: true },
            { x: 1200, y: 400, w: 600, h: 20, health: 200, destructible: true },
            { x: 800, y: 200, w: 400, h: 20, health: 200, destructible: true },
            { x: 500, y: 480, w: 50, h: 70, health: 1000, destructible: false }
        ],
        enemies: [
            { x: 500, y: 350, className: 'ASSAULT' },
            { x: 900, y: 350, className: 'MERCENARY' },
            { x: 1000, y: 150, className: 'SNIPER' },
            { x: 1500, y: 500, className: 'HEAVY' },
            { x: 2500, y: 500, className: 'ASSAULT' }
        ]
    }
};

// UI & Map Logic
const UI = {
    showMainMenu: () => {
        GAME.paused = true;
        GAME.running = false;
        document.getElementById('main-menu').classList.remove('hidden');
        document.getElementById('map-list-screen').classList.add('hidden');
    },
    showMapList: () => {
        document.getElementById('main-menu').classList.add('hidden');
        document.getElementById('map-list-screen').classList.remove('hidden');
        UI.renderMapList();
    },
    renderMapList: () => {
        const container = document.getElementById('map-items');
        container.innerHTML = '';

        // Built-in Maps
        Object.keys(DEFAULT_MAPS).forEach(name => {
            const item = document.createElement('div');
            item.className = 'map-item default-map';
            item.innerHTML = `<span style="color: #666;">[HQ]</span> ${name}`;
            item.onclick = () => UI.loadMap(DEFAULT_MAPS[name]);
            container.appendChild(item);
        });

        // Custom User Maps
        const maps = JSON.parse(localStorage.getItem('sierra_maps') || '{}');
        Object.keys(maps).forEach(name => {
            const item = document.createElement('div');
            item.className = 'map-item';
            item.innerHTML = `<span style="color: #900;">[USER]</span> ${name}`;
            item.onclick = () => UI.loadMap(maps[name]);
            container.appendChild(item);
        });
    },
    loadMap: (mapData) => {
        document.getElementById('map-list-screen').classList.add('hidden');
        initLevel(mapData);
        GAME.paused = false;
        GAME.running = true;
    },
    startEditor: () => {
        document.getElementById('main-menu').classList.add('hidden');
        document.getElementById('hud').classList.add('hidden');
        document.getElementById('editor-ui').classList.remove('hidden');
        GAME.editorMode = true;
        GAME.running = true;
        GAME.paused = false;
        initLevel(null); // start fresh
    },
    resume: () => {
        if (GAME.player) {
            document.getElementById('main-menu').classList.add('hidden');
            GAME.paused = false;
        }
    },
    openSaveDialog: () => {
        document.getElementById('save-map-dialog').classList.remove('hidden');
    },
    closeSaveDialog: () => {
        document.getElementById('save-map-dialog').classList.add('hidden');
    },
    saveCustomMap: () => {
        const name = document.getElementById('map-name-input').value.trim();
        if (!name) return alert("Enter sector name!");
        const maps = JSON.parse(localStorage.getItem('sierra_maps') || '{}');
        maps[name] = {
            walls: GAME.walls,
            enemies: GAME.enemies.map(e => ({ x: e.x, y: e.y, className: e.className }))
        };
        localStorage.setItem('sierra_maps', JSON.stringify(maps));
        UI.closeSaveDialog();
        alert("Sector committed to database.");
    }
};

class Particle {
    constructor(x, y, color) {
        this.x = x; this.y = y;
        this.vx = (Math.random() - 0.5) * 4;
        this.vy = (Math.random() - 0.5) * 4;
        this.life = 1.0; this.color = color;
    }
    update() { this.x += this.vx; this.y += this.vy; this.life -= 0.05; }
    draw() {
        ctx.globalAlpha = this.life;
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, 2, 2);
        ctx.globalAlpha = 1;
    }
}

class Bullet {
    constructor(x, y, angle, owner, damage) {
        this.x = x; this.y = y;
        this.vx = Math.cos(angle) * 20;
        this.vy = Math.sin(angle) * 20;
        this.owner = owner; this.damage = damage;
        this.active = true;
    }
    update() {
        this.x += this.vx; this.y += this.vy;
        GAME.walls.forEach(wall => {
            if (this.x > wall.x && this.x < wall.x + wall.w && this.y > wall.y && this.y < wall.y + wall.h) {
                this.active = false;
                if (wall.destructible) {
                    wall.health -= this.damage;
                    for (let i = 0; i < 3; i++) GAME.particles.push(new Particle(this.x, this.y, '#444'));
                } else {
                    for (let i = 0; i < 5; i++) GAME.particles.push(new Particle(this.x, this.y, '#666'));
                }
            }
        });
        if (this.x < -1000 || this.x > 4000 || this.y < -1000 || this.y > 1000) this.active = false;
    }
    draw() {
        ctx.strokeStyle = '#ff0'; ctx.lineWidth = 2; ctx.beginPath();
        ctx.moveTo(this.x - GAME.cameraX, this.y);
        ctx.lineTo(this.x - GAME.cameraX - this.vx * 0.5, this.y - this.vy * 0.5);
        ctx.stroke();
    }
}

class Player {
    constructor(x, y, className) {
        this.className = className;
        const config = CLASSES[this.className];
        this.x = x; this.y = y; this.w = 20; this.h = 50;
        this.vx = 0; this.vy = 0;
        this.maxHealth = config.health; this.health = config.health;
        this.weapon = { ...config.weapon }; this.ammo = this.weapon.ammo;
        this.speed = config.speed; this.color = config.color;
        this.lastFired = 0; this.reloading = false; this.crouching = false;
        this.facing = 1; this.grounded = false; this.jumpPower = -12;
    }
    update() {
        if (GAME.death || GAME.editorMode || GAME.paused) return;
        let speed = this.speed;
        if (keys['KeyA']) { this.vx = -speed; this.facing = -1; }
        else if (keys['KeyD']) { this.vx = speed; this.facing = 1; }
        else { this.vx *= 0.8; }
        this.crouching = keys['ControlLeft'] || keys['KeyC'];
        this.h = this.crouching ? 30 : 50;
        if (this.crouching) this.vx *= 0.5;
        this.vy += GAME.gravity; this.y += this.vy;
        this.grounded = false;
        GAME.walls.forEach(wall => {
            if (this.x < wall.x + wall.w && this.x + this.w > wall.x && this.y < wall.y + wall.h && this.y + this.h > wall.y) {
                if (this.vy > 0) { this.y = wall.y - this.h; this.vy = 0; this.grounded = true; }
                else if (this.vy < 0) { this.y = wall.y + wall.h; this.vy = 0; }
            }
        });
        if ((keys['Space'] || keys['KeyW']) && this.grounded && !this.crouching) { this.vy = this.jumpPower; this.grounded = false; }
        this.x += this.vx;
        GAME.walls.forEach(wall => {
            if (this.x < wall.x + wall.w && this.x + this.w > wall.x && this.y < wall.y + wall.h && this.y + this.h > wall.y) {
                if (this.vx > 0) this.x = wall.x - this.w;
                if (this.vx < 0) this.x = wall.x + wall.w;
            }
        });
        if (keys['Digit1']) GAME.player = new Player(this.x, this.y, 'SNIPER');
        if (keys['Digit2']) GAME.player = new Player(this.x, this.y, 'ASSAULT');
        if (keys['Digit3']) GAME.player = new Player(this.x, this.y, 'MERCENARY');
        if (keys['Digit4']) GAME.player = new Player(this.x, this.y, 'HEAVY');
        if (mouse.pressed && !this.reloading && this.ammo > 0) {
            let now = Date.now();
            if (now - this.lastFired > this.weapon.fireRate) { this.shoot(); this.lastFired = now; }
        }
        if (keys['KeyR'] && !this.reloading && this.ammo < this.weapon.magSize) { this.reload(); }

        const hud = document.getElementById('hud');
        if (GAME.editorMode) hud.classList.add('hidden');
        else hud.classList.remove('hidden');

        document.getElementById('ammo-count').innerText = `${this.ammo} / ${this.weapon.totalAmmo}`;
        document.getElementById('weapon-name').innerText = `${this.className}: ${this.weapon.name}`;
        GAME.cameraX = this.x - 400;
        if (GAME.cameraX < 0) GAME.cameraX = 0;
    }
    shoot() {
        let dx = (mouse.x + GAME.cameraX) - (this.x + this.w / 2);
        let dy = mouse.y - (this.y + 15);
        let angle = Math.atan2(dy, dx);
        angle += (Math.random() - 0.5) * this.weapon.spread;
        GAME.bullets.push(new Bullet(this.x + this.w / 2, this.y + 15, angle, 'player', this.weapon.damage));
        this.ammo--; this.y -= 2;
        for (let i = 0; i < 3; i++) GAME.particles.push(new Particle(this.x + this.w / 2, this.y + 15, '#aaaaaa'));
    }
    reload() {
        this.reloading = true;
        setTimeout(() => { this.ammo = this.weapon.magSize; this.reloading = false; }, this.weapon.reloadTime);
    }
    draw() {
        ctx.fillStyle = this.color; ctx.fillRect(this.x - GAME.cameraX, this.y, this.w, this.h);
        ctx.fillStyle = '#111'; ctx.fillRect(this.x - GAME.cameraX, this.y, this.w, 10);
        ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.fillRect(this.x - GAME.cameraX, this.y + 15, this.w, 20);
        let dx = (mouse.x + GAME.cameraX) - (this.x + this.w / 2);
        let dy = mouse.y - (this.y + 15);
        let angle = Math.atan2(dy, dx);
        if (this.className === 'SNIPER') {
            let laserX = this.x + this.w / 2, laserY = this.y + 18, targetX = laserX + Math.cos(angle) * 1000, targetY = laserY + Math.sin(angle) * 1000;
            GAME.walls.forEach(wall => {
                for (let d = 0; d < 1000; d += 15) {
                    let px = laserX + Math.cos(angle) * d, py = laserY + Math.sin(angle) * d;
                    if (px > wall.x && px < wall.x + wall.w && py > wall.y && py < wall.y + wall.h) { targetX = px; targetY = py; break; }
                }
            });
            ctx.strokeStyle = 'rgba(255, 0, 0, 0.4)'; ctx.lineWidth = 1; ctx.setLineDash([5, 5]); ctx.beginPath();
            ctx.moveTo(laserX - GAME.cameraX, laserY); ctx.lineTo(targetX - GAME.cameraX, targetY); ctx.stroke(); ctx.setLineDash([]);
        }
        ctx.save(); ctx.translate(this.x + this.w / 2 - GAME.cameraX, this.y + 20); ctx.rotate(angle); ctx.fillStyle = '#000'; ctx.fillRect(0, -2, 18, 4); ctx.restore();
    }
}

class Enemy {
    constructor(x, y, className = 'ASSAULT') {
        this.className = className; const config = CLASSES[className];
        this.x = x; this.y = y; this.w = 20; this.h = 50;
        this.maxHealth = config.health * 0.6; this.health = this.maxHealth;
        this.weapon = { ...config.weapon }; this.state = 'PATROL';
        this.patrolStart = x; this.patrolEnd = x + 150; this.dir = 1;
        this.lastShot = 0; this.alertTimer = 0;
        this.vx = 0; this.vy = 0; this.grounded = false;
    }
    update() {
        if (this.health <= 0 || GAME.paused || GAME.editorMode) return;

        // Gravity and Physics for Enemy
        this.vy += GAME.gravity;
        this.y += this.vy;
        this.grounded = false;
        GAME.walls.forEach(wall => {
            if (this.x < wall.x + wall.w && this.x + this.w > wall.x && this.y < wall.y + wall.h && this.y + this.h > wall.y) {
                if (this.vy > 0) { this.y = wall.y - this.h; this.vy = 0; this.grounded = true; }
                else if (this.vy < 0) { this.y = wall.y + wall.h; this.vy = 0; }
            }
        });

        let dist = Math.abs(this.x - GAME.player.x);
        if (dist < 400 && Math.abs(this.y - GAME.player.y) < 200) this.state = 'COMBAT';
        else if (this.state === 'COMBAT') { this.state = 'ALERT'; this.alertTimer = 180; }

        if (this.state === 'PATROL') {
            // Patrol movement
            let nextX = this.x + this.dir * 1;

            // Check for wall or ledge
            let hasFloor = false;
            GAME.walls.forEach(wall => {
                if (nextX + this.w / 2 > wall.x && nextX + this.w / 2 < wall.x + wall.w && this.y + this.h + 5 > wall.y && this.y + this.h + 5 < wall.y + wall.h) {
                    hasFloor = true;
                }
            });

            if (nextX > this.patrolEnd || nextX < this.patrolStart || !hasFloor) {
                this.dir *= -1;
            } else {
                this.x = nextX;
            }
        } else if (this.state === 'COMBAT') {
            this.dir = GAME.player.x > this.x ? 1 : -1;
            let now = Date.now();
            if (now - this.lastShot > this.weapon.fireRate * 2) { this.shoot(); this.lastShot = now; }
        } else if (this.state === 'ALERT') { if (--this.alertTimer <= 0) this.state = 'PATROL'; }

        // Wall collision for side movement
        GAME.walls.forEach(wall => {
            if (this.x < wall.x + wall.w && this.x + this.w > wall.x && this.y < wall.y + wall.h && this.y + this.h > wall.y) {
                if (this.dir > 0) this.x = wall.x - this.w;
                else if (this.dir < 0) this.x = wall.x + wall.w;
                this.dir *= -1; // Bounce
            }
        });

        GAME.bullets.forEach(b => {
            if (b.owner === 'player' && b.active && b.x > this.x && b.x < this.x + this.w && b.y > this.y && b.y < this.y + this.h) {
                this.health -= (b.y < this.y + 15) ? b.damage * 2 : b.damage;
                b.active = false;
                for (let i = 0; i < 8; i++) GAME.particles.push(new Particle(b.x, b.y, '#900'));
            }
        });
    }
    shoot() {
        let dx = GAME.player.x - this.x, dy = (GAME.player.y + 20) - (this.y + 15);
        let angle = Math.atan2(dy, dx);
        GAME.bullets.push(new Bullet(this.x + this.w / 2, this.y + 15, angle, 'enemy', 10));
    }
    draw() {
        if (this.health <= 0) { ctx.fillStyle = '#200'; ctx.fillRect(this.x - GAME.cameraX, this.y + this.h - 10, this.w + 10, 10); return; }
        ctx.fillStyle = '#300'; ctx.fillRect(this.x - GAME.cameraX, this.y, this.w, this.h);
        ctx.fillStyle = '#100'; ctx.fillRect(this.x - GAME.cameraX, this.y, this.w, 10);
        ctx.fillStyle = 'rgba(0,0,0,0.4)'; ctx.fillRect(this.x - GAME.cameraX, this.y + 15, this.w, 20);
        let dx = GAME.player.x - this.x, dy = (GAME.player.y + 20) - (this.y + 15), angle = Math.atan2(dy, dx);

        if (!GAME.editorMode) {
            if (this.className === 'SNIPER') {
                ctx.strokeStyle = 'rgba(255, 0, 0, 0.3)'; ctx.lineWidth = 1; ctx.beginPath();
                ctx.moveTo(this.x + this.w / 2 - GAME.cameraX, this.y + 18);
                ctx.lineTo(this.x + this.w / 2 - GAME.cameraX + Math.cos(angle) * 800, this.y + 18 + Math.sin(angle) * 800);
                ctx.stroke();
            }
            ctx.save(); ctx.translate(this.x + this.w / 2 - GAME.cameraX, this.y + 20); ctx.rotate(angle); ctx.fillStyle = '#000'; ctx.fillRect(0, -2, 14, 3); ctx.restore();
            if (this.state === 'COMBAT') { ctx.fillStyle = '#f00'; ctx.font = 'bold 16px Courier New'; ctx.fillText('!', this.x + this.w / 2 - GAME.cameraX - 4, this.y - 10); }
        } else {
            // Distinct "Editor Icon" for enemies
            ctx.fillStyle = '#f00';
            ctx.font = 'bold 12px Courier New';
            ctx.fillText(this.className[0], this.x + this.w / 2 - GAME.cameraX - 4, this.y + 30);
        }
    }
}

function initLevel(mapData) {
    GAME.bullets = []; GAME.particles = []; GAME.death = false; GAME.missionComplete = false;
    if (mapData) {
        GAME.walls = mapData.walls;
        GAME.enemies = mapData.enemies.map(e => new Enemy(e.x, e.y, e.className));
    } else {
        GAME.walls = [
            { x: -100, y: 550, w: 4000, h: 100, health: 1000, destructible: false },
            { x: -100, y: 0, w: 100, h: 600, health: 1000, destructible: false },
            { x: 3000, y: 0, w: 100, h: 600, health: 1000, destructible: false },
            { x: 400, y: 400, w: 200, h: 20, health: 100, destructible: true },
            { x: 600, y: 400, w: 20, h: 150, health: 150, destructible: true }
        ];
        GAME.enemies = [new Enemy(500, 340, 'SNIPER'), new Enemy(900, 490, 'HEAVY')];
    }
    GAME.player = new Player(50, 480, 'ASSAULT');
}

window.addEventListener('keydown', e => {
    if (e.code === 'Escape') {
        if (GAME.editorMode) {
            GAME.editorMode = false;
            document.getElementById('editor-ui').classList.add('hidden');
            UI.showMainMenu();
        }
        else { GAME.paused = !GAME.paused; document.getElementById('main-menu').classList.toggle('hidden', !GAME.paused); }
    }
    if (e.code === 'Tab') {
        e.preventDefault();
        GAME.editorMode = !GAME.editorMode;
        document.getElementById('hud').classList.toggle('hidden', GAME.editorMode);
        document.getElementById('editor-ui').classList.toggle('hidden', !GAME.editorMode);
        document.body.style.cursor = GAME.editorMode ? 'crosshair' : 'default';
    }
    if (GAME.editorMode) {
        if (e.code === 'KeyZ') GAME.editorItem = 'WALL';
        if (e.code === 'KeyX') GAME.editorItem = 'COVER';
        if (e.code === 'KeyC') GAME.editorItem = 'ENEMY';
        if (e.code === 'Digit1') GAME.editorClass = 'SNIPER';
        if (e.code === 'Digit2') GAME.editorClass = 'ASSAULT';
        if (e.code === 'Digit3') GAME.editorClass = 'MERCENARY';
        if (e.code === 'Digit4') GAME.editorClass = 'HEAVY';
        if (e.code === 'KeyS') UI.openSaveDialog();
        if (e.code === 'Delete') { GAME.walls = []; GAME.enemies = []; }
    }
});

canvas.addEventListener('mousedown', e => {
    if (!GAME.editorMode) return;
    const rect = canvas.getBoundingClientRect();
    const ex = Math.floor((e.clientX - rect.left + GAME.cameraX) / 50) * 50;
    const ey = Math.floor((e.clientY - rect.top) / 50) * 50;
    if (GAME.editorItem === 'WALL') GAME.walls.push({ x: ex, y: ey, w: 50, h: 50, health: 1000, destructible: false });
    else if (GAME.editorItem === 'COVER') GAME.walls.push({ x: ex, y: ey, w: 50, h: 50, health: 100, destructible: true });
    else if (GAME.editorItem === 'ENEMY') GAME.enemies.push(new Enemy(ex + 15, ey, GAME.editorClass));
});

function update() {
    if (!GAME.running) return;

    if (GAME.editorMode) {
        if (keys['KeyA']) GAME.cameraX -= 15;
        if (keys['KeyD']) GAME.cameraX += 15;
        if (GAME.cameraX < 0) GAME.cameraX = 0;
        if (GAME.cameraX > 2000) GAME.cameraX = 2000;
        return; // Don't run game logic in editor
    }

    if (GAME.paused) return;

    GAME.player.update();
    GAME.bullets.forEach(b => {
        if (b.owner === 'enemy' && b.active && b.x > GAME.player.x && b.x < GAME.player.x + GAME.player.w && b.y > GAME.player.y && b.y < GAME.player.y + GAME.player.h) {
            GAME.player.health -= b.damage; b.active = false;
            for (let i = 0; i < 5; i++) GAME.particles.push(new Particle(b.x, b.y, '#f00'));
        }
    });
    if (GAME.player.health <= 0) { GAME.death = true; document.getElementById('death-screen').classList.remove('hidden'); }
    GAME.enemies.forEach(e => e.update());
    GAME.bullets.forEach(b => b.update());
    GAME.bullets = GAME.bullets.filter(b => b.active);
    GAME.walls = GAME.walls.filter(w => !w.destructible || w.health > 0);
    GAME.particles.forEach(p => p.update());
    GAME.particles = GAME.particles.filter(p => p.life > 0);
    if (GAME.enemies.length > 0 && GAME.enemies.every(e => e.health <= 0)) {
        GAME.missionComplete = true; document.getElementById('win-screen').classList.remove('hidden');
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#1a1a1a'; ctx.lineWidth = 1;
    for (let x = -GAME.cameraX % 50; x < canvas.width; x += 50) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke(); }
    GAME.walls.forEach(wall => {
        ctx.fillStyle = (wall.destructible && wall.health < 50) ? '#1a1a1a' : '#222';
        ctx.fillRect(wall.x - GAME.cameraX, wall.y, wall.w, wall.h);
        ctx.strokeStyle = wall.destructible ? '#444' : '#333'; ctx.strokeRect(wall.x - GAME.cameraX, wall.y, wall.w, wall.h);
    });
    GAME.enemies.forEach(e => e.draw());
    if (GAME.player && !GAME.editorMode) GAME.player.draw();
    GAME.bullets.forEach(b => b.draw());
    GAME.particles.forEach(p => p.draw());

    if (GAME.editorMode) {
        // Update Editor UI Text
        document.getElementById('ed-item').innerText = GAME.editorItem;
        document.getElementById('ed-class').innerText = GAME.editorClass;

        // Ghost placement
        const gx = Math.floor((mouse.x + GAME.cameraX) / 50) * 50;
        const gy = Math.floor(mouse.y / 50) * 50;
        ctx.strokeStyle = '#fff';
        ctx.strokeRect(gx - GAME.cameraX, gy, 50, 50);
    } else if (GAME.player) {
        ctx.fillStyle = '#300'; ctx.fillRect(20, 560, 200, 20);
        ctx.fillStyle = '#f00'; ctx.fillRect(20, 560, (GAME.player.health / GAME.player.maxHealth) * 200, 20);
    }
}

function loop() { update(); draw(); requestAnimationFrame(loop); }
UI.showMainMenu();
loop();
