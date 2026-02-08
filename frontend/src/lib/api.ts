import {
  Genre,
  Mood,
  TrackListItem,
  TrackDetail,
  PaginatedResponse,
  User,
  AuthTokens,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

// Tracks
export async function fetchTracks(
  params?: Record<string, string>
): Promise<PaginatedResponse<TrackListItem>> {
  const query = params ? '?' + new URLSearchParams(params).toString() : '';
  return apiFetch(`/tracks/${query}`);
}

export async function fetchTrack(id: string): Promise<TrackDetail> {
  return apiFetch(`/tracks/${id}/`);
}

export async function fetchGenres(): Promise<Genre[]> {
  return apiFetch('/tracks/genres/');
}

export async function fetchMoods(): Promise<Mood[]> {
  return apiFetch('/tracks/moods/');
}

export async function fetchFeatured(): Promise<TrackListItem[]> {
  return apiFetch('/tracks/featured/');
}

export async function fetchPopular(): Promise<TrackListItem[]> {
  return apiFetch('/tracks/popular/');
}

export async function recordPlay(id: string): Promise<void> {
  await apiFetch(`/tracks/${id}/play/`, { method: 'POST' });
}

export function getDownloadUrl(id: string): string {
  return `${API_URL}/tracks/${id}/download/`;
}

export async function fetchSimilarTracks(
  id: string
): Promise<TrackListItem[]> {
  return apiFetch(`/tracks/${id}/similar/`);
}

// Auth
export async function register(
  username: string,
  email: string,
  password: string
): Promise<AuthTokens> {
  return apiFetch('/auth/register/', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  });
}

export async function login(
  username: string,
  password: string
): Promise<AuthTokens> {
  return apiFetch('/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

export async function refreshToken(refresh: string): Promise<{ access: string }> {
  return apiFetch('/auth/refresh/', {
    method: 'POST',
    body: JSON.stringify({ refresh }),
  });
}

export async function fetchMe(token: string): Promise<User> {
  return apiFetch('/auth/me/', { headers: authHeaders(token) });
}
