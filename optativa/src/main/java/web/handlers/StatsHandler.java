package web.handlers;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import config.JsonUtil;
import domain.Task;
import repo.TaskRepository;
import service.TaskStatsService;
import web.HttpUtil;

import java.io.IOException;
import java.util.List;
import java.util.Map;

public class StatsHandler implements HttpHandler {

    private final TaskRepository repo;
    private final TaskStatsService stats;

    public StatsHandler(TaskRepository repo, TaskStatsService stats) {
        // Recibe repo y servicio de estadísticas.
        this.repo = repo;
        this.stats = stats;
    }

    @Override
    public void handle(HttpExchange ex) throws IOException {
        // Devuelve resumen de estadísticas.
        if (!ex.getRequestMethod().equalsIgnoreCase("GET")) {
            HttpUtil.sendJson(ex, 405, "{\"error\":\"method_not_allowed\"}");
            return;
        }

        try {
            List<Task> all = repo.listTasks(java.util.Optional.empty(), java.util.Optional.empty());

            int total = all.size();
            int done = stats.doneCount(all);
            double ratio = stats.doneRatio(all);

            List<Task> top = stats.topPriority(all, 3);

            StringBuilder topJson = new StringBuilder();
            topJson.append("[");
            for (int i = 0; i < top.size(); i++) {
                if (i > 0) topJson.append(",");
                topJson.append(JsonUtil.jsonString(top.get(i).title));
            }
            topJson.append("]");

            String json = JsonUtil.jsonObject(Map.of(
                    "total", String.valueOf(total),
                    "done", String.valueOf(done),
                    "done_ratio", String.valueOf(ratio),
                    "top_priority_titles", topJson.toString()
            ));

            HttpUtil.sendJson(ex, 200, json);
        } catch (Exception e) {
            e.printStackTrace();
            HttpUtil.sendJson(ex, 500, "{\"error\":\"server_error\"}");
        }
    }
}
