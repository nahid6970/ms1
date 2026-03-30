import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Get the current game state
export const getGameState = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("game_state").order("desc").first();
  },
});

// Start a brand new game
export const startNewGame = mutation({
  args: { numPlayers: v.number() },
  handler: async (ctx, args) => {
    const initialState = {
      status: "playing",
      numPlayers: args.numPlayers,
      currentPlayer: 0, // 0: Red, 1: Green, 2: Yellow, 3: Blue
      diceValue: 1,
      waitingForRoll: true,
      tokens: [
        { player: 'red', pos: -1 }, { player: 'red', pos: -1 }, { player: 'red', pos: -1 }, { player: 'red', pos: -1 },
        { player: 'green', pos: -1 }, { player: 'green', pos: -1 }, { player: 'green', pos: -1 }, { player: 'green', pos: -1 },
        { player: 'yellow', pos: -1 }, { player: 'yellow', pos: -1 }, { player: 'yellow', pos: -1 }, { player: 'yellow', pos: -1 },
        { player: 'blue', pos: -1 }, { player: 'blue', pos: -1 }, { player: 'blue', pos: -1 }, { player: 'blue', pos: -1 },
      ],
      timestamp: Date.now(),
    };
    const id = await ctx.db.insert("game_state", initialState);
    return id;
  },
});

// Roll the dice (updated)
export const rollDice = mutation({
  args: { playerIndex: v.number() },
  handler: async (ctx, args) => {
    const state = await ctx.db.query("game_state").order("desc").first();
    if (!state || !state.waitingForRoll || state.currentPlayer !== args.playerIndex) {
      throw new Error("Cannot roll now");
    }

    const diceValue = Math.floor(Math.random() * 6) + 1;
    await ctx.db.patch(state._id, {
      diceValue,
      waitingForRoll: false,
      timestamp: Date.now(),
    });
    return diceValue;
  },
});
