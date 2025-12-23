// Game Constants
const SUITS = ['♠', '♥', '♦', '♣'];
const RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];

// Game State
let deck = [];
let playerHand = [];
let dealerHand = [];
let balance = 1000;
let currentBet = 0;
let gameState = 'betting'; // 'betting', 'playing', 'ended'

// DOM Elements
const balanceEl = document.getElementById('balance');
const currentBetEl = document.getElementById('current-bet');
const dealerScoreEl = document.getElementById('dealer-score');
const playerScoreEl = document.getElementById('player-score');
const dealerCardsEl = document.getElementById('dealer-cards');
const playerCardsEl = document.getElementById('player-cards');
const gameMessageEl = document.getElementById('game-message');
const bettingControls = document.getElementById('betting-controls');
const actionControls = document.getElementById('action-controls');
const dealBtn = document.getElementById('deal-btn');
const clearBtn = document.getElementById('clear-btn');
const hitBtn = document.getElementById('hit-btn');
const standBtn = document.getElementById('stand-btn');
const doubleBtn = document.getElementById('double-btn');
const overlay = document.getElementById('overlay');
const overlayTitle = document.getElementById('overlay-title');
const overlaySubtitle = document.getElementById('overlay-subtitle');
const playAgainBtn = document.getElementById('play-again-btn');

// Initialize Game
function init() {
    updateUI();
    
    dealBtn.addEventListener('click', startDeal);
    clearBtn.addEventListener('click', clearBet);
    hitBtn.addEventListener('click', playerHit);
    standBtn.addEventListener('click', playerStand);
    doubleBtn.addEventListener('click', playerDouble);
    playAgainBtn.addEventListener('click', resetGame);
}

// Deck Functions
function createDeck() {
    let newDeck = [];
    for (let suit of SUITS) {
        for (let rank of RANKS) {
            newDeck.push({ suit, rank, isRed: suit === '♥' || suit === '♦' });
        }
    }
    return newDeck;
}

function shuffleDeck(deck) {
    for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [deck[i], deck[j]] = [deck[j], deck[i]];
    }
}

// Logic Functions
function getCardValue(card) {
    if (['J', 'Q', 'K'].includes(card.rank)) return 10;
    if (card.rank === 'A') return 11;
    return parseInt(card.rank);
}

function calculateScore(hand) {
    let score = 0;
    let aces = 0;
    
    for (let card of hand) {
        if (card.rank === 'A') aces++;
        score += getCardValue(card);
    }
    
    while (score > 21 && aces > 0) {
        score -= 10;
        aces--;
    }
    
    return score;
}

// Betting Logic
window.placeBet = function(amount) {
    if (gameState !== 'betting') return;
    if (amount <= balance) {
        currentBet += amount;
        balance -= amount;
        updateUI();
        dealBtn.disabled = false;
    }
};

function clearBet() {
    balance += currentBet;
    currentBet = 0;
    dealBtn.disabled = true;
    updateUI();
}

// Game Flow
function startDeal() {
    if (currentBet === 0) return;
    
    gameState = 'playing';
    deck = createDeck();
    shuffleDeck(deck);
    
    playerHand = [];
    dealerHand = [];
    
    bettingControls.classList.add('hidden');
    actionControls.classList.remove('hidden');
    gameMessageEl.textContent = "Dealing...";

    // Deal alternating
    setTimeout(() => dealCard('player'), 200);
    setTimeout(() => dealCard('dealer'), 400);
    setTimeout(() => dealCard('player'), 600);
    setTimeout(() => {
        dealCard('dealer', true); // Hidden card
        checkInitialGameStatus();
    }, 800);
}

function dealCard(target, isHidden = false) {
    const card = deck.pop();
    const hand = target === 'player' ? playerHand : dealerHand;
    hand.push(card);
    
    const cardEl = document.createElement('div');
    cardEl.className = `card ${card.isRed ? 'red' : ''} dealing`;
    if (isHidden) cardEl.classList.add('flipped');
    
    cardEl.innerHTML = `
        <div class="rank">${card.rank}</div>
        <div class="suit">${card.suit}</div>
        <div class="rank" style="transform: rotate(180deg)">${card.rank}</div>
    `;
    
    const container = target === 'player' ? playerCardsEl : dealerCardsEl;
    container.appendChild(cardEl);
    
    // Trigger animation
    setTimeout(() => cardEl.classList.remove('dealing'), 50);
    
    updateScores();
}

function updateScores() {
    const pScore = calculateScore(playerHand);
    playerScoreEl.textContent = pScore;
    
    // Dealer score only shows first card until end
    if (gameState === 'playing' && dealerHand.length === 2) {
        dealerScoreEl.textContent = getCardValue(dealerHand[0]);
    } else {
        dealerScoreEl.textContent = calculateScore(dealerHand);
    }
}

function checkInitialGameStatus() {
    const pScore = calculateScore(playerHand);
    const dScore = calculateScore(dealerHand);
    
    if (pScore === 21 && dScore === 21) {
        endGame('PUSH', 'Both have Blackjack');
    } else if (pScore === 21) {
        endGame('BLACKJACK!', `You won $${currentBet * 2.5}`, 2.5);
    } else if (dScore === 21) {
        revealDealer();
        endGame('DEALER BLACKJACK', 'You lost your bet');
    } else {
        gameMessageEl.textContent = "Your turn";
    }
}

function playerHit() {
    dealCard('player');
    const score = calculateScore(playerHand);
    doubleBtn.disabled = true; // Can only double on first move
    
    if (score > 21) {
        endGame('BUST', 'You went over 21');
    }
}

function playerStand() {
    dealerTurn();
}

function playerDouble() {
    if (balance >= currentBet) {
        balance -= currentBet;
        currentBet *= 2;
        updateUI();
        dealCard('player');
        
        const score = calculateScore(playerHand);
        if (score > 21) {
            endGame('BUST', 'You went over 21');
        } else {
            dealerTurn();
        }
    }
}

async function dealerTurn() {
    gameState = 'dealer-turn';
    revealDealer();
    
    let dScore = calculateScore(dealerHand);
    
    while (dScore < 17) {
        await new Promise(r => setTimeout(r, 600));
        dealCard('dealer');
        dScore = calculateScore(dealerHand);
    }
    
    determineWinner();
}

function revealDealer() {
    const hiddenCard = dealerCardsEl.querySelector('.card.flipped');
    if (hiddenCard) hiddenCard.classList.remove('flipped');
    updateScores();
}

function determineWinner() {
    const pScore = calculateScore(playerHand);
    const dScore = calculateScore(dealerHand);
    
    if (dScore > 21) {
        endGame('DEALER BUSTS!', `You won $${currentBet * 2}`, 2);
    } else if (pScore > dScore) {
        endGame('YOU WIN!', `You won $${currentBet * 2}`, 2);
    } else if (pScore < dScore) {
        endGame('DEALER WINS', 'Better luck next time');
    } else {
        endGame('PUSH', 'Bet returned');
    }
}

function endGame(title, subtitle, multiplier = 0) {
    gameState = 'ended';
    if (multiplier > 0) {
        balance += Math.floor(currentBet * multiplier);
    } else if (title === 'PUSH') {
        balance += currentBet;
    }
    
    setTimeout(() => {
        overlayTitle.textContent = title;
        overlaySubtitle.textContent = subtitle;
        overlay.classList.remove('hidden');
        updateUI();
    }, 1000);
}

function resetGame() {
    currentBet = 0;
    playerHand = [];
    dealerHand = [];
    playerCardsEl.innerHTML = '';
    dealerCardsEl.innerHTML = '';
    dealerScoreEl.textContent = '0';
    playerScoreEl.textContent = '0';
    
    overlay.classList.add('hidden');
    bettingControls.classList.remove('hidden');
    actionControls.classList.add('hidden');
    dealBtn.disabled = true;
    doubleBtn.disabled = false;
    gameState = 'betting';
    gameMessageEl.textContent = "Place your bet to start";
    updateUI();
}

function updateUI() {
    balanceEl.textContent = `$${balance.toLocaleString()}`;
    currentBetEl.textContent = `$${currentBet.toLocaleString()}`;
}

// Run Initializer
init();
