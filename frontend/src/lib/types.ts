export interface Genre {
  id: number;
  name: string;
  slug: string;
  track_count: number;
}

export interface Mood {
  id: number;
  name: string;
  slug: string;
  track_count: number;
}

export interface TrackListItem {
  id: string;
  title: string;
  artist_name: string;
  language: string;
  genre_name: string | null;
  mood_name: string | null;
  duration: number;
  duration_display: string;
  bpm: number | null;
  download_count: number;
  play_count: number;
  audio_url: string | null;
  file_size: number;
  is_featured: boolean;
  created_at: string;
}

export interface TrackDetail {
  id: string;
  title: string;
  artist_name: string;
  language: string;
  description: string;
  lyrics: string;
  genre: Genre | null;
  mood: Mood | null;
  tags_list: string[];
  duration: number;
  duration_display: string;
  bpm: number | null;
  download_count: number;
  play_count: number;
  audio_url: string | null;
  file_size: number;
  waveform_data: number[] | null;
  is_featured: boolean;
  created_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}
