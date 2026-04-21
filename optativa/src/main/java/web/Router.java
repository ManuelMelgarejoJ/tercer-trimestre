package web;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.util.*;

public class Router implements HttpHandler {

    // Un "route" representa método + patrón + handler.
    private static class Route {
        final String method;
        final String pattern;
        final List<String> parts;
        final HttpHandler handler;

        Route(String method, String pattern, HttpHandler handler) {
            this.method = method;
            this.pattern = pattern;
            this.parts = split(pattern);
            this.handler = handler;
        }
    }

    private final List<Route> routes = new ArrayList<>();

    public void add(String method, String pattern, HttpHandler handler) {
        // Registra una ruta.
        routes.add(new Route(method.toUpperCase(), pattern, handler));
    }

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        // Resuelve la ruta y ejecuta el handler correspondiente.
        String method = exchange.getRequestMethod().toUpperCase();
        String path = exchange.getRequestURI().getPath();

        List<String> pathParts = split(path);

        for (Route r : routes) {
            if (!r.method.equals(method)) continue;
            Map<String, String> params = match(r.parts, pathParts);
            if (params != null) {
                // Guarda params en atributos del exchange para que los handlers los lean.
                exchange.setAttribute("routeParams", params);
                r.handler.handle(exchange);
                return;
            }
        }

        // Si no hay match, 404.
        HttpUtil.sendJson(exchange, 404, "{\"error\":\"not_found\"}");
    }

    private static List<String> split(String path) {
        // Divide el path por "/" ignorando vacíos (mantiene trailing slash como ruta distinta).
        String p = path;
        if (p.startsWith("/")) p = p.substring(1);
        if (p.endsWith("/") && p.length() > 0) p = p.substring(0, p.length() - 1);

        if (p.isEmpty()) return List.of();
        return Arrays.asList(p.split("/"));
    }

    private static Map<String, String> match(List<String> patternParts, List<String> pathParts) {
        // Comprueba si el patrón coincide y extrae parámetros {id}.
        if (patternParts.size() != pathParts.size()) return null;

        Map<String, String> params = new HashMap<>();
        for (int i = 0; i < patternParts.size(); i++) {
            String pp = patternParts.get(i);
            String ap = pathParts.get(i);

            if (pp.startsWith("{") && pp.endsWith("}")) {
                String key = pp.substring(1, pp.length() - 1);
                params.put(key, ap);
            } else {
                if (!pp.equals(ap)) return null;
            }
        }
        return params;
    }
}
