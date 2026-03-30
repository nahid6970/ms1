import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const getGameState = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("game_state").order("desc").first();
  },
});

const START_INDEXES = [1, 14, 40, 27]; // Red, Green, Yellow, Blue
const SAFE_SQUARES = [1, 9, 14, 22, 27, 35, 40, 48];

function getAbsPos(playerIdx: number, relativePos: number) {
  if (relativePos === -1 || relativePos >= 52) return -1;
  return (relativePos + START_INDEXES[playerIdx]) % 52;
}

export const startNewGame = mutation({
  args: { numPlayers: v.number() },
  handler: async (ctx, args) => {
    let firstPlayer = 0;
    if (args.numPlayers === 2) firstPlayer = 1;

    const initialState = {
      status: "playing",
      numPlayers: args.numPlayers,
      currentPlayer: firstPlayer, 
      diceValue: 1,
      waitingForRoll: true,
      sixCount: 0,
      turnId: Date.now().toString(),
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
    if (diceValue === 6) sixCount++; else sixCount = 0;

    if (sixCount === 3) {
      await ctx.db.patch(state._id, {
        diceValue, sixCount: 0,
        currentPlayer: getNextPlayer(state.currentPlayer, state.numPlayers),
        waitingForRoll: true,
        turnId: Date.now().toString(),
      });
      return { diceValue, skipped: true };
    }

    await ctx.db.patch(state._id, { diceValue, sixCount, waitingForRoll: false, timestamp: Date.now() });
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

    if (token.pos === -1) {
      if (state.diceValue === 6) { token.pos = 0; extraTurn = true; }
      else return;
    } else {
      const newPos = token.pos + state.diceValue;
      if (newPos <= 57) {
        token.pos = newPos;
        if (state.diceValue === 6) extraTurn = true;
      } else return;
    }

    // Correct Capture Logic using Absolute Positions
    const myAbsPos = getAbsPos(state.currentPlayer, token.pos);
    const isAtSafeSquare = SAFE_SQUARES.includes(myAbsPos);

    if (myAbsPos !== -1 && !isAtSafeSquare) {
      for (let i = 0; i < tokens.length; i++) {
        const otherPlayerIdx = Math.floor(i / 4);
        if (otherPlayerIdx !== state.currentPlayer) {
          const otherAbsPos = getAbsPos(otherPlayerIdx, tokens[i].pos);
          if (otherAbsPos === myAbsPos) {
            tokens[i].pos = -1; // Capture!
            extraTurn = true; 
          }
        }
      }
    }

    let nextPlayer = state.currentPlayer;
    if (!extraTurn) nextPlayer = getNextPlayer(state.currentPlayer, state.numPlayers);

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
    await ctx.db.patch(state._id, {
      currentPlayer: getNextPlayer(state.currentPlayer, state.numPlayers),
      waitingForRoll: true,
      sixCount: 0,
      turnId: Date.now().toString(),
    });
  },
});

function getNextPlayer(curr: number, total: number) {
  if (total === 2) return curr === 1 ? 2 : 1;
  if (total === 3) return (curr + 1) % 3;
  return (curr + 1) % 4;
}
