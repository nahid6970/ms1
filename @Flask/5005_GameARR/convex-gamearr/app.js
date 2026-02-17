import { ConvexHttpClient } from "https://esm.sh/convex@1.16.0/browser";

const client = new ConvexHttpClient("YOUR_CONVEX_URL_HERE");

window.toggleForm = () => {
  document.getElementById('gameForm').classList.toggle('active');
};

window.addGame = async () => {
  const name = document.getElementById('gameName').value;
  const year = document.getElementById('gameYear').value;
  const image = document.getElementById('gameImage').value;
  const url = document.getElementById('gameUrl').value;
  const rating = parseInt(document.getElementById('gameRating').value) || 0;
  const progression = document.getElementById('gameProgression').value;
  const collection = document.getElementById('gameCollection').value;
  
  if (!name) return alert('Game name is required');
  
  await client.mutation("games:add", { name, year, image, url, rating, progression, collection });
  
  document.getElementById('gameName').value = '';
  document.getElementById('gameYear').value = '';
  document.getElementById('gameImage').value = '';
  document.getElementById('gameUrl').value = '';
  document.getElementById('gameRating').value = '';
  document.getElementById('gameCollection').value = '';
  
  toggleForm();
  loadGames();
};

window.loadGames = async () => {
  const searchQuery = document.getElementById('searchInput').value;
  const collectionFilter = document.getElementById('collectionFilter').value;
  const sortBy = document.getElementById('sortBy').value;
  
  let games = searchQuery 
    ? await client.query("games:search", { query: searchQuery })
    : await client.query("games:list");
  
  if (collectionFilter) {
    games = games.filter(g => g.collection === collectionFilter);
  }
  
  games.sort((a, b) => {
    if (sortBy === 'name') return a.name.localeCompare(b.name);
    if (sortBy === 'year') return (b.year || '').localeCompare(a.year || '');
    if (sortBy === 'rating') return (b.rating || 0) - (a.rating || 0);
    return 0;
  });
  
  const collections = [...new Set(games.map(g => g.collection).filter(c => c))];
  const collectionSelect = document.getElementById('collectionFilter');
  const currentValue = collectionSelect.value;
  collectionSelect.innerHTML = '<option value="">All Collections</option>' + 
    collections.map(c => `<option value="${c}">${c}</option>`).join('');
  collectionSelect.value = currentValue;
  
  document.getElementById('gamesGrid').innerHTML = games.map(game => `
    <div class="game-card" onclick="window.open('${game.url || '#'}', '_blank')">
      <img src="${game.image || 'https://via.placeholder.com/200x280?text=No+Image'}" alt="${game.name}">
      <div class="game-info">
        <div class="game-name">${game.name}</div>
        <div class="game-year">${game.year || 'N/A'}</div>
        <div class="game-rating">${'⭐'.repeat(game.rating || 0)}</div>
        <div class="game-progression">${game.progression || ''}</div>
      </div>
    </div>
  `).join('');
};

document.getElementById('searchInput').addEventListener('input', loadGames);

loadGames();
setInterval(loadGames, 10000);
