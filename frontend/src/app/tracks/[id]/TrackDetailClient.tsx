'use client';

import { TrackDetail } from '@/lib/types';
import { usePlayer } from '@/contexts/PlayerContext';
import { getDownloadUrl } from '@/lib/api';
import { formatDuration, formatFileSize } from '@/lib/utils';
import WaveformPlayer from '@/components/WaveformPlayer';
import SimilarTracks from '@/components/SimilarTracks';

export default function TrackDetailClient({ track }: { track: TrackDetail }) {
  const { play, pause, currentTrack, isPlaying } = usePlayer();
  const isActive = currentTrack?.id === track.id;
  const isCurrentlyPlaying = isActive && isPlaying;

  const handlePlay = () => {
    if (isCurrentlyPlaying) {
      pause();
    } else {
      play({
        id: track.id,
        title: track.title,
        genre_name: track.genre?.name || null,
        mood_name: track.mood?.name || null,
        duration: track.duration,
        duration_display: track.duration_display,
        bpm: track.bpm,
        download_count: track.download_count,
        play_count: track.play_count,
        audio_url: track.audio_url,
        file_size: track.file_size,
        is_featured: track.is_featured,
        created_at: track.created_at,
      });
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white sm:text-3xl">
          {track.title}
        </h1>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          {track.genre && (
            <span className="rounded-full bg-primary-900/50 px-3 py-1 text-xs font-medium text-primary-300">
              {track.genre.name}
            </span>
          )}
          {track.mood && (
            <span className="rounded-full bg-zinc-800 px-3 py-1 text-xs text-zinc-300">
              {track.mood.name}
            </span>
          )}
        </div>
      </div>

      {/* Waveform */}
      <div className="mb-6">
        <WaveformPlayer
          track={{
            ...track,
            genre_name: track.genre?.name || null,
            mood_name: track.mood?.name || null,
          }}
        />
      </div>

      {/* Actions */}
      <div className="mb-8 flex flex-wrap gap-3">
        <button
          onClick={handlePlay}
          className="flex items-center gap-2 rounded-lg bg-primary-600 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-primary-500"
        >
          {isCurrentlyPlaying ? (
            <>
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="4" width="4" height="16" />
                <rect x="14" y="4" width="4" height="16" />
              </svg>
              Pause
            </>
          ) : (
            <>
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <polygon points="5,3 19,12 5,21" />
              </svg>
              Play
            </>
          )}
        </button>
        <a
          href={getDownloadUrl(track.id)}
          className="flex items-center gap-2 rounded-lg border border-zinc-700 px-6 py-2.5 text-sm font-medium text-white transition hover:border-zinc-500"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
          </svg>
          Download
        </a>
      </div>

      {/* Info Grid */}
      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
          <p className="text-xs text-zinc-500">Duration</p>
          <p className="text-lg font-semibold text-white">
            {track.duration_display}
          </p>
        </div>
        {track.bpm && (
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
            <p className="text-xs text-zinc-500">BPM</p>
            <p className="text-lg font-semibold text-white">{track.bpm}</p>
          </div>
        )}
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
          <p className="text-xs text-zinc-500">Downloads</p>
          <p className="text-lg font-semibold text-white">
            {track.download_count.toLocaleString()}
          </p>
        </div>
        <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
          <p className="text-xs text-zinc-500">File Size</p>
          <p className="text-lg font-semibold text-white">
            {formatFileSize(track.file_size)}
          </p>
        </div>
      </div>

      {/* Description */}
      {track.description && (
        <div className="mb-8">
          <h2 className="mb-2 text-sm font-semibold text-zinc-400">
            Description
          </h2>
          <p className="text-sm leading-relaxed text-zinc-300">
            {track.description}
          </p>
        </div>
      )}

      {/* Tags */}
      {track.tags_list.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-2 text-sm font-semibold text-zinc-400">Tags</h2>
          <div className="flex flex-wrap gap-2">
            {track.tags_list.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-zinc-800 px-3 py-1 text-xs text-zinc-300"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Similar Tracks */}
      <div className="mt-12">
        <SimilarTracks trackId={track.id} />
      </div>
    </div>
  );
}
