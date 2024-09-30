import { defineCollection, z } from "astro:content";

const writing = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    heroImage: z.string().optional(),
  }),
});

const reading = defineCollection({
  type: "data",
  schema: z.object({
    title: z.string(),
    author: z.string(),
    coverImage: z.string().optional(),
    yearRead: z.coerce.date().optional(),
  }),
});

export const collections = { writing };
