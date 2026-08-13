import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

// Automatically check all channels for new videos every 6 hours.
crons.interval(
  "auto-refresh-channels",
  { hours: 6 },
  internal.refresh.refreshAllCron,
);

export default crons;
