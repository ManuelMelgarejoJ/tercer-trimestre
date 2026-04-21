package domain;

import java.time.Instant;
import java.util.List;

public class Task {
    // Identificador de la tarea (BD).
    public int id;

    // Título de la tarea.
    public String title;

    // Indica si está completada.
    public boolean done;

    // Prioridad (1..5).
    public int priority;

    // Fecha de creación.
    public Instant createdAt;

    // Lista de etiquetas asociadas.
    public List<String> tags;

    public Task() {
        // Constructor vacío.
    }

    public Task(int id, String title, boolean done, int priority, Instant createdAt, List<String> tags) {
        // Constructor de conveniencia.
        this.id = id;
        this.title = title;
        this.done = done;
        this.priority = priority;
        this.createdAt = createdAt;
        this.tags = tags;
    }

    public String getStatusLabel() {
        if (done) {
            return "COMPLETADA";
        } else if (priority >= 4) {
            return "URGENTE";
        } else {
            return "PENDIENTE";
        }
    }

}
