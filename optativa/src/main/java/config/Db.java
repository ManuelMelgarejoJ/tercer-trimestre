package config;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class Db {
    private final String jdbcUrl;
    private final String user;
    private final String password;

    public Db(String host, int port, String dbName, String user, String password) {
        // Construye la URL JDBC a partir de variables separadas.
        this.jdbcUrl = "jdbc:postgresql://" + host + ":" + port + "/" + dbName;
        this.user = user;
        this.password = password;
    }

    public Connection getConnection() throws SQLException {
        // Abre una conexión nueva (suficiente para un proyecto didáctico).
        return DriverManager.getConnection(jdbcUrl, user, password);
    }

    public String getJdbcUrl() {
        // Devuelve la URL JDBC (útil para logs/depuración).
        return jdbcUrl;
    }
}
