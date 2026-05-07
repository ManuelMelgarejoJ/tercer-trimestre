const API = {
    register: "/api/auth/register/",
    login: "/api/auth/login/",
    logout: "/api/auth/logout/",
    me: "/api/users/me/",
    changePassword: "/api/users/me/password/",
    entries: "/api/library/entries/",
    detail: id => `/api/library/entries/${id}/`,
    catalogSearch: q => `/api/catalog/search/?q=${encodeURIComponent(q)}`,
};

/* UTILS */
function showResponse(data) {
    const viewer = document.getElementById("response-viewer");
    viewer.value = JSON.stringify(data, null, 2);
    // Auto-scroll to response
    // document.getElementById("response-section").scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function updateStatus(id, text, type = "") {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = "status " + type;
    el.classList.remove("hidden");
}

async function request(url, method = "GET", body = null) {
    const options = {
        method,
        credentials: "include",
        headers: { "Content-Type": "application/json" }
    };

    if (body) options.body = JSON.stringify(body);

    try {
        const res = await fetch(url, options);
        let data;
        if (res.status === 204) {
            data = { ok: true };
        } else {
            data = await res.json().catch(() => ({}));
        }
        showResponse(data);
        return { data, status: res.status, ok: res.ok };
    } catch (err) {
        console.error(err);
        return { data: { error: "fetch_error", message: err.message }, ok: false, status: 0 };
    }
}

/* TABS */
document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.onclick = () => {
        const tabId = btn.dataset.tab;
        
        // Update buttons
        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        // Update content
        document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
        document.getElementById(`tab-${tabId}`).classList.add("active");
    };
});

/* AUTH */
document.querySelectorAll("#auth-form button").forEach(btn => {
    btn.onclick = async () => {
        const action = btn.dataset.action;
        const username = document.getElementById("username").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        updateStatus("auth-status", "Procesando...", "warn");

        let res;
        if (action === "register") {
            res = await request(API.register, "POST", { username, password, email });
        } else if (action === "login") {
            res = await request(API.login, "POST", { username, password });
        } else if (action === "logout") {
            res = await request(API.logout, "POST");
        } else if (action === "me") {
            res = await request(API.me);
        }

        if (res.ok) {
            updateStatus("auth-status", action === "logout" ? "Sesión cerrada" : "Éxito", "ok");
            checkUser(); // Update pill
        } else {
            updateStatus("auth-status", res.data.message || "Error", "error");
        }
    };
});

document.getElementById("btn-logout-pill").onclick = async () => {
    await request(API.logout, "POST");
    checkUser();
    updateStatus("auth-status", "Sesión cerrada", "ok");
};

/* PASSWORD */
document.getElementById("password-form").onsubmit = async e => {
    e.preventDefault();
    const current_password = document.getElementById("current-password").value;
    const new_password = document.getElementById("new-password").value;

    updateStatus("password-status", "Cambiando...", "warn");
    const res = await request(API.changePassword, "POST", { current_password, new_password });
    
    if (res.ok) updateStatus("password-status", "Contraseña cambiada", "ok");
    else updateStatus("password-status", res.data.message || "Error", "error");
};

/* CATALOG */
document.getElementById("btn-catalog-search").onclick = searchCatalog;
document.getElementById("catalog-query").onkeypress = e => { if (e.key === "Enter") searchCatalog(); };

async function searchCatalog() {
    const q = document.getElementById("catalog-query").value.trim();
    if (!q) return;

    const resultsDiv = document.getElementById("catalog-results");
    resultsDiv.innerHTML = '<div class="spinner"></div>';
    updateStatus("catalog-status", `Buscando "${q}"...`, "warn");

    const res = await request(API.catalogSearch(q));
    resultsDiv.innerHTML = "";

    if (!res.ok) {
        updateStatus("catalog-status", res.data.message || "Error al buscar", "error");
        return;
    }

    updateStatus("catalog-status", `Se han encontrado ${res.data.length} juegos.`, "ok");

    res.data.forEach(game => {
        const card = document.createElement("div");
        card.className = "game-card";
        
        const thumb = game.thumb 
            ? `<img src="${game.thumb}" class="game-card-thumb" alt="${game.external}">`
            : `<div class="game-card-thumb-placeholder">🎮</div>`;

        card.innerHTML = `
            ${thumb}
            <div class="game-card-body">
                <div class="game-card-title" title="${game.external}">${game.external}</div>
                <div class="game-card-meta">
                    <span class="game-card-score">ID: ${game.gameID}</span>
                    <button class="small game-card-add" data-id="${game.gameID}">Añadir</button>
                </div>
            </div>
        `;

        card.querySelector(".game-card-add").onclick = () => {
            document.getElementById("external-game-id").value = game.gameID;
            // Switch to library tab
            document.querySelector('[data-tab="library"]').click();
            updateStatus("library-status", `Juego seleccionado: ${game.external}`, "ok");
        };

        resultsDiv.appendChild(card);
    });
}

/* LIBRARY ACTIONS */
document.querySelectorAll("[data-entry-action]").forEach(btn => {
    btn.onclick = async () => {
        const action = btn.dataset.entryAction;
        const id = document.getElementById("entry-id").value;
        const external_game_id = document.getElementById("external-game-id").value;
        const status = document.getElementById("status").value;
        const hours_played = Number(document.getElementById("hours-played").value);

        updateStatus("library-status", "Procesando...", "warn");

        let res;
        if (action === "list") res = await request(API.entries);
        else if (action === "detail") res = await request(API.detail(id));
        else if (action === "patch") res = await request(API.detail(id), "PATCH", { hours_played });
        else if (action === "put") res = await request(API.detail(id), "PUT", { external_game_id, status, hours_played });
        else if (action === "delete") res = await request(API.detail(id), "DELETE");

        if (res.ok) {
            updateStatus("library-status", "Operación completada", "ok");
            if (action === "list") renderLibrary(res.data);
        } else {
            updateStatus("library-status", res.data.message || "Error", "error");
        }
    };
});

document.getElementById("btn-create-entry").onclick = async () => {
    const external_game_id = document.getElementById("external-game-id").value;
    const status = document.getElementById("status").value;
    const hours_played = Number(document.getElementById("hours-played").value);

    updateStatus("library-status", "Creando...", "warn");
    const res = await request(API.entries, "POST", { external_game_id, status, hours_played });
    
    if (res.ok) updateStatus("library-status", "Juego añadido a la biblioteca", "ok");
    else updateStatus("library-status", res.data.message || "Error", "error");
};

function renderLibrary(entries) {
    const listDiv = document.getElementById("entries");
    listDiv.innerHTML = "";
    
    if (!Array.isArray(entries)) return;

    entries.forEach(e => {
        const div = document.createElement("div");
        div.className = "entry";
        div.innerHTML = `
            <div class="entry-id">${e.id}</div>
            <div class="entry-info">
                <div class="entry-game">${e.external_game_id}</div>
                <div class="entry-meta">${e.hours_played} horas jugadas</div>
            </div>
            <span class="badge badge-${e.status}">${e.status}</span>
        `;
        div.onclick = () => {
            document.getElementById("entry-id").value = e.id;
            document.getElementById("external-game-id").value = e.external_game_id;
            document.getElementById("status").value = e.status;
            document.getElementById("hours-played").value = e.hours_played;
            updateStatus("library-status", `Seleccionada entrada #${e.id}`, "ok");
        };
        listDiv.appendChild(div);
    });
}

/* MISC */
document.getElementById("btn-clear-response").onclick = () => {
    document.getElementById("response-viewer").value = "";
};

async function checkUser() {
    const pill = document.getElementById("user-pill");
    const nameSpan = document.getElementById("user-pill-name");
    
    const res = await fetch(API.me, { credentials: "include" });
    if (res.ok) {
        const data = await res.json();
        nameSpan.textContent = data.username;
        pill.classList.remove("hidden");
        updateStatus("auth-status", `Bienvenido, ${data.username}`, "ok");
        updateStatus("password-status", "Listo para cambiar contraseña", "ok");
    } else {
        pill.classList.add("hidden");
        updateStatus("password-status", "Necesitas iniciar sesión antes.", "warn");
    }
}

// Init
checkUser();
