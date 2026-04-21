package service;

public class PriorityRules {

    public static int parsePriority(String raw) {
        // Convierte un texto a prioridad (1..5) o lanza error.
        if (raw == null) throw new IllegalArgumentException("priority_null");
        try {
            int p = Integer.parseInt(raw.trim());
            validatePriority(p);
            return p;
        } catch (NumberFormatException ex) {
            throw new IllegalArgumentException("priority_not_number");
        }
    }

    public static void validatePriority(int p) {
        // Lanza error si la prioridad no está en rango.
        if (p < 1 || p > 5) throw new IllegalArgumentException("priority_out_of_range");
    }
}
