// Game State
let ammoCount = 1;
let chambers = [0, 0, 0, 0, 0, 0];
let currentChamber = 0;
let survived = 0;
let deaths = 0;
let isSpinning = false;

// DOM Elements
const cylinder = document.getElementById('cylinder');
const ammoDisplay = document.getElementById('ammoCount');
const btnUp = document.getElementById('btnUp');
const btnDown = document.getElementById('btnDown');
const spinBtn = document.getElementById('spinBtn');
const pullTriggerBtn = document.getElementById('pullTriggerBtn');
const statusText = document.getElementById('statusText');
const survivedDisplay = document.getElementById('survivedCount');
const deathDisplay = document.getElementById('deathCount');
const modal = document.getElementById('resultModal');
const resultTitle = document.getElementById('resultTitle');
const resultDesc = document.getElementById('resultDesc');
const closeModal = document.getElementById('closeModal');

// Audio
const audioSpin = document.getElementById('audioSpin');
const audioClick = document.getElementById('audioClick');
const audioShot = document.getElementById('audioShot');

// Initialize
updateAmmoUI();

// Event Listeners
btnUp.addEventListener('click', () => {
    if (ammoCount < 6) {
        ammoCount++;
        updateAmmoUI();
    }
});

btnDown.addEventListener('click', () => {
    if (ammoCount > 1) {
        ammoCount--;
        updateAmmoUI();
    }
});

spinBtn.addEventListener('click', spinCylinder);
pullTriggerBtn.addEventListener('click', pullTrigger);
closeModal.addEventListener('click', () => modal.classList.remove('show'));

function updateAmmoUI() {
    ammoDisplay.innerText = ammoCount;
    // Visual indicators for chambers
    const chamberElements = document.querySelectorAll('.chamber');
    chamberElements.forEach((el, index) => {
        el.classList.remove('loaded');
        if (index < ammoCount) {
            el.classList.add('loaded');
        }
    });
    statusText.innerText = "LOADED " + ammoCount + " BULLETS";
}

function spinCylinder() {
    if (isSpinning) return;
    
    isSpinning = true;
    spinBtn.disabled = true;
    pullTriggerBtn.disabled = true;
    statusText.innerText = "SPINNING...";
    
    // Play spin sound
    audioSpin.currentTime = 0;
    audioSpin.play().catch(e => console.log("Audio play blocked"));

    // Random rotation
    const randomSpins = 5 + Math.floor(Math.random() * 10);
    const randomChamber = Math.floor(Math.random() * 6);
    const degrees = randomSpins * 360 + randomChamber * 60;
    
    // Rotate the cylinder
    cylinder.style.transform = `rotate(-${degrees}deg)`;

    // Calculate which chamber is at the top (active)
    // The visual rotation is -degrees, so we map that back to 0-5
    currentChamber = randomChamber;

    // Reset chambers array based on ammoCount
    chambers = [0, 0, 0, 0, 0, 0];
    let loaded = 0;
    // Distribute bullets (simple logic: fill first N)
    // In a real spin, the bullets stay in their spots but the starting point changes.
    // Here we just shuffle the loaded bullets' positions.
    const positions = [0, 1, 2, 3, 4, 5];
    shuffle(positions);
    for(let i=0; i<ammoCount; i++) {
        chambers[positions[i]] = 1;
    }

    // Update chamber visuals based on distribution
    const chamberElements = document.querySelectorAll('.chamber');
    chamberElements.forEach((el, index) => {
        el.classList.remove('loaded');
        if (chambers[index] === 1) {
            el.classList.add('loaded');
        }
    });

    setTimeout(() => {
        isSpinning = false;
        spinBtn.disabled = false;
        pullTriggerBtn.disabled = false;
        statusText.innerText = "CYLINDER SET. TAKE YOUR CHANCE.";
    }, 3000);
}

function pullTrigger() {
    if (isSpinning) return;

    // Play click sound
    audioClick.currentTime = 0;
    audioClick.play().catch(e => console.log("Audio play blocked"));

    // Check if current chamber is loaded
    // We check the chamber currently at the "top" (index 0 is top at start)
    // After rotation, we need to track index correctly.
    // The currentChamber variable already tracks where it landed.
    
    const isLoaded = chambers[currentChamber];

    if (isLoaded) {
        gameOver(true);
    } else {
        gameOver(false);
    }
}

function gameOver(dead) {
    spinBtn.disabled = true;
    pullTriggerBtn.disabled = true;

    if (dead) {
        deaths++;
        deathDisplay.innerText = deaths;
        statusText.innerText = "BANG!";
        resultTitle.innerText = "FATAL!";
        resultTitle.style.color = "var(--accent-red)";
        resultDesc.innerText = "The bullet found its target. You are dead.";
        
        audioShot.currentTime = 0;
        audioShot.play().catch(e => console.log("Audio play blocked"));
        
        document.body.classList.add('shot-fired');
        setTimeout(() => document.body.classList.remove('shot-fired'), 500);
    } else {
        survived++;
        survivedDisplay.innerText = survived;
        statusText.innerText = "CLICK...";
        resultTitle.innerText = "SAFE";
        resultTitle.style.color = "var(--accent-gold)";
        resultDesc.innerText = "The chamber was empty. Fortune favors the bold.";
    }

    setTimeout(() => {
        modal.classList.add('show');
        spinBtn.disabled = false;
        pullTriggerBtn.disabled = true; // Must spin again
    }, 600);
}

function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[array[j]]] = [array[array[j]], array[i]];
    }
}
