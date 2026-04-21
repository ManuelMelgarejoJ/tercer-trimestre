import org.junit.jupiter.api.Test;

import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

import static org.junit.jupiter.api.Assertions.*;

class HealthEndpointTest {

    @Test
    void healthReturnsOkStatus() throws Exception {
        // Precondiciones
        String url = "http://localhost:8080/api/health";

        // Llamar a la ruta
        HttpURLConnection con = (HttpURLConnection) new URL(url).openConnection();

        // Comprobaciones: Comprobar el código y el estado
        assertEquals(200, con.getResponseCode());
        String body = new String(con.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
        assertTrue(body.contains("ok"));
    }
}


