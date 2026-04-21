package config;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class JsonUtil {

    public static String escape(String s) {
        // Escapa caracteres básicos para JSON (suficiente para este proyecto).
        if (s == null) return "";
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t");
    }

    public static String jsonObject(Map<String, String> fields) {
        // Construye un JSON objeto a partir de pares clave->valor YA en formato JSON (con comillas si toca).
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        boolean first = true;
        for (Map.Entry<String, String> e : fields.entrySet()) {
            if (!first) sb.append(",");
            first = false;
            sb.append("\"").append(escape(e.getKey())).append("\":").append(e.getValue());
        }
        sb.append("}");
        return sb.toString();
    }

    public static String jsonString(String s) {
        // Devuelve un string JSON con comillas.
        return "\"" + escape(s) + "\"";
    }

    public static String jsonArrayStrings(List<String> items) {
        // Devuelve un array JSON de strings.
        if (items == null) items = new ArrayList<>();
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        for (int i = 0; i < items.size(); i++) {
            if (i > 0) sb.append(",");
            sb.append(jsonString(items.get(i)));
        }
        sb.append("]");
        return sb.toString();
    }
}
