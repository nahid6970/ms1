import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Initialize or get current game state
export const getGameState = query({
  args: {},
  handler: async (ctx) => {
    const gameState = await ctx.db.query("game").order("desc").first();
    if (!gameState) {
      return { diceValue: 1, lastRolledBy: "System" };
    }
    return gameState;
  },
});

// Roll the dice and save result
export const rollDice = mutation({
  args: { player: v.string() },
  handler: async (ctx, args) => {
    const diceValue = Math.floor(Math.random() * 6) + 1;
    const newId = await ctx.db.insert("game", {
      diceValue,
      lastRolledBy: args.player,
      timestamp: Date.now(),
    });
    return { id: newId, diceValue };
  },
});
