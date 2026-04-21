package web.handlers;

import java.util.ArrayList;
import java.util.List;

/**
 * Parseo JSON MUY simple para este proyecto.
 * - No es un parser general.
 * - Soporta: strings, enteros y arrays de strings.
 * - Está pensado para 1.º y para tests.
 *
 * Importante: asume JSON "simple" (sin escapes complejos).
 */
public class SimpleJson {

    public static String getString(String json, String key) {
        // Devuelve el valor de una clave string o null.
        if (json == null || key == null) return null;

        String needle = "\"" + key + "\"";
        int k = json.indexOf(needle);
        if (k < 0) return null;

        int colon = json.indexOf(':', k + needle.length());
        if (colon < 0) return null;

        int firstQuote = json.indexOf('"', colon + 1);
        if (firstQuote < 0) return null;

        int secondQuote = json.indexOf('"', firstQuote + 1);
        if (secondQuote < 0) return null;

        return json.substring(firstQuote + 1, secondQuote);
    }

    public static Integer getInt(String json, String key) {
        // Devuelve el valor entero de una clave o null.
        if (json == null || key == null) return null;

        String needle = "\"" + key + "\"";
        int k = json.indexOf(needle);
        if (k < 0) return null;

        int colon = json.indexOf(':', k + needle.length());
        if (colon < 0) return null;

        int start = colon + 1;
        while (start < json.length() && Character.isWhitespace(json.charAt(start))) start++;

        int end = start;
        while (end < json.length()) {
            char c = json.charAt(end);
            if (c == ',' || c == '}' || Character.isWhitespace(c)) break;
            end++;
        }

        String raw = json.substring(start, end).trim();
        if (raw.isEmpty()) return null;

        try {
            return Integer.parseInt(raw);
        } catch (NumberFormatException ex) {
            return null;
        }
    }

    public static List<String> getStringArray(String json, String key) {
        // Devuelve un array de strings o una lista vacía.
        if (json == null || key == null) return List.of();

        String needle = "\"" + key + "\"";
        int k = json.indexOf(needle);
        if (k < 0) return List.of();

        int colon = json.indexOf(':', k + needle.length());
        if (colon < 0) return List.of();

        int open = json.indexOf('[', colon + 1);
        if (open < 0) return List.of();

        int close = json.indexOf(']', open + 1);
        if (close < 0) return List.of();

        String inside = json.substring(open + 1, close).trim();
        if (inside.isEmpty()) return List.of();

        ArrayList<String> out = new ArrayList<>();
        String[] parts = inside.split(",");
        for (String p : parts) {
            String t = p.trim();
            // Quitamos comillas si las hay.
            if (t.startsWith("\"")) t = t.substring(1);
            if (t.endsWith("\"")) t = t.substring(0, t.length() - 1);
            if (!t.isEmpty()) out.add(t);
        }
        return out;
    }
}
