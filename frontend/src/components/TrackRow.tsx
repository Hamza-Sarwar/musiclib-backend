'use client';

import { TrackListItem } from '@/lib/types';
import TrackCard from './TrackCard';

export default function TrackRow({ tracks }: { tracks: TrackListItem[] }) {
  if (tracks.length === 0) return null;

  return (
    <div className="rounded-xl bg-zinc-900/50 py-1">
      {tracks.map((track) => (
        <TrackCard key={track.id} track={track} />
      ))}
    </div>
  );
}
