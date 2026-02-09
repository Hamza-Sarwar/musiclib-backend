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
        artist_name: track.artist_name,
        language: track.language,
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
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      {/* Title area */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
          {track.title}
        </h1>
        {track.artist_name && (
          <p className="mt-1 text-base text-violet-400">{track.artist_name}</p>
        )}
        <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-zinc-500">
          {track.genre && <span>{track.genre.name}</span>}
          {track.genre && track.mood && <span className="text-zinc-700">/</span>}
          {track.mood && <span>{track.mood.name}</span>}
          {track.language && track.language !== 'English' && (
            <>
              <span className="text-zinc-800">|</span>
              <span className="text-violet-400/70">{track.language}</span>
            </>
          )}
          {track.bpm && (
            <>
              <span className="text-zinc-800">|</span>
              <span>{track.bpm} BPM</span>
            </>
          )}
          <span className="text-zinc-800">|</span>
          <span>{track.duration_display}</span>
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
      <div className="mb-8 flex items-center gap-3">
        <button
          onClick={handlePlay}
          className="flex items-center gap-2 rounded-full bg-white px-6 py-2.5 text-sm font-medium text-zinc-950 transition hover:scale-105"
        >
          {isCurrentlyPlaying ? (
            <>
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="4" width="4" height="16" />
                <rect x="14" y="4" width="4" height="16" />
              </svg>
              Pause
            </>
          ) : (
            <>
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                <polygon points="5,3 19,12 5,21" />
              </svg>
              Play
            </>
          )}
        </button>
        <a
          href={getDownloadUrl(track.id)}
          className="flex items-center gap-2 rounded-full border border-zinc-800 px-6 py-2.5 text-sm font-medium text-white transition hover:border-zinc-600"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3" />
          </svg>
          Download
          <span className="text-zinc-500">{formatFileSize(track.file_size)}</span>
        </a>
      </div>

      {/* Stats row */}
      <div className="mb-8 flex gap-6 text-sm">
        <div>
          <span className="text-zinc-600">Plays</span>
          <span className="ml-2 font-medium text-white">{track.play_count.toLocaleString()}</span>
        </div>
        <div>
          <span className="text-zinc-600">Downloads</span>
          <span className="ml-2 font-medium text-white">{track.download_count.toLocaleString()}</span>
        </div>
      </div>

      {/* Description */}
      {track.description && (
        <div className="mb-6">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-widest text-zinc-600">
            About
          </h2>
          <p className="text-sm leading-relaxed text-zinc-400">
            {track.description}
          </p>
        </div>
      )}

      {/* Lyrics */}
      {track.lyrics && (
        <div className="mb-6">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-widest text-zinc-600">
            Lyrics
          </h2>
          <div className="rounded-xl bg-zinc-900/50 p-5">
            <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-zinc-300">
              {track.lyrics}
            </pre>
          </div>
        </div>
      )}

      {/* Tags */}
      {track.tags_list.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-widest text-zinc-600">
            Tags
          </h2>
          <div className="flex flex-wrap gap-2">
            {track.tags_list.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-zinc-900 px-3 py-1 text-xs text-zinc-400"
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
