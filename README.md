# 🎵 MusicLib - Free AI Background Music Download Site

## Phase 1: Foundation Setup

### Step 1: Create the Django Project

```bash
# Create project folder
mkdir musiclib-backend && cd musiclib-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install django djangorestframework django-cors-headers django-filter pillow boto3 django-storages djangorestframework-simplejwt python-dotenv mutagen

# Create Django project
django-admin startproject config .

# Create the tracks app
python manage.py startapp tracks

# Create media directory for local development
mkdir -p media/tracks
```

### Step 2: Copy the files from this package into your project

```
musiclib-backend/
├── config/
│   ├── settings.py        (replace)
│   ├── urls.py            (replace)
│   └── wsgi.py            (keep default)
├── tracks/
│   ├── models.py          (replace)
│   ├── serializers.py     (create)
│   ├── views.py           (replace)
│   ├── urls.py            (create)
│   ├── admin.py           (replace)
│   └── filters.py         (create)
├── .env                   (create)
├── requirements.txt
└── manage.py
```

### Step 3: Run migrations and create superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Step 4: Access

- Admin: http://localhost:8000/admin/ (upload tracks here)
- API: http://localhost:8000/api/tracks/
- API Docs: http://localhost:8000/api/

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/tracks/ | List all tracks (filterable) |
| GET | /api/tracks/{id}/ | Get track detail |
| GET | /api/tracks/{id}/download/ | Download track (increments counter) |
| GET | /api/tracks/genres/ | List available genres |
| GET | /api/tracks/moods/ | List available moods |

### Query Parameters
- `?genre=lofi` - Filter by genre
- `?mood=calm` - Filter by mood
- `?search=peaceful` - Search title/description
- `?ordering=-download_count` - Sort by popularity
