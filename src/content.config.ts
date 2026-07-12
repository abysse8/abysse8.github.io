import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

// Contract for everything downstream: the pipeline's emit_drafts.py writes
// files that must validate against this schema. draft defaults to true —
// nothing publishes without a deliberate flip.
const ideas = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/ideas" }),
  schema: z.object({
    title: z.string().max(80),
    date: z.coerce.date(),
    tags: z.array(z.string()).min(1).max(4),
    status: z.enum(["spark", "growing", "mature"]).default("spark"),
    sources: z
      .array(
        z.object({
          kind: z.enum(["chatgpt", "claude", "codex", "claude-code", "manual"]),
          date: z.coerce.date(),
          fragment_id: z.string().optional(),
          quote: z.string().optional(),
        }),
      )
      .default([]),
    revisits: z.array(z.coerce.date()).optional(),
    draft: z.boolean().default(true),
  }),
});

export const collections = { ideas };
