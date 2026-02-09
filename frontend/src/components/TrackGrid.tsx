import { TrackListItem } from '@/lib/types';
import TrackCard from './TrackCard';

export default function TrackGrid({ tracks }: { tracks: TrackListItem[] }) {
  if (tracks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <svg
          className="mb-3 h-10 w-10 text-zinc-800"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path d="M9 19V6l12-3v13M9 19c0 1.1-1.34 2-3 2s-3-.9-3-2 1.34-2 3-2 3 .9 3 2zm12-3c0 1.1-1.34 2-3 2s-3-.9-3-2 1.34-2 3-2 3 .9 3 2z" />
        </svg>
        <p className="text-sm text-zinc-500">No tracks found</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-zinc-900">
      {tracks.map((track) => (
        <TrackCard key={track.id} track={track} />
      ))}
    </div>
  );
}
