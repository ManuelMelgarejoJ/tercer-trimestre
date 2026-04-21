# Etapa 1: build
FROM eclipse-temurin:17-jdk AS build
WORKDIR /app

# Utilidades para descargar el driver JDBC de PostgreSQL
RUN apt-get update -y && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Copiamos código
COPY src ./src
COPY scripts ./scripts

# Descargamos librerías necesarias para compilar/ejecutar (driver JDBC)
RUN bash scripts/download-libs.sh

# Compilamos el código de la app
RUN mkdir -p /app/out/main && find src/main/java -name "*.java" > sources.txt && javac -cp "lib/*" -d /app/out/main @sources.txt

# Etapa 2: runtime (solo JRE)
FROM eclipse-temurin:17-jre
WORKDIR /app

# Copiamos clases compiladas y librerías runtime (postgresql jar)
COPY --from=build /app/out/main ./out/main
COPY --from=build /app/lib ./lib

EXPOSE 8080

# Ejecuta la clase principal
CMD ["java", "-cp", "lib/*:out/main", "App"]
