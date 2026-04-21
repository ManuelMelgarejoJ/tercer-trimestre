package web.handlers;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import web.HttpUtil;

import java.io.IOException;

public class HealthHandler implements HttpHandler {

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        // Devuelve estado de salud.
        if (!exchange.getRequestMethod().equalsIgnoreCase("GET")) {
            HttpUtil.sendJson(exchange, 405, "{\"error\":\"method_not_allowed\"}");
            return;
        }
        HttpUtil.sendJson(exchange, 200, "{\"status\":\"ok\"}");
    }
}
