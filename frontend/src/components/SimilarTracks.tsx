'use client';

import { useEffect, useState } from 'react';
import { TrackListItem } from '@/lib/types';
import { fetchSimilarTracks } from '@/lib/api';
import TrackCard from './TrackCard';

export default function SimilarTracks({ trackId }: { trackId: string }) {
  const [tracks, setTracks] = useState<TrackListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSimilarTracks(trackId)
      .then(setTracks)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [trackId]);

  if (loading) {
    return (
      <div className="py-4 text-center text-sm text-zinc-600">
        Loading similar tracks...
      </div>
    );
  }

  if (tracks.length === 0) return null;

  return (
    <section>
      <h2 className="mb-2 text-xs font-semibold uppercase tracking-widest text-zinc-600">
        Similar Tracks
      </h2>
      <div className="rounded-xl bg-zinc-900/30 py-1">
        {tracks.map((track) => (
          <TrackCard key={track.id} track={track} />
        ))}
      </div>
    </section>
  );
}
