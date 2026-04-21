#!/usr/bin/env bash
set -euo pipefail

# Descarga librerías (JARs) en ./lib
# - postgresql JDBC: necesario para conectar con Postgres
# - junit console: necesario para ejecutar tests sin Maven/Gradle

mkdir -p lib

POSTGRES_VER="42.7.4"
JUNIT_CONSOLE_VER="1.10.3"

POSTGRES_URL="https://repo1.maven.org/maven2/org/postgresql/postgresql/${POSTGRES_VER}/postgresql-${POSTGRES_VER}.jar"
JUNIT_URL="https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/${JUNIT_CONSOLE_VER}/junit-platform-console-standalone-${JUNIT_CONSOLE_VER}.jar"

if [ ! -f "lib/postgresql-${POSTGRES_VER}.jar" ]; then
  echo "Descargando PostgreSQL JDBC..."
  curl -fsSL "$POSTGRES_URL" -o "lib/postgresql-${POSTGRES_VER}.jar"
fi

if [ ! -f "lib/junit-platform-console-standalone-${JUNIT_CONSOLE_VER}.jar" ]; then
  echo "Descargando JUnit Console..."
  curl -fsSL "$JUNIT_URL" -o "lib/junit-platform-console-standalone-${JUNIT_CONSOLE_VER}.jar"
fi


echo "OK. JARs en ./lib"
