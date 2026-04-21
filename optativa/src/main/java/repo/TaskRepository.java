package repo;

import config.Db;
import domain.Task;
import service.PriorityRules;
import service.TagRules;
import service.TitleRules;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class TaskRepository {
    private final Db db;

    public TaskRepository(Db db) {
        // Guarda la configuración de base de datos.
        this.db = db;
    }

    public Task createTask(String rawTitle, int priority, List<String> rawTags) throws Exception {
        // Crea una tarea y sus etiquetas (si existen).
        String title = TitleRules.normalizeTitle(rawTitle);
        TitleRules.validateTitle(title);
        PriorityRules.validatePriority(priority);

        List<String> tags = TagRules.normalizeAndDeduplicate(rawTags);
        TagRules.validateTagList(tags);

        try (Connection c = db.getConnection()) {
            c.setAutoCommit(false);

            int taskId;
            try (PreparedStatement ps = c.prepareStatement(
                    "INSERT INTO tasks(title, done, priority) VALUES (?, FALSE, ?) RETURNING id"
            )) {
                ps.setString(1, title);
                ps.setInt(2, priority);
                try (ResultSet rs = ps.executeQuery()) {
                    rs.next();
                    taskId = rs.getInt(1);
                }
            }

            // Inserta etiquetas si existen (con bucle).
            for (String tag : tags) {
                int tagId = upsertTag(c, tag);
                linkTaskTag(c, taskId, tagId);
            }

            c.commit();

            // Devuelve el objeto completo.
            return getTaskById(taskId).orElseThrow();
        } catch (Exception ex) {
            throw ex;
        }
    }

    private int upsertTag(Connection c, String normalizedTag) throws Exception {
        // Crea una etiqueta si no existe, y devuelve su id.
        // 1) intenta insertar
        try (PreparedStatement ps = c.prepareStatement(
                "INSERT INTO tags(name) VALUES (?) ON CONFLICT (name) DO NOTHING RETURNING id"
        )) {
            ps.setString(1, normalizedTag);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return rs.getInt(1);
                }
            }
        }

        // 2) si no se insertó (ya existía), la buscamos
        try (PreparedStatement ps2 = c.prepareStatement("SELECT id FROM tags WHERE name = ?")) {
            ps2.setString(1, normalizedTag);
            try (ResultSet rs2 = ps2.executeQuery()) {
                rs2.next();
                return rs2.getInt(1);
            }
        }
    }

    private void linkTaskTag(Connection c, int taskId, int tagId) throws Exception {
        // Relaciona task con tag evitando duplicados.
        try (PreparedStatement ps = c.prepareStatement(
                "INSERT INTO task_tags(task_id, tag_id) VALUES (?, ?) ON CONFLICT DO NOTHING"
        )) {
            ps.setInt(1, taskId);
            ps.setInt(2, tagId);
            ps.executeUpdate();
        }
    }

    public List<Task> listTasks(Optional<Boolean> done, Optional<String> tag) throws Exception {
        // Lista tareas con filtros opcionales (done y/o tag).
        List<Task> tasks = new ArrayList<>();

        StringBuilder sql = new StringBuilder();
        sql.append("SELECT t.id, t.title, t.done, t.priority, t.created_at ");
        sql.append("FROM tasks t ");

        if (tag.isPresent()) {
            sql.append("JOIN task_tags tt ON tt.task_id = t.id ");
            sql.append("JOIN tags g ON g.id = tt.tag_id ");
        }

        List<Object> params = new ArrayList<>();
        List<String> where = new ArrayList<>();

        if (done.isPresent()) {
            where.add("t.done = ?");
            params.add(done.get());
        }
        if (tag.isPresent()) {
            where.add("g.name = ?");
            params.add(TagRules.normalizeTag(tag.get()));
        }

        if (!where.isEmpty()) {
            sql.append("WHERE ").append(String.join(" AND ", where)).append(" ");
        }

        sql.append("ORDER BY t.id ASC");

        try (Connection c = db.getConnection();
             PreparedStatement ps = c.prepareStatement(sql.toString())) {

            // Asigna parámetros (bucle).
            for (int i = 0; i < params.size(); i++) {
                Object p = params.get(i);
                if (p instanceof Boolean b) ps.setBoolean(i + 1, b);
                else ps.setString(i + 1, String.valueOf(p));
            }

            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    int id = rs.getInt("id");
                    tasks.add(new Task(
                            id,
                            rs.getString("title"),
                            rs.getBoolean("done"),
                            rs.getInt("priority"),
                            rs.getTimestamp("created_at").toInstant(),
                            getTagsForTask(c, id)
                    ));
                }
            }
        }

        return tasks;
    }

    public Optional<Task> getTaskById(int id) throws Exception {
        // Devuelve una tarea por id (si existe).
        try (Connection c = db.getConnection();
             PreparedStatement ps = c.prepareStatement(
                     "SELECT id, title, done, priority, created_at FROM tasks WHERE id = ?"
             )) {
            ps.setInt(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (!rs.next()) return Optional.empty();

                return Optional.of(new Task(
                        rs.getInt("id"),
                        rs.getString("title"),
                        rs.getBoolean("done"),
                        rs.getInt("priority"),
                        rs.getTimestamp("created_at").toInstant(),
                        getTagsForTask(c, id)
                ));
            }
        }
    }

    public boolean toggleDone(int id) throws Exception {
        // Cambia el estado done (true/false) y devuelve si se actualizó alguna fila.
        try (Connection c = db.getConnection();
             PreparedStatement ps = c.prepareStatement(
                     "UPDATE tasks SET done = NOT done WHERE id = ?"
             )) {
            ps.setInt(1, id);
            int updated = ps.executeUpdate();
            return updated == 1;
        }
    }

    public boolean updateTitle(int id, String rawTitle) throws Exception {
        // Actualiza el título de la tarea con validación y normalización.
        String title = TitleRules.normalizeTitle(rawTitle);
        TitleRules.validateTitle(title);

        try (Connection c = db.getConnection();
             PreparedStatement ps = c.prepareStatement(
                     "UPDATE tasks SET title = ? WHERE id = ?"
             )) {
            ps.setString(1, title);
            ps.setInt(2, id);
            int updated = ps.executeUpdate();
            return updated == 1;
        }
    }

    private List<String> getTagsForTask(Connection c, int taskId) throws Exception {
        // Devuelve las etiquetas asociadas a una tarea.
        List<String> tags = new ArrayList<>();
        try (PreparedStatement ps = c.prepareStatement(
                "SELECT g.name FROM tags g JOIN task_tags tt ON tt.tag_id = g.id WHERE tt.task_id = ? ORDER BY g.name ASC"
        )) {
            ps.setInt(1, taskId);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    tags.add(rs.getString(1));
                }
            }
        }
        return tags;
    }
}
