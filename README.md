# MusicLib Backend

Django REST API for a free AI-generated background music library. Browse, stream, and download royalty-free tracks with filtering by genre, mood, BPM, and duration.

## Tech Stack

- **Django 5** + **Django REST Framework**
- SQLite (dev) / PostgreSQL (production)
- `django-filter` for advanced filtering
- `django-cors-headers` for frontend integration
- Cloudflare R2 storage ready (S3-compatible)

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Hamza-Sarwar/musiclib-backend.git
cd musiclib-backend
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Edit with your settings

# Run migrations and start
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | insecure-default | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hosts |
| `FRONTEND_URL` | `http://localhost:3000` | CORS allowed origin |
| `DATABASE_URL` | — | PostgreSQL connection string (production) |

## API Endpoints

Base URL: `/api/`

### Tracks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tracks/` | List tracks (paginated, filterable) |
| GET | `/api/tracks/{id}/` | Track detail |
| GET | `/api/tracks/{id}/stream/` | Stream audio (supports Range requests) |
| GET | `/api/tracks/{id}/download/` | Download track (increments counter) |
| POST | `/api/tracks/{id}/play/` | Increment play count |
| GET | `/api/tracks/genres/` | List genres with track counts |
| GET | `/api/tracks/moods/` | List moods with track counts |
| GET | `/api/tracks/featured/` | Featured tracks |
| GET | `/api/tracks/popular/` | Most downloaded tracks |

### Filtering & Search

| Parameter | Example | Description |
|-----------|---------|-------------|
| `genre` | `?genre=lofi` | Filter by genre slug |
| `mood` | `?mood=calm` | Filter by mood slug |
| `search` | `?search=chill` | Search title, description, tags |
| `min_bpm` / `max_bpm` | `?min_bpm=80&max_bpm=120` | BPM range |
| `min_duration` / `max_duration` | `?max_duration=180` | Duration range (seconds) |
| `featured` | `?featured=true` | Featured tracks only |
| `ordering` | `?ordering=-download_count` | Sort by field |

## Project Structure

```
musiclib-backend/
├── config/
│   ├── settings.py          # Django settings
│   └── urls.py              # Root URL config
├── tracks/
│   ├── models.py            # Genre, Mood, Track models
│   ├── serializers.py       # List & detail serializers
│   ├── views.py             # TrackViewSet (stream, download, play)
│   ├── filters.py           # TrackFilter (genre, mood, bpm, duration)
│   ├── admin.py             # Admin registration
│   └── management/commands/ # import_tracks, seed_data
├── scripts/
│   └── generate_music.py    # AI music generation script
├── requirements.txt
└── .env
```

## Models

- **Genre** — name, slug
- **Mood** — name, slug
- **Track** — title, description, genre (FK), mood (FK), tags, audio_file, duration, bpm, waveform_data, download_count, play_count, is_featured, is_active

## Admin

Upload and manage tracks at `http://localhost:8000/admin/`.
