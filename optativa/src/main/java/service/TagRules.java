package service;

import java.util.*;

public class TagRules {

    public static String normalizeTag(String raw) {
        // Normaliza una etiqueta: recorta, minúsculas y valida caracteres básicos.
        if (raw == null) throw new IllegalArgumentException("tag_null");
        String t = raw.trim().toLowerCase();
        if (t.isEmpty()) throw new IllegalArgumentException("tag_empty");
        if (t.length() > 30) throw new IllegalArgumentException("tag_too_long");
        if (!t.matches("[a-z0-9_-]+")) throw new IllegalArgumentException("tag_invalid_chars");
        return t;
    }

    public static List<String> normalizeAndDeduplicate(List<String> rawTags) {
        // Normaliza una lista de etiquetas y elimina duplicados manteniendo el orden.
        if (rawTags == null) return List.of();

        LinkedHashSet<String> set = new LinkedHashSet<>();
        for (String rt : rawTags) {
            if (rt == null) continue;
            String trimmed = rt.trim();
            if (trimmed.isEmpty()) continue;
            set.add(normalizeTag(trimmed));
        }
        return new ArrayList<>(set);
    }

    public static void validateTagList(List<String> tags) {
        // Valida que no haya demasiadas etiquetas (máximo 5).
        if (tags == null) return;
        if (tags.size() > 5) throw new IllegalArgumentException("too_many_tags");
    }
}
