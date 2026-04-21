package web;

import com.sun.net.httpserver.HttpExchange;

import java.io.*;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

public class HttpUtil {

    public static String readBody(HttpExchange ex) throws IOException {
        // Lee el body completo como texto UTF-8.
        try (InputStream is = ex.getRequestBody()) {
            return new String(is.readAllBytes(), StandardCharsets.UTF_8);
        }
    }

    public static void sendJson(HttpExchange ex, int status, String json) throws IOException {
        // Envía una respuesta JSON con el status indicado.
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        ex.sendResponseHeaders(status, bytes.length);
        try (OutputStream os = ex.getResponseBody()) {
            os.write(bytes);
        }
    }

    public static Map<String, String> queryParams(HttpExchange ex) {
        // Parsea parámetros de query (?a=1&b=2).
        Map<String, String> out = new HashMap<>();
        String q = ex.getRequestURI().getRawQuery();
        if (q == null || q.isBlank()) return out;

        for (String pair : q.split("&")) {
            if (pair.isBlank()) continue;
            String[] kv = pair.split("=", 2);
            String k = urlDecode(kv[0]);
            String v = kv.length > 1 ? urlDecode(kv[1]) : "";
            out.put(k, v);
        }
        return out;
    }

    private static String urlDecode(String s) {
        // Decodifica URL en UTF-8.
        return URLDecoder.decode(s, StandardCharsets.UTF_8);
    }

    @SuppressWarnings("unchecked")
    public static Map<String, String> routeParams(HttpExchange ex) {
        // Devuelve parámetros extraídos por el router (por ejemplo {id}).
        Object o = ex.getAttribute("routeParams");
        if (o == null) return Map.of();
        return (Map<String, String>) o;
    }
}
