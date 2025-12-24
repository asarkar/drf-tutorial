This repository contains practice code for the official [Django REST Framework Tutorial](https://www.django-rest-framework.org/tutorial/1-serialization/).

[![](https://github.com/asarkar/drf-tutorial/workflows/CI/badge.svg)](https://github.com/asarkar/drf-tutorial/actions)

Each chapter of the tutorial is implemented in its own directory, allowing you to explore the progression from basic serialization to viewsets and routers.

**Note:** Comprehensive unit tests have been added for models, serializers, and views, which the original tutorial does not cover.

## Syllabus

1. [**Serialization**](1-serialization/) - Introduction to serializers, creating a basic Web API with Django views
2. [**Requests and Responses**](2-requests-and-responses/) - Using DRF's Request/Response objects, `@api_view` decorator, format suffixes
3. [**Class-based Views**](3-class-based-views/) - Refactoring to class-based views using `APIView` and generic views
4. [**Authentication and Permissions**](4-authentication-and-permissions/) - Adding user authentication, object-level permissions, login support
5. [**Relationships and Hyperlinked APIs**](5-relationships-and-hyperlinked-apis/) - Using `HyperlinkedModelSerializer`, API root endpoint, pagination
6. [**Viewsets and Routers**](6-viewsets-and-routers/) - Refactoring to ViewSets and automatic URL routing

## API Endpoints

### Snippets API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/snippets/` | List all snippets |
| GET | `/snippets.json` | List all snippets (JSON) |
| GET | `/snippets.api` | List all snippets (Browsable API) |
| POST | `/snippets/` | Create a new snippet |
| GET | `/snippets/{id}/` | Retrieve a snippet |
| GET | `/snippets/{id}.json` | Retrieve a snippet (JSON) |
| GET | `/snippets/{id}.api` | Retrieve a snippet (Browsable API) |
| PUT | `/snippets/{id}/` | Update a snippet |
| PATCH | `/snippets/{id}/` | Partial update a snippet |
| DELETE | `/snippets/{id}/` | Delete a snippet |
| GET | `/snippets/{id}/highlight/` | Get highlighted HTML (chapters 5-6) |

### Users API (chapters 4-6)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/` | List all users |
| GET | `/users.json` | List all users (JSON) |
| GET | `/users.api` | List all users (Browsable API) |
| GET | `/users/{id}/` | Retrieve a user |
| GET | `/users/{id}.json` | Retrieve a user (JSON) |
| GET | `/users/{id}.api` | Retrieve a user (Browsable API) |

### Other Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root with hyperlinks (chapters 5-6) |
| GET | `/.api` | API root (Browsable API) |
| GET | `/api-auth/login/` | Browsable API login |

## Technologies

- **Django** - Web framework
- **Django REST Framework** - REST API toolkit
- **Pygments** - Code syntax highlighting
- **uv** - Python package and project manager
- **ruff** - Linting

## Development

### Setup

```bash
# Install dependencies
uv sync

# Activate virtual environment (optional, uv run handles this)
source .venv/bin/activate
```

### Running a Chapter

```bash
# Run migrations
uv run --directory <chapter>/ manage.py migrate

# Start development server
uv run --directory <chapter>/ manage.py runserver
```

Example:
```bash
uv run --directory 1-serialization manage.py migrate
uv run --directory 1-serialization manage.py runserver
```

### Running Tests

```bash
# Run tests for a specific chapter
uv run --directory <chapter>/ manage.py test

# Or use the CI script
./.github/run.sh <chapter>/
```

Example:
```bash
uv run --directory 4-authentication-and-permissions manage.py test
```
