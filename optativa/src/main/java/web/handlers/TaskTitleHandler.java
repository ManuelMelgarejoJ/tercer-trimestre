package web.handlers;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import config.JsonUtil;
import repo.TaskRepository;
import web.HttpUtil;

import java.io.IOException;
import java.util.Map;

public class TaskTitleHandler implements HttpHandler {

    private final TaskRepository repo;

    public TaskTitleHandler(TaskRepository repo) {
        // Recibe el repositorio para acceder a BD.
        this.repo = repo;
    }

    @Override
    public void handle(HttpExchange ex) throws IOException {
        // Actualiza el título de una tarea.
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

            String body = HttpUtil.readBody(ex);
            String title = SimpleJson.getString(body, "title");
            if (title == null) {
                HttpUtil.sendJson(ex, 400, "{\"error\":\"validation_error\",\"code\":\"title_missing\"}");
                return;
            }

            boolean updated = repo.updateTitle(id, title);
            if (!updated) {
                HttpUtil.sendJson(ex, 404, "{\"error\":\"not_found\"}");
                return;
            }

            HttpUtil.sendJson(ex, 200, "{\"ok\":true}");
        } catch (NumberFormatException nfe) {
            // El id no es un número.
            HttpUtil.sendJson(ex, 400, "{\"error\":\"validation_error\",\"code\":\"id_invalid\"}");
        } catch (IllegalArgumentException iae) {
            // Errores de validación (por ejemplo, título inválido).
            HttpUtil.sendJson(ex, 400, "{\"error\":\"validation_error\",\"code\":" + JsonUtil.jsonString(iae.getMessage()) + "}");
        } catch (Exception e) {
            e.printStackTrace();
            HttpUtil.sendJson(ex, 500, "{\"error\":\"server_error\"}");
        }
    }
}
