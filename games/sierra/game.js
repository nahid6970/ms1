const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Set canvas size
canvas.width = 1200;
canvas.height = 600;

// Game State
const GAME = {
    running: true,
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
    editorItem: 'WALL', // WALL, COVER, ENEMY
    editorClass: 'ASSAULT'
};

// Input
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

// Weapons & Classes
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

const EDITOR_CONFIG = {
    gridSize: 50
};

class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 4;
        this.vy = (Math.random() - 0.5) * 4;
        this.life = 1.0;
        this.color = color;
    }
    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life -= 0.05;
    }
    draw() {
        ctx.globalAlpha = this.life;
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, 2, 2);
        ctx.globalAlpha = 1;
    }
}

class Bullet {
    constructor(x, y, angle, owner, damage) {
        this.x = x;
        this.y = y;
        this.vx = Math.cos(angle) * 20;
        this.vy = Math.sin(angle) * 20;
        this.owner = owner;
        this.damage = damage;
        this.active = true;
    }
    update() {
        this.x += this.vx;
        this.y += this.vy;

        // Wall collision
        GAME.walls.forEach(wall => {
            if (this.x > wall.x && this.x < wall.x + wall.w &&
                this.y > wall.y && this.y < wall.y + wall.h) {
                this.active = false;

                if (wall.destructible) {
                    wall.health -= this.damage;
                    for (let i = 0; i < 3; i++) GAME.particles.push(new Particle(this.x, this.y, '#444'));
                } else {
                    for (let i = 0; i < 5; i++) GAME.particles.push(new Particle(this.x, this.y, '#666'));
                }
            }
        });

        if (this.x < 0 || this.x > 3000 || this.y < 0 || this.y > 600) this.active = false;
    }
    draw() {
        ctx.strokeStyle = '#ff0';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(this.x - GAME.cameraX, this.y);
        ctx.lineTo(this.x - GAME.cameraX - this.vx * 0.5, this.y - this.vy * 0.5);
        ctx.stroke();
    }
}

class Player {
    constructor(x, y, className) {
        this.className = className;
        const config = CLASSES[this.className];
        this.x = x;
        this.y = y;
        this.w = 20;
        this.h = 50;
        this.vx = 0;
        this.vy = 0;
        this.maxHealth = config.health;
        this.health = config.health;
        this.weapon = { ...config.weapon };
        this.ammo = this.weapon.ammo;
        this.speed = config.speed;
        this.color = config.color;
        this.lastFired = 0;
        this.reloading = false;
        this.crouching = false;
        this.facing = 1;
        this.grounded = false;
        this.jumpPower = -12;
    }

    update() {
        if (GAME.death || GAME.editorMode) return;

        let speed = this.speed;
        if (keys['KeyA']) {
            this.vx = -speed;
            this.facing = -1;
        } else if (keys['KeyD']) {
            this.vx = speed;
            this.facing = 1;
        } else {
            this.vx *= 0.8;
        }

        this.crouching = keys['ControlLeft'] || keys['KeyC'];
        if (this.crouching) {
            this.vx *= 0.5;
            this.h = 30;
        } else {
            this.h = 50;
        }

        this.vy += GAME.gravity;
        this.y += this.vy;

        this.grounded = false;
        GAME.walls.forEach(wall => {
            if (this.x < wall.x + wall.w && this.x + this.w > wall.x &&
                this.y < wall.y + wall.h && this.y + this.h > wall.y) {
                if (this.vy > 0) {
                    this.y = wall.y - this.h;
                    this.vy = 0;
                    this.grounded = true;
                } else if (this.vy < 0) {
                    this.y = wall.y + wall.h;
                    this.vy = 0;
                }
            }
        });

        if ((keys['Space'] || keys['KeyW']) && this.grounded && !this.crouching) {
            this.vy = this.jumpPower;
            this.grounded = false;
        }

        this.x += this.vx;
        GAME.walls.forEach(wall => {
            if (this.x < wall.x + wall.w && this.x + this.w > wall.x &&
                this.y < wall.y + wall.h && this.y + this.h > wall.y) {
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
            if (now - this.lastFired > this.weapon.fireRate) {
                this.shoot();
                this.lastFired = now;
            }
        }

        if (keys['KeyR'] && !this.reloading && this.ammo < this.weapon.magSize) {
            this.reload();
        }

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
        this.ammo--;
        this.y -= 2;
        for (let i = 0; i < 3; i++) GAME.particles.push(new Particle(this.x + this.w / 2, this.y + 15, '#aaaaaa'));
    }

    reload() {
        this.reloading = true;
        setTimeout(() => {
            this.ammo = this.weapon.magSize;
            this.reloading = false;
        }, this.weapon.reloadTime);
    }

    draw() {
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x - GAME.cameraX, this.y, this.w, this.h);
        ctx.fillStyle = '#111';
        ctx.fillRect(this.x - GAME.cameraX, this.y, this.w, 10);
        ctx.fillStyle = 'rgba(0,0,0,0.3)';
        ctx.fillRect(this.x - GAME.cameraX, this.y + 15, this.w, 20);        // Arm/Gun simplified
        let dx = (mouse.x + GAME.cameraX) - (this.x + this.w / 2);
        let dy = mouse.y - (this.y + 15);
        let angle = Math.atan2(dy, dx);

        // Sniper Laser Indicator
        if (this.className === 'SNIPER') {
            let laserX = this.x + this.w / 2;
            let laserY = this.y + 18;
            let targetX = laserX + Math.cos(angle) * 1000;
            let targetY = laserY + Math.sin(angle) * 1000;

            // Simple raycast to first wall
            GAME.walls.forEach(wall => {
                // Simplified line-box intersection for laser
                // Just check a few points along the line for now for performance/simplicity
                for (let d = 0; d < 1000; d += 10) {
                    let px = laserX + Math.cos(angle) * d;
                    let py = laserY + Math.sin(angle) * d;
                    if (px > wall.x && px < wall.x + wall.w && py > wall.y && py < wall.y + wall.h) {
                        targetX = px;
                        targetY = py;
                        break;
                    }
                }
            });

            ctx.strokeStyle = 'rgba(255, 0, 0, 0.4)';
            ctx.lineWidth = 1;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(laserX - GAME.cameraX, laserY);
            ctx.lineTo(targetX - GAME.cameraX, targetY);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        ctx.save();
        ctx.translate(this.x + this.w / 2 - GAME.cameraX, this.y + 20);
        ctx.rotate(angle);
        ctx.fillStyle = '#000';
        ctx.fillRect(0, -2, 18, 4);
        ctx.restore();
    }
}

class Enemy {
    constructor(x, y, className = 'ASSAULT') {
        this.className = className;
        const config = CLASSES[className];
        this.x = x;
        this.y = y;
        this.w = 20;
        this.h = 50;
        this.maxHealth = config.health * 0.6;
        this.health = this.maxHealth;
        this.weapon = { ...config.weapon };
        this.state = 'PATROL';
        this.patrolStart = x;
        this.patrolEnd = x + 150;
        this.dir = 1;
        this.lastShot = 0;
        this.alertTimer = 0;
        this.color = '#300';
    }

    update() {
        if (this.health <= 0) return;

        let dist = Math.abs(this.x - GAME.player.x);
        if (dist < 400 && Math.abs(this.y - GAME.player.y) < 150) {
            this.state = 'COMBAT';
        } else if (this.state === 'COMBAT') {
            this.state = 'ALERT';
            this.alertTimer = 180;
        }

        if (this.state === 'PATROL') {
            this.x += this.dir * 1;
            if (this.x > this.patrolEnd) this.dir = -1;
            if (this.x < this.patrolStart) this.dir = 1;
        } else if (this.state === 'COMBAT') {
            this.dir = GAME.player.x > this.x ? 1 : -1;
            let now = Date.now();
            if (now - this.lastShot > this.weapon.fireRate * 2) {
                this.shoot();
                this.lastShot = now;
            }
        } else if (this.state === 'ALERT') {
            this.alertTimer--;
            if (this.alertTimer <= 0) this.state = 'PATROL';
        }

        GAME.bullets.forEach(b => {
            if (b.owner === 'player' && b.active) {
                if (b.x > this.x && b.x < this.x + this.w &&
                    b.y > this.y && b.y < this.y + this.h) {
                    if (b.y < this.y + 15) this.health -= b.damage * 2;
                    else this.health -= b.damage;
                    b.active = false;
                    for (let i = 0; i < 8; i++) GAME.particles.push(new Particle(b.x, b.y, '#900'));
                }
            }
        });
    }

    shoot() {
        let dx = GAME.player.x - this.x;
        let dy = (GAME.player.y + 20) - (this.y + 15);
        let angle = Math.atan2(dy, dx);
        GAME.bullets.push(new Bullet(this.x + this.w / 2, this.y + 15, angle, 'enemy', 10));
    }

    draw() {
        if (this.health <= 0) {
            ctx.fillStyle = '#200';
            ctx.fillRect(this.x - GAME.cameraX, this.y + this.h - 10, this.w + 10, 10);
            return;
        }

        ctx.fillStyle = '#300';
        ctx.fillRect(this.x - GAME.cameraX, this.y, this.w, this.h);
        ctx.fillStyle = '#100';
        ctx.fillRect(this.x - GAME.cameraX, this.y, this.w, 10);
        ctx.fillStyle = 'rgba(0,0,0,0.4)';
        ctx.fillRect(this.x - GAME.cameraX, this.y + 15, this.w, 20);

        let dx = GAME.player.x - this.x;
        let dy = (GAME.player.y + 20) - (this.y + 15);
        let angle = Math.atan2(dy, dx);

        // Enemy Sniper Laser
        if (this.className === 'SNIPER') {
            let laserX = this.x + this.w / 2;
            let laserY = this.y + 18;
            let targetX = laserX + Math.cos(angle) * 800;
            let targetY = laserY + Math.sin(angle) * 800;

            ctx.strokeStyle = 'rgba(255, 0, 0, 0.3)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(laserX - GAME.cameraX, laserY);
            ctx.lineTo(targetX - GAME.cameraX, targetY);
            ctx.stroke();
        }

        ctx.save();
        ctx.translate(this.x + this.w / 2 - GAME.cameraX, this.y + 20);
        ctx.rotate(angle);
        ctx.fillStyle = '#000';
        ctx.fillRect(0, -2, 14, 3);
        ctx.restore();

        if (this.state === 'COMBAT') {
            ctx.fillStyle = '#f00';
            ctx.font = 'bold 16px Courier New';
            ctx.fillText('!', this.x + this.w / 2 - GAME.cameraX - 4, this.y - 10);
        }
    }
}

function initLevel() {
    GAME.walls = [
        { x: -100, y: 550, w: 4000, h: 100, health: 1000, destructible: false },
        { x: -100, y: 0, w: 100, h: 600, health: 1000, destructible: false },
        { x: 3000, y: 0, w: 100, h: 600, health: 1000, destructible: false },
        { x: 400, y: 400, w: 200, h: 20, health: 100, destructible: true },
        { x: 600, y: 400, w: 20, h: 150, health: 150, destructible: true },
        { x: 500, y: 480, w: 50, h: 70, health: 60, destructible: true },
        { x: 800, y: 350, w: 400, h: 20, health: 100, destructible: true },
        { x: 1200, y: 350, w: 20, h: 200, health: 150, destructible: true },
        { x: 900, y: 480, w: 60, h: 70, health: 80, destructible: true },
        { x: 1400, y: 450, w: 300, h: 100, health: 200, destructible: true },
        { x: 1800, y: 400, w: 200, h: 150, health: 200, destructible: true },
        { x: 2200, y: 450, w: 400, h: 100, health: 250, destructible: true },
    ];

    GAME.player = new Player(50, 480, 'ASSAULT');
    GAME.enemies = [
        new Enemy(500, 350, 'SNIPER'),
        new Enemy(900, 300, 'ASSAULT'),
        new Enemy(1100, 500, 'HEAVY'),
        new Enemy(1500, 400, 'MERCENARY'),
        new Enemy(2000, 400, 'ASSAULT'),
        new Enemy(2500, 500, 'HEAVY'),
        new Enemy(2800, 500, 'SNIPER')
    ];
}

// Update Input for Editor
window.addEventListener('keydown', e => {
    if (e.code === 'Tab') {
        e.preventDefault();
        GAME.editorMode = !GAME.editorMode;
        document.body.style.cursor = GAME.editorMode ? 'crosshair' : 'default';
        console.log("Editor Mode:", GAME.editorMode);
    }
    if (GAME.editorMode) {
        if (e.code === 'KeyZ') GAME.editorItem = 'WALL';
        if (e.code === 'KeyX') GAME.editorItem = 'COVER';
        if (e.code === 'KeyC') GAME.editorItem = 'ENEMY';
        if (e.code === 'Digit1') GAME.editorClass = 'SNIPER';
        if (e.code === 'Digit2') GAME.editorClass = 'ASSAULT';
        if (e.code === 'Digit3') GAME.editorClass = 'MERCENARY';
        if (e.code === 'Digit4') GAME.editorClass = 'HEAVY';
        if (e.code === 'KeyP') console.log(JSON.stringify({ walls: GAME.walls, enemies: GAME.enemies.map(e => ({ x: e.x, y: e.y, className: e.className })) }));
        if (e.code === 'Delete') { GAME.walls = []; GAME.enemies = []; }
    }
});

canvas.addEventListener('mousedown', e => {
    if (!GAME.editorMode) return;
    const rect = canvas.getBoundingClientRect();
    const ex = Math.floor((e.clientX - rect.left + GAME.cameraX) / 50) * 50;
    const ey = Math.floor((e.clientY - rect.top) / 50) * 50;

    if (GAME.editorItem === 'WALL') {
        GAME.walls.push({ x: ex, y: ey, w: 50, h: 50, health: 1000, destructible: false });
    } else if (GAME.editorItem === 'COVER') {
        GAME.walls.push({ x: ex, y: ey, w: 50, h: 50, health: 100, destructible: true });
    } else if (GAME.editorItem === 'ENEMY') {
        GAME.enemies.push(new Enemy(ex + 15, ey, GAME.editorClass));
    }
});

function update() {
    if (!GAME.running) return;
    if (GAME.editorMode) {
        // Simple editor camera movement
        if (keys['KeyA']) GAME.cameraX -= 10;
        if (keys['KeyD']) GAME.cameraX += 10;
        return;
    }
    GAME.player.update();
    GAME.bullets.forEach(b => {
        if (b.owner === 'enemy' && b.active) {
            if (b.x > GAME.player.x && b.x < GAME.player.x + GAME.player.w &&
                b.y > GAME.player.y && b.y < GAME.player.y + GAME.player.h) {
                GAME.player.health -= b.damage;
                b.active = false;
                for (let i = 0; i < 5; i++) GAME.particles.push(new Particle(b.x, b.y, '#f00'));
            }
        }
    });

    if (GAME.player.health <= 0) {
        GAME.death = true;
        document.getElementById('death-screen').classList.remove('hidden');
    }

    GAME.enemies.forEach(e => e.update());
    GAME.bullets.forEach(b => b.update());
    GAME.bullets = GAME.bullets.filter(b => b.active);
    GAME.walls = GAME.walls.filter(w => !w.destructible || w.health > 0);
    GAME.particles.forEach(p => p.update());
    GAME.particles = GAME.particles.filter(p => p.life > 0);

    if (GAME.enemies.every(e => e.health <= 0)) {
        GAME.missionComplete = true;
        document.getElementById('win-screen').classList.remove('hidden');
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#1a1a1a';
    ctx.lineWidth = 1;
    for (let x = -GAME.cameraX % 50; x < canvas.width; x += 50) {
        ctx.beginPath();
        ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }

    GAME.walls.forEach(wall => {
        ctx.fillStyle = (wall.destructible && wall.health < 50) ? '#1a1a1a' : '#222';
        ctx.fillRect(wall.x - GAME.cameraX, wall.y, wall.w, wall.h);
        ctx.strokeStyle = wall.destructible ? '#444' : '#333';
        ctx.strokeRect(wall.x - GAME.cameraX, wall.y, wall.w, wall.h);
    });

    GAME.enemies.forEach(e => e.draw());
    GAME.player.draw();
    GAME.bullets.forEach(b => b.draw());
    GAME.particles.forEach(p => p.draw());

    if (GAME.editorMode) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.font = '20px Courier New';
        ctx.fillText(`EDITOR MODE: Placing ${GAME.editorItem} (${GAME.editorClass})`, 20, 50);
        ctx.fillText(`Z: Wall, X: Cover, C: Enemy | 1-4: Class | DEL: Clear | TAB: Exit`, 20, 80);

        // Ghost placement
        const gx = Math.floor((mouse.x + GAME.cameraX) / 50) * 50;
        const gy = Math.floor(mouse.y / 50) * 50;
        ctx.strokeStyle = '#fff';
        ctx.strokeRect(gx - GAME.cameraX, gy, 50, 50);
    } else {
        ctx.fillStyle = '#300';
        ctx.fillRect(20, 560, 200, 20);
        ctx.fillStyle = '#f00';
        ctx.fillRect(20, 560, (GAME.player.health / GAME.player.maxHealth) * 200, 20);
    }
}

function loop() {
    update(); draw(); requestAnimationFrame(loop);
}

initLevel();
loop();
