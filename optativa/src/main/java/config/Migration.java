package config;

import java.sql.Connection;
import java.sql.Statement;

public class Migration {

    public static void run(Db db) throws Exception {
        // Crea tablas si no existen (migración mínima).
        try (Connection c = db.getConnection();
             Statement st = c.createStatement()) {

            st.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                  id SERIAL PRIMARY KEY,
                  title VARCHAR(60) NOT NULL,
                  done BOOLEAN NOT NULL DEFAULT FALSE,
                  priority INT NOT NULL,
                  created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """);

            st.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                  id SERIAL PRIMARY KEY,
                  name VARCHAR(30) NOT NULL UNIQUE
                );
            """);

            st.execute("""
                CREATE TABLE IF NOT EXISTS task_tags (
                  task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                  tag_id INT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                  PRIMARY KEY (task_id, tag_id)
                );
            """);
        }
    }

    public static void runWithRetry(Db db) throws Exception {
        // Reintenta la migración unos segundos (útil porque Postgres puede tardar en arrancar).
        int maxAttempts = 20;
        long sleepMs = 500;

        Exception last = null;

        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                run(db);
                return;
            } catch (Exception ex) {
                last = ex;
                System.out.println("DB aún no lista (intento " + attempt + "/" + maxAttempts + "). Reintentando...");
                try {
                    Thread.sleep(sleepMs);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw ex;
                }
            }
        }

        // Si no se pudo conectar tras varios intentos, propagamos el último error.
        throw last;
    }
}
