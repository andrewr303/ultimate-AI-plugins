import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  return [{ url: "https://www.example.com/", lastModified: "2026-10-01" }];
}
