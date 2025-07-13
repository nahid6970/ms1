const diceContainer = document.getElementById('dice-container');
const diceCountInput = document.getElementById('dice-count');

function rollDice() {
    diceContainer.innerHTML = '';
    const diceCount = parseInt(diceCountInput.value);

    for (let i = 0; i < diceCount; i++) {
        const diceValue = Math.floor(Math.random() * 6) + 1;
        const dice = document.createElement('div');
        dice.classList.add('dice');
        dice.textContent = diceValue;
        diceContainer.appendChild(dice);
    }
}

document.addEventListener('keydown', (event) => {
    if (event.code === 'Space') {
        rollDice();
    }
});

// Initial roll
rollDice();