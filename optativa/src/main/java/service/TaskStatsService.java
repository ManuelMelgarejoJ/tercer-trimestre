package service;

import domain.Task;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class TaskStatsService {

    public double doneRatio(List<Task> tasks) {
        // Calcula el ratio de tareas completadas (0..1).
        if (tasks == null || tasks.isEmpty()) return 0.0;

        int done = 0;
        for (Task t : tasks) {
            if (t.done) done++;
        }
        return (double) done / tasks.size();
    }

    public int doneCount(List<Task> tasks) {
        // Cuenta cuántas tareas están completadas.
        if (tasks == null || tasks.isEmpty()) return 0;

        int done = 0;
        for (Task t : tasks) {
            if (t.done) done++;
        }
        return done;
    }

    public List<Task> topPriority(List<Task> tasks, int n) {
        // Devuelve las N tareas con mayor prioridad.
        if (tasks == null || tasks.isEmpty() || n <= 0) return List.of();

        ArrayList<Task> copy = new ArrayList<>(tasks);
        copy.sort(Comparator.comparingInt((Task t) -> t.priority).reversed());
        return copy.subList(0, Math.min(n, copy.size()));
    }
}
