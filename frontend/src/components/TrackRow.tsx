'use client';

import { TrackListItem } from '@/lib/types';
import TrackCard from './TrackCard';

export default function TrackRow({ tracks }: { tracks: TrackListItem[] }) {
  if (tracks.length === 0) return null;

  return (
    <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-hide">
      {tracks.map((track) => (
        <div key={track.id} className="w-64 flex-shrink-0">
          <TrackCard track={track} />
        </div>
      ))}
    </div>
  );
}
