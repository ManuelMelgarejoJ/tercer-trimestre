# steamlike_backend

Backend Django para el proyecto que se realizará en DWES de 2º DAW.

## Arranque del proyecto

### 1) Levantar contenedores
```
docker compose up --build
```

### 2) Migraciones
Para crear las migraciones:
```
docker compose exec web python manage.py makemigrations
```

Para aplicar las migraciones:
```
docker compose exec web python manage.py migrate
```

### 3) Crear superusuario (admin)
```
docker compose exec web python manage.py createsuperuser
```

### 4) Abrir el admin
- Admin: `http://localhost:8000/admin/`

### 5) Health-check
- `GET http://localhost:8000/health/`

## Comandos útiles dentro del contenedor

### Entrar en una shell del contenedor web
```
docker compose exec web bash
```

### Crear una nueva app (ej.: auth_api)
```
docker compose exec web python manage.py startapp auth_api
```

> Recuerda: después hay que añadir la app a `INSTALLED_APPS` y crear/incluir sus `urls.py` si aplica.

## Variables de entorno (.env)
El proyecto carga variables desde `.env` (usado por `docker-compose.yml`).  
En desarrollo, por defecto CORS permite:
- `http://frontend:3000`
- `http://localhost:3000`

Si cambias el frontend, ajusta `DJANGO_CORS_ALLOWED_ORIGINS` y `DJANGO_CSRF_TRUSTED_ORIGINS`.

## Estructura inicial
- `core`: health-check y configuración base
- `library`: modelo `LibraryEntry`

> No hay endpoints API predefinidos (salvo `admin/` y `health/`).

## Despliegue en Render

Este proyecto está preparado para desplegarse como **Web Service** usando el
`Dockerfile`.

### 1) Crear el servicio web

En Render:

1. New + → Web Service.
2. Conecta el repositorio de GitHub.
3. Runtime: Docker.
4. Branch: la rama que vayas a entregar.
5. Health Check Path: `/api/health/`.

Render usará el `Dockerfile`, aplicará migraciones, recogerá estáticos y
arrancará Django con `gunicorn`.

### 2) Conectar la base de datos PostgreSQL

En la base de datos de Render, copia la **Internal Database URL** y añádela en
el Web Service como variable:

```env
DATABASE_URL=postgresql://...
```

No uses `POSTGRES_HOST=db` en Render: `db` solo existe dentro de
`docker-compose` local.

### 3) Variables recomendadas

Configura estas variables en el Web Service:

```env
DEBUG=False
SECRET_KEY=pon_aqui_una_clave_larga
DATABASE_URL=la_internal_database_url_de_render
```

### 4) Comprobar que funciona

Cuando el deploy termine, abre:

```text
https://TU-SERVICIO.onrender.com/api/health/
```

Debe responder:

```json
{"status": "ok"}
```
