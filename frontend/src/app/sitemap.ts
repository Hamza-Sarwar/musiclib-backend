import { MetadataRoute } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const entries: MetadataRoute.Sitemap = [
    {
      url: SITE_URL,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
  ];

  try {
    // Fetch all tracks for sitemap
    let page = 1;
    let hasNext = true;
    while (hasNext) {
      const res = await fetch(`${API_URL}/tracks/?page=${page}`, {
        cache: 'no-store',
      });
      if (!res.ok) break;
      const data = await res.json();
      for (const track of data.results) {
        entries.push({
          url: `${SITE_URL}/tracks/${track.id}`,
          lastModified: new Date(track.created_at),
          changeFrequency: 'monthly',
          priority: 0.8,
        });
      }
      hasNext = !!data.next;
      page++;
    }
  } catch {
    // Silently fail - sitemap will just have the homepage
  }

  return entries;
}
