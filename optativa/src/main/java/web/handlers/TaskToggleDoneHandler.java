package web.handlers;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import repo.TaskRepository;
import web.HttpUtil;

import java.io.IOException;
import java.util.Map;

public class TaskToggleDoneHandler implements HttpHandler {

    private final TaskRepository repo;

    public TaskToggleDoneHandler(TaskRepository repo) {
        // Recibe el repositorio para acceder a BD.
        this.repo = repo;
    }

    @Override
    public void handle(HttpExchange ex) throws IOException {
        // Cambia el estado done de una tarea.
        if (!ex.getRequestMethod().equalsIgnoreCase("PATCH")) {
            HttpUtil.sendJson(ex, 405, "{\"error\":\"method_not_allowed\"}");
            return;
        }

        try {
            Map<String, String> params = HttpUtil.routeParams(ex);
            int id = Integer.parseInt(params.getOrDefault("id", "0"));

            if (id <= 0) {
                HttpUtil.sendJson(ex, 400, "{\"error\":\"validation_error\",\"code\":\"id_invalid\"}");
                return;
            }

            boolean updated = repo.toggleDone(id);
            if (!updated) {
                HttpUtil.sendJson(ex, 404, "{\"error\":\"not_found\"}");
                return;
            }

            HttpUtil.sendJson(ex, 200, "{\"ok\":true}");
        } catch (NumberFormatException nfe) {
            HttpUtil.sendJson(ex, 400, "{\"error\":\"validation_error\",\"code\":\"id_invalid\"}");
        } catch (Exception e) {
            e.printStackTrace();
            HttpUtil.sendJson(ex, 500, "{\"error\":\"server_error\"}");
        }
    }
}
