package config;

public class Env {

    public static String get(String key, String defaultValue) {
        // Devuelve la variable de entorno o un valor por defecto si no existe.
        String v = System.getenv(key);
        return (v == null || v.isBlank()) ? defaultValue : v;
    }

    public static int getInt(String key, int defaultValue) {
        // Devuelve la variable de entorno como entero o un valor por defecto si no se puede convertir.
        String v = System.getenv(key);
        if (v == null || v.isBlank()) return defaultValue;
        try {
            return Integer.parseInt(v.trim());
        } catch (NumberFormatException ex) {
            return defaultValue;
        }
    }
}
