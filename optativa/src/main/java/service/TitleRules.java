package service;

public class TitleRules {

    public static String normalizeTitle(String raw) {
        // Normaliza un título: recorta y convierte múltiples espacios en uno.
        if (raw == null) throw new IllegalArgumentException("title_null");
        return raw.trim().replaceAll("\\s+", " ");
    }

    public static void validateTitle(String normalized) {
        // Valida que el título sea correcto (no vacío, <= 60).
        if (normalized == null) throw new IllegalArgumentException("title_null");
        if (normalized.isBlank()) throw new IllegalArgumentException("title_empty");
        if (normalized.length() > 60) throw new IllegalArgumentException("title_too_long");
    }
}
