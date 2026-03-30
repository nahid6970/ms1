import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const getGameState = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("game_state").order("desc").first();
  },
});

export const startNewGame = mutation({
  args: { numPlayers: v.number() },
  handler: async (ctx, args) => {
    // 2 players: Green (1) and Yellow (2)
    // 3 players: Red (0), Green (1), Yellow (2)
    // 4 players: Red, Green, Yellow, Blue
    let firstPlayer = 0;
    if (args.numPlayers === 2) firstPlayer = 1;

    const initialState = {
      status: "playing",
      numPlayers: args.numPlayers,
      currentPlayer: firstPlayer, 
      diceValue: 1,
      waitingForRoll: true,
      sixCount: 0,
      turnId: Date.now().toString(), // Track unique turn states
      tokens: [
        { player: 'red', pos: -1 }, { player: 'red', pos: -1 }, { player: 'red', pos: -1 }, { player: 'red', pos: -1 },
        { player: 'green', pos: -1 }, { player: 'green', pos: -1 }, { player: 'green', pos: -1 }, { player: 'green', pos: -1 },
        { player: 'yellow', pos: -1 }, { player: 'yellow', pos: -1 }, { player: 'yellow', pos: -1 }, { player: 'yellow', pos: -1 },
        { player: 'blue', pos: -1 }, { player: 'blue', pos: -1 }, { player: 'blue', pos: -1 }, { player: 'blue', pos: -1 },
      ],
      timestamp: Date.now(),
    };
    return await ctx.db.insert("game_state", initialState);
  },
});

export const rollDice = mutation({
  args: { playerIndex: v.number() },
  handler: async (ctx, args) => {
    const state = await ctx.db.query("game_state").order("desc").first();
    if (!state || !state.waitingForRoll || state.currentPlayer !== args.playerIndex) return;

    const diceValue = Math.floor(Math.random() * 6) + 1;
    let sixCount = state.sixCount;

    if (diceValue === 6) {
      sixCount++;
    } else {
      sixCount = 0;
    }

    // Rule: Three consecutive sixes skips turn
    if (sixCount === 3) {
      await ctx.db.patch(state._id, {
        diceValue,
        sixCount: 0,
        currentPlayer: getNextPlayer(state.currentPlayer, state.numPlayers),
        waitingForRoll: true,
        turnId: Date.now().toString(),
      });
      return { diceValue, skipped: true };
    }

    await ctx.db.patch(state._id, {
      diceValue,
      sixCount,
      waitingForRoll: false,
      timestamp: Date.now(),
    });
    return { diceValue };
  },
});

export const moveToken = mutation({
  args: { tokenIndex: v.number() },
  handler: async (ctx, args) => {
    const state = await ctx.db.query("game_state").order("desc").first();
    if (!state || state.waitingForRoll) return;

    const playerIndex = Math.floor(args.tokenIndex / 4);
    if (playerIndex !== state.currentPlayer) return;

    const tokens = [...state.tokens];
    const token = tokens[args.tokenIndex];
    let extraTurn = false;

    // Move Logic
    if (token.pos === -1) {
      if (state.diceValue === 6) {
        token.pos = 0;
        extraTurn = true; 
      } else return;
    } else {
      const newPos = token.pos + state.diceValue;
      if (newPos <= 57) {
        token.pos = newPos;
        if (state.diceValue === 6) extraTurn = true;
      } else return;
    }

    // Capture logic
    if (token.pos < 52 && ![0, 8, 13, 21, 26, 34, 39, 47].includes(token.pos)) {
      for (let i = 0; i < tokens.length; i++) {
        const otherPlayer = Math.floor(i / 4);
        if (otherPlayer !== state.currentPlayer && tokens[i].pos === token.pos) {
          tokens[i].pos = -1;
          extraTurn = true; // Bonus turn for capture
        }
      }
    }

    let nextPlayer = state.currentPlayer;
    if (!extraTurn) {
      nextPlayer = getNextPlayer(state.currentPlayer, state.numPlayers);
    }

    await ctx.db.patch(state._id, {
      tokens,
      currentPlayer: nextPlayer,
      waitingForRoll: true,
      sixCount: extraTurn ? state.sixCount : 0,
      turnId: Date.now().toString(),
      timestamp: Date.now(),
    });
  },
});

export const skipTurn = mutation({
  args: { playerIndex: v.number() },
  handler: async (ctx, args) => {
    const state = await ctx.db.query("game_state").order("desc").first();
    if (!state || state.waitingForRoll || state.currentPlayer !== args.playerIndex) return;

    const nextPlayer = getNextPlayer(state.currentPlayer, state.numPlayers);
    await ctx.db.patch(state._id, {
      currentPlayer: nextPlayer,
      waitingForRoll: true,
      sixCount: 0,
      turnId: Date.now().toString(),
      timestamp: Date.now(),
    });
  },
});

function getNextPlayer(curr: number, total: number) {
  if (total === 2) return curr === 1 ? 2 : 1;
  if (total === 3) return (curr + 1) % 3;
  return (curr + 1) % 4;
}
