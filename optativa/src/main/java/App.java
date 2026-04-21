import com.sun.net.httpserver.HttpServer;
import config.Db;
import config.Env;
import config.Migration;
import repo.TaskRepository;
import service.TaskStatsService;
import web.Router;
import web.handlers.*;

import java.net.InetSocketAddress;

public class App {

    public static void main(String[] args) throws Exception {
        // Lee el puerto desde la variable PORT (en Render la define la plataforma). Si no existe, usa 8080.
        int port = Env.getInt("PORT", 8080);

        // Crea la configuración de DB a partir de variables separadas.
        Db db = new Db(
                Env.get("DB_HOST", "localhost"),
                Env.getInt("DB_PORT", 5432),
                Env.get("DB_NAME", "todo_db"),
                Env.get("DB_USER", "todo_user"),
                Env.get("DB_PASSWORD", "todo_pass")
        );

        // Aplica la "migración" mínima (crea tablas si no existen).
        Migration.runWithRetry(db);

        // Capa de repositorio (JDBC).
        TaskRepository taskRepo = new TaskRepository(db);

        // Servicio para estadísticas (lógica pura: condicionales/bucles).
        TaskStatsService statsService = new TaskStatsService();

        // Crea el servidor HTTP y escucha en 0.0.0.0 (necesario en Docker/Render).
        HttpServer server = HttpServer.create(new InetSocketAddress("0.0.0.0", port), 0);

        // Router: permite mapear rutas con métodos HTTP.
        Router router = new Router();

        // Endpoints.
        router.add("GET", "/api/health/", new HealthHandler());
        router.add("GET", "/api/tasks/", new TasksHandler(taskRepo));
        router.add("POST", "/api/tasks/", new TasksHandler(taskRepo));
        router.add("PATCH", "/api/tasks/{id}/done", new TaskToggleDoneHandler(taskRepo));
        router.add("PATCH", "/api/tasks/{id}/title", new TaskTitleHandler(taskRepo));
        router.add("GET", "/api/stats/summary", new StatsHandler(taskRepo, statsService));

        // Conecta el router al servidor.
        server.createContext("/", router);

        // Arranca el servidor.
        server.start();
        System.out.println("Servidor escuchando en http://0.0.0.0:" + port);
    }
}
