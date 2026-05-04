const API = {
    register: "/api/auth/register/",
    login: "/api/auth/login/",
    logout: "/api/auth/logout/",
    me: "/api/users/me/",
    changePassword: "/api/users/me/password/",
    deleteAccount: "/api/users/me/delete/",
    entries: "/api/library/entries/",
    list: "/api/library/entries/list/",
    detail: id => `/api/library/entries/${id}/`,
    patch: id => `/api/library/entries/${id}/patch/`,
    put: id => `/api/library/entries/${id}/put/`,
    delete: id => `/api/library/entries/${id}/delete/`,
};

function showResponse(data) {
    document.getElementById("response-viewer").value = JSON.stringify(data, null, 2);
}

async function request(url, method="GET", body=null) {
    const options = {
        method,
        credentials: "include",
        headers: { "Content-Type": "application/json" }
    };

    if (body) options.body = JSON.stringify(body);

    const res = await fetch(url, options);
    const data = await res.json().catch(() => ({}));
    showResponse(data);
    return data;
}

/* AUTH */
document.querySelectorAll("#auth-form button").forEach(btn => {
    btn.onclick = async () => {
        const action = btn.dataset.action;
        const username = document.getElementById("username").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        let data;

        if (action === "register") {
            if (!email) {
                data = {
                    error: "validation_error",
                    message: "Introduce un correo electronico para registrarte",
                };
                showResponse(data);
                document.getElementById("auth-status").textContent = JSON.stringify(data);
                return;
            }
            data = await request(API.register, "POST", { username, password, email });
        }

        if (action === "login")
            data = await request(API.login, "POST", { username, password });

        if (action === "logout")
            data = await request(API.logout, "POST");

        if (action === "me")
            data = await request(API.me);

        document.getElementById("auth-status").textContent = JSON.stringify(data);
    };
});

/* PASSWORD */
document.getElementById("password-form").onsubmit = async e => {
    e.preventDefault();

    const current_password = document.getElementById("current-password").value;
    const new_password = document.getElementById("new-password").value;

    const data = await request(API.changePassword, "POST", {
        current_password,
        new_password
    });

    document.getElementById("password-status").textContent = JSON.stringify(data);
};

/* LIBRARY */
document.querySelectorAll("[data-entry-action]").forEach(btn => {
    btn.onclick = async () => {
        const action = btn.dataset.entryAction;
        const id = document.getElementById("entry-id").value;
        const external_game_id = document.getElementById("external-game-id").value;
        const status = document.getElementById("status").value;
        const hours_played = Number(document.getElementById("hours-played").value);

        let data;

        if (action === "list")
            data = await request(API.list);

        if (action === "detail")
            data = await request(API.detail(id));

        if (action === "patch")
            data = await request(API.patch(id), "PATCH", { hours_played });

        if (action === "put")
            data = await request(API.put(id), "PUT", { external_game_id, status, hours_played });

        if (action === "delete")
            data = await request(API.delete(id), "DELETE");

        document.getElementById("library-status").textContent = JSON.stringify(data);
    };
});

/* CREATE ENTRY */
document.getElementById("entry-form").onsubmit = async e => {
    e.preventDefault();

    const external_game_id = document.getElementById("external-game-id").value;
    const status = document.getElementById("status").value;
    const hours_played = Number(document.getElementById("hours-played").value);

    const data = await request(API.entries, "POST", {
        external_game_id,
        status,
        hours_played
    });

    document.getElementById("library-status").textContent = JSON.stringify(data);
};
