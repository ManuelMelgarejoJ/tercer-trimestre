package domain;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class TaskTest {
    @Test
    void getStatusLabel_completada() {
        // Precondiciones: Crear un objeto Task
        Task t = new Task();
        t.done = true;

        // Llamar al metodo
        String estado = t.getStatusLabel();

        // Comprobaciones: Si done=true, el metodo debe devolver "COMPLETADA"
        System.out.println(estado);
        assertEquals("COMPLETADA", estado);
    }

    @Test
    void getStatusLabel_urgente() {
        // Precondiciones: Crear un objeto Task
        Task t = new Task();
        t.done = false;
        t.priority = 5;

        // Llamar al metodo
        String estado = t.getStatusLabel();

        // Comprobaciones: Si done=false y priority>=4
        // el metodo debe devolver "URGENTE"
        System.out.println(estado);
        assertEquals("URGENTE", estado);
    }

    @Test
    void getStatusLabel_pendiente() {
        // Precondiciones: Crear un objeto Task
        Task t = new Task();
        t.done = false;
        t.priority = 1;

        // Llamar al metodo
        String estado = t.getStatusLabel();

        // Comprobaciones: Si done=false y priority<=4
        // el metodo debe devolver "PENDIENTE"
        System.out.println(estado);
        assertEquals("PENDIENTE", estado);
    }

}
