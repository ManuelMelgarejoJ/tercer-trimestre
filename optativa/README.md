# ToDo (Java + PostgreSQL + Docker)

Aplicación: una API HTTP de tareas (ToDo) con bases de datos PostgreSQL.

## Requisitos
- Docker y Docker Compose (recomendado para local)
- (Opcional) Java 17 si quieres ejecutar fuera de Docker
---

## Variables de entorno
La app usa variables:
- `PORT` (puerto HTTP)
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

En local, `docker-compose.yml` ya las configura.
---

## 1) Ejecutar en local (Docker Compose)

### Arrancar
```
docker compose up --build
```

La API quedará en:
- http://localhost:8080

### Probar endpoints rápido (curl)
Health:
```
curl -i http://localhost:8080/api/health/
```

Crear tarea:
```
curl -i -X POST http://localhost:8080/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Comprar pan","priority":3,"tags":["casa","recados"]}'
```

Listar tareas:
```
curl -i http://localhost:8080/api/tasks/
```

Filtrar por done:
```
curl -i "http://localhost:8080/api/tasks/?done=true"
```

Filtrar por tag:
```
curl -i "http://localhost:8080/api/tasks/?tag=casa"
```

Toggle done:
```
curl -i -X PATCH http://localhost:8080/api/tasks/1/done
```

Cambiar título:
```
curl -i -X PATCH http://localhost:8080/api/tasks/1/title \
  -H "Content-Type: application/json" \
  -d '{"title":"Comprar pan integral"}'
```

Stats:
```
curl -i http://localhost:8080/api/stats/summary
```

### Parar
```
docker compose down
```

> Nota: el volumen de Postgres se mantiene para no perder datos.
Para borrarlo:
```
docker compose down -v
```

---

## 2) Ejecutar fuera de Docker (opcional)

### Descargar librerías (JDBC Postgres y JUnit para tests)
En Linux/Mac:
```
bash scripts/download-libs.sh
```

En Windows (PowerShell):
```powershell
powershell -ExecutionPolicy Bypass -File scripts\download-libs.ps1
```

### Compilar
Linux/Mac:
```
mkdir -p out/main
find src/main/java -name "*.java" > sources.txt
javac -cp "lib/*" -d out/main @sources.txt
```

Windows (PowerShell):
```
New-Item -ItemType Directory -Force out\main | Out-Null
Get-ChildItem -Recurse src\main\java -Filter *.java | ForEach-Object { $_.FullName } | Set-Content sources.txt
javac -cp "lib/*" -d out\main @sources.txt
```

### Ejecutar
Define variables de entorno (ejemplo Linux/Mac):
```
export PORT=8080
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=todo_db
export DB_USER=todo_user
export DB_PASSWORD=todo_pass
java -cp "lib/*:out/main" App
```

---

## 3) Tests

Hay ejemplos de tests en `src/test/java`.

### Descargar JUnit (si no lo has hecho)
```
bash scripts/download-libs.sh
```

### Compilar tests y ejecutar
Linux/Mac:
#### 1) Compilar MAIN
```
mkdir -p out/main
find src/main/java -name "*.java" > sources.txt
javac -cp "lib/*" -d out/main @sources.txt
```
#### 2) Compilar TESTS
```
mkdir -p out/test
find src/test/java -name "*.java" > test-sources.txt
javac -cp "lib/*:out/main" -d out/test @test-sources.txt
```

#### 3) Ejecutar TESTS
```
java -jar lib/junit-platform-console-standalone-1.10.3.jar \
  -cp "lib/*:out/main:out/test" \
  --scan-classpath
```

En Windows:
#### 1) Compilar MAIN
```
New-Item -ItemType Directory -Force out\main | Out-Null
Get-ChildItem -Recurse src\main\java -Filter *.java | ForEach-Object { $_.FullName } | Set-Content sources.txt
javac -cp "lib/*" -d out\main @sources.txt
```

#### 2) Compilar TESTS
```
New-Item -ItemType Directory -Force out\test | Out-Null
Get-ChildItem -Recurse src\test\java -Filter *.java | ForEach-Object { $_.FullName } | Set-Content test-sources.txt
javac -cp "lib/*;out\main" -d out\test @test-sources.txt
```

#### 3) Ejecutar TESTS
```
java -jar lib\junit-platform-console-standalone-1.10.3.jar `
  -cp "lib/*;out\main;out\test" `
--scan-classpath
```

---

## 4) Notas para despliegue (Render)
- La app lee `PORT` y escucha en `0.0.0.0`.
- En Render, define las variables `DB_*` (separadas) y `PORT` la aporta Render.
- El `Dockerfile` ya construye la app dentro de la imagen con `javac`.

---

## Estructura del proyecto
- `src/main/java`: código de la app
- `src/test/java`: tests (JUnit)
- `scripts/`: descarga de librerías para ejecución fuera de Docker
- `Dockerfile`: build y runtime con Java 17
- `docker-compose.yml`: Postgres + app para local


# Endpoints de la aplicación

Base URL (local):

```
http://localhost:8080
```

---

## Health check

### GET `/api/health/`

Comprueba que la aplicación está en ejecución.

**Ejemplo**

```
curl http://localhost:8080/api/health/
```

**Respuesta**

```
{ "status": "ok" }
```

---

## Tareas

### POST `/api/tasks/`

Crea una nueva tarea.

**Body**

```
{
  "title": "Comprar pan",
  "priority": 3,
  "tags": ["casa", "recados"]
}
```

**Ejemplo**

```
curl -X POST http://localhost:8080/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Comprar pan","priority":3,"tags":["casa","recados"]}'
```

**Respuesta**

```
{
  "id": 1,
  "title": "Comprar pan",
  "done": false,
  "priority": 3,
  "created_at": "2026-01-05T10:20:30Z",
  "tags": ["casa", "recados"]
}
```

---

### GET `/api/tasks/`

Devuelve todas las tareas.

**Ejemplo**

```
curl http://localhost:8080/api/tasks/
```

---

### GET `/api/tasks/?done=true`

Filtra tareas por estado (`true` o `false`).

**Ejemplo**

```
curl "http://localhost:8080/api/tasks/?done=false"
```

---

### GET `/api/tasks/?tag=casa`

Filtra tareas por etiqueta.

**Ejemplo**

```
curl "http://localhost:8080/api/tasks/?tag=casa"
```

---

## Cambiar estado de una tarea

### PATCH `/api/tasks/{id}/done`

Cambia el estado `done` de una tarea.

**Ejemplo**

```
curl -X PATCH http://localhost:8080/api/tasks/1/done
```

**Respuesta**

```
{ "ok": true }
```

---

## Cambiar título de una tarea

### PATCH `/api/tasks/{id}/title`

Modifica el título de una tarea.

**Body**

```
{
  "title": "Comprar pan integral"
}
```

**Ejemplo**

```
curl -X PATCH http://localhost:8080/api/tasks/1/title \
  -H "Content-Type: application/json" \
  -d '{"title":"Comprar pan integral"}'
```

---

## Estadísticas

### GET `/api/stats/summary`

Devuelve un resumen simple de las tareas.

**Ejemplo**

```
curl http://localhost:8080/api/stats/summary
```

**Respuesta**

```
{
  "total": 5,
  "done": 2,
  "done_ratio": 0.4,
  "top_priority_titles": ["Examen", "Entrega práctica", "Comprar pan"]
}
```

