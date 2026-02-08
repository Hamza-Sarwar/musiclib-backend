import { Metadata } from 'next';
import TrackDetailClient from './TrackDetailClient';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

async function getTrack(id: string) {
  try {
    const res = await fetch(`${API_URL}/tracks/${id}/`, {
      cache: 'no-store',
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: { id: string };
}): Promise<Metadata> {
  const track = await getTrack(params.id);
  if (!track) {
    return { title: 'Track Not Found' };
  }

  const description = `Download "${track.title}" - Free ${track.genre?.name || ''} ${track.mood?.name || ''} background music. ${track.duration_display} long, ${track.bpm ? track.bpm + ' BPM' : ''}. Royalty-free.`;

  return {
    title: track.title,
    description,
    openGraph: {
      title: `${track.title} - Free Download | MusicLib`,
      description,
      type: 'music.song',
    },
  };
}

export default async function TrackDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const track = await getTrack(params.id);

  if (!track) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-20 text-center sm:px-6">
        <h1 className="text-2xl font-bold text-white">Track Not Found</h1>
        <p className="mt-2 text-zinc-400">
          The track you&apos;re looking for doesn&apos;t exist or has been
          removed.
        </p>
      </div>
    );
  }

  // JSON-LD structured data
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'MusicRecording',
    name: track.title,
    description: track.description,
    duration: `PT${Math.floor(track.duration / 60)}M${track.duration % 60}S`,
    genre: track.genre?.name,
    isrcCode: track.id,
    interactionStatistic: [
      {
        '@type': 'InteractionCounter',
        interactionType: 'https://schema.org/ListenAction',
        userInteractionCount: track.play_count,
      },
      {
        '@type': 'InteractionCounter',
        interactionType: 'https://schema.org/DownloadAction',
        userInteractionCount: track.download_count,
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <TrackDetailClient track={track} />
    </>
  );
}
