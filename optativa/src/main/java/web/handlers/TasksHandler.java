package web.handlers;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import config.JsonUtil;
import domain.Task;
import repo.TaskRepository;
import web.HttpUtil;

import java.io.IOException;
import java.util.*;

public class TasksHandler implements HttpHandler {

    private final TaskRepository repo;

    public TasksHandler(TaskRepository repo) {
        // Recibe el repositorio para acceder a BD.
        this.repo = repo;
    }

    @Override
    public void handle(HttpExchange ex) throws IOException {
        // Maneja GET (listar) y POST (crear).
        String method = ex.getRequestMethod().toUpperCase();

        try {
            if (method.equals("GET")) {
                handleList(ex);
                return;
            }
            if (method.equals("POST")) {
                handleCreate(ex);
                return;
            }
            HttpUtil.sendJson(ex, 405, "{\"error\":\"method_not_allowed\"}");
        } catch (IllegalArgumentException iae) {
            // Errores de validación -> 400
            HttpUtil.sendJson(ex, 400, "{\"error\":\"validation_error\",\"code\":" + JsonUtil.jsonString(iae.getMessage()) + "}");
        } catch (Exception e) {
            e.printStackTrace();
            HttpUtil.sendJson(ex, 500, "{\"error\":\"server_error\"}");
        }
    }

    private void handleList(HttpExchange ex) throws Exception {
        // Lista tareas con filtros opcionales (?done=true/false y/o ?tag=xxx).
        Map<String, String> q = HttpUtil.queryParams(ex);

        Optional<Boolean> done = Optional.empty();
        if (q.containsKey("done")) {
            String v = q.get("done").trim().toLowerCase();
            if (v.equals("true")) done = Optional.of(true);
            else if (v.equals("false")) done = Optional.of(false);
            else throw new IllegalArgumentException("done_invalid");
        }

        Optional<String> tag = Optional.empty();
        if (q.containsKey("tag") && !q.get("tag").isBlank()) {
            tag = Optional.of(q.get("tag"));
        }

        List<Task> tasks = repo.listTasks(done, tag);

        HttpUtil.sendJson(ex, 200, tasksToJson(tasks));
    }

    private void handleCreate(HttpExchange ex) throws Exception {
        // Crea una tarea a partir de JSON.
        String body = HttpUtil.readBody(ex);

        String title = SimpleJson.getString(body, "title");
        Integer priority = SimpleJson.getInt(body, "priority");
        List<String> tags = SimpleJson.getStringArray(body, "tags");

        if (title == null) throw new IllegalArgumentException("title_missing");
        if (priority == null) throw new IllegalArgumentException("priority_missing");

        Task created = repo.createTask(title, priority, tags);

        HttpUtil.sendJson(ex, 201, taskToJson(created));
    }

    private String tasksToJson(List<Task> tasks) {
        // Convierte lista de tareas a JSON.
        StringBuilder sb = new StringBuilder();
        sb.append("{\"tasks\":[");
        for (int i = 0; i < tasks.size(); i++) {
            if (i > 0) sb.append(",");
            sb.append(taskToJson(tasks.get(i)));
        }
        sb.append("]}");
        return sb.toString();
    }

    private String taskToJson(Task t) {
        // Convierte una tarea a JSON.
        String tagsJson = JsonUtil.jsonArrayStrings(t.tags == null ? List.of() : t.tags);

        return "{"
                + "\"id\":" + t.id + ","
                + "\"title\":" + JsonUtil.jsonString(t.title) + ","
                + "\"done\":" + (t.done ? "true" : "false") + ","
                + "\"priority\":" + t.priority + ","
                + "\"created_at\":" + JsonUtil.jsonString(t.createdAt.toString()) + ","
                + "\"tags\":" + tagsJson
                + "}";
    }
}
