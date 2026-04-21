$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force "lib" | Out-Null

$POSTGRES_VER = "42.7.4"
$JUNIT_CONSOLE_VER = "1.10.3"

$POSTGRES_URL = "https://repo1.maven.org/maven2/org/postgresql/postgresql/$POSTGRES_VER/postgresql-$POSTGRES_VER.jar"
$JUNIT_URL = "https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/$JUNIT_CONSOLE_VER/junit-platform-console-standalone-$JUNIT_CONSOLE_VER.jar"

$pgJar = "lib/postgresql-$POSTGRES_VER.jar"
$junitJar = "lib/junit-platform-console-standalone-$JUNIT_CONSOLE_VER.jar"

if (!(Test-Path $pgJar)) {
  Write-Host "Descargando PostgreSQL JDBC..."
  Invoke-WebRequest -Uri $POSTGRES_URL -OutFile $pgJar
}

if (!(Test-Path $junitJar)) {
  Write-Host "Descargando JUnit Console..."
  Invoke-WebRequest -Uri $JUNIT_URL -OutFile $junitJar
}

Copy-Item $pgJar "lib/postgresql.jar" -Force
Copy-Item $junitJar "lib/junit-platform-console-standalone-1.10.3.jar" -Force

Write-Host "OK. JARs en ./lib"
