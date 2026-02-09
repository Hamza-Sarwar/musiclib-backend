'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { TrackListItem, PaginatedResponse } from '@/lib/types';
import { fetchTracks, fetchFeatured, fetchPopular } from '@/lib/api';
import TrackGrid from '@/components/TrackGrid';
import TrackFilters from '@/components/TrackFilters';
import Pagination from '@/components/Pagination';
import TrackCard from '@/components/TrackCard';
import LandingPage from '@/components/LandingPage';
import { useAuth } from '@/contexts/AuthContext';

function HomeContent() {
  const searchParams = useSearchParams();
  const { user, isLoading: authLoading } = useAuth();
  const [data, setData] = useState<PaginatedResponse<TrackListItem> | null>(null);
  const [featured, setFeatured] = useState<TrackListItem[]>([]);
  const [popular, setPopular] = useState<TrackListItem[]>([]);
  const [loading, setLoading] = useState(true);

  const browseMode = searchParams.get('browse') === 'true';

  const hasFilters =
    searchParams.get('genre') ||
    searchParams.get('mood') ||
    searchParams.get('search') ||
    searchParams.get('page');

  // Show landing page for unauthenticated users who haven't clicked "Browse"
  const showLanding = !authLoading && !user && !browseMode && !hasFilters;

  useEffect(() => {
    if (showLanding) return;
    if (!hasFilters) {
      Promise.all([fetchFeatured(), fetchPopular()])
        .then(([f, p]) => {
          setFeatured(f);
          setPopular(p);
        })
        .catch(() => {});
    }
  }, [hasFilters, showLanding]);

  useEffect(() => {
    if (showLanding) {
      setLoading(false);
      return;
    }
    setLoading(true);
    const params: Record<string, string> = {};
    searchParams.forEach((value, key) => {
      if (key !== 'browse') params[key] = value;
    });
    fetchTracks(params)
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [searchParams, showLanding]);

  if (authLoading) {
    return (
      <div className="py-20 text-center text-sm text-zinc-600">Loading...</div>
    );
  }

  if (showLanding) {
    return <LandingPage />;
  }

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6">
      {/* Hero - only on default view */}
      {!hasFilters && (
        <section className="pb-8 pt-12 text-center">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Free{' '}
            <span className="bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
              AI-Generated
            </span>{' '}
            Music
          </h1>
          <p className="mx-auto mt-3 max-w-md text-sm text-zinc-500">
            Download royalty-free background music for your videos, podcasts, and projects. No attribution required.
          </p>
        </section>
      )}

      {/* Featured - compact */}
      {!hasFilters && featured.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-1 text-xs font-semibold uppercase tracking-widest text-zinc-500">
            Featured
          </h2>
          <div className="rounded-xl bg-zinc-900/50 py-1">
            {featured.slice(0, 5).map((track) => (
              <TrackCard key={track.id} track={track} />
            ))}
          </div>
        </section>
      )}

      {/* Popular - compact */}
      {!hasFilters && popular.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-1 text-xs font-semibold uppercase tracking-widest text-zinc-500">
            Popular
          </h2>
          <div className="rounded-xl bg-zinc-900/50 py-1">
            {popular.slice(0, 5).map((track) => (
              <TrackCard key={track.id} track={track} />
            ))}
          </div>
        </section>
      )}

      {/* Filters */}
      <section className="mb-6">
        <TrackFilters />
      </section>

      {/* All Tracks */}
      <section className="pb-8">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-medium text-zinc-300">
            {searchParams.get('search')
              ? `Results for "${searchParams.get('search')}"`
              : 'All Tracks'}
          </h2>
          {data && (
            <span className="text-xs text-zinc-600">
              {data.count} track{data.count !== 1 ? 's' : ''}
            </span>
          )}
        </div>

        {loading ? (
          <div className="py-16 text-center text-sm text-zinc-600">
            Loading...
          </div>
        ) : (
          <>
            <div className="rounded-xl bg-zinc-900/30 py-1">
              <TrackGrid tracks={data?.results || []} />
            </div>
            {data && <Pagination count={data.count} />}
          </>
        )}
      </section>
    </div>
  );
}

export default function HomePage() {
  return (
    <Suspense
      fallback={
        <div className="py-20 text-center text-sm text-zinc-600">Loading...</div>
      }
    >
      <HomeContent />
    </Suspense>
  );
}
