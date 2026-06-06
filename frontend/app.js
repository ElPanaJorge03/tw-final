const API_BASE = "http://38.180.81.158:8000";

/* ── DOM refs ─────────────────────────────────────────────── */
const authCard        = document.getElementById("auth-card");
const inventoryCard   = document.getElementById("inventory-card");
const recipesCard     = document.getElementById("recipes-card");
const registerForm    = document.getElementById("register-form");
const loginForm       = document.getElementById("login-form");
const ingredientForm  = document.getElementById("ingredient-form");
const ingredientList  = document.getElementById("ingredient-list");
const recipesList     = document.getElementById("recipes-list");
const generateBtn     = document.getElementById("generate-btn");
const logoutBtn       = document.getElementById("logout-btn");
const globalAlert     = document.getElementById("global-alert");
const healthStatus    = document.getElementById("health-status");
const tabs            = document.querySelectorAll(".tab");

const tokenKey = "tw_token";

/* ── Alerts ───────────────────────────────────────────────── */
let alertTimer = null;

const showAlert = (message, isSuccess = false) => {
  clearTimeout(alertTimer);
  globalAlert.textContent = message;
  globalAlert.classList.add("show");
  globalAlert.classList.toggle("success", isSuccess);
  alertTimer = setTimeout(hideAlert, 5000);
};

const hideAlert = () => {
  clearTimeout(alertTimer);
  globalAlert.textContent = "";
  globalAlert.classList.remove("show", "success");
};

/* ── Tabs (register / login) ─────────────────────────────── */
const setActiveTab = (tabId) => {
  tabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === tabId);
  });

  document.querySelectorAll("[data-pane]").forEach((pane) => {
    pane.classList.toggle("hidden", pane.dataset.pane !== tabId);
  });
};

tabs.forEach((tab) => {
  tab.addEventListener("click", () => setActiveTab(tab.dataset.tab));
});

/* ── Token helpers ────────────────────────────────────────── */
const getToken   = () => localStorage.getItem(tokenKey);
const setToken   = (token) => localStorage.setItem(tokenKey, token);
const clearToken = () => localStorage.removeItem(tokenKey);

const isLoggedIn = () => !!getToken();

/* ── UI state management ──────────────────────────────────── */
const updateUI = () => {
  const logged = isLoggedIn();

  /* Show auth card only when NOT logged in */
  authCard.classList.toggle("hidden", logged);

  /* Show inventory + recipes only when logged in */
  inventoryCard.classList.toggle("hidden", !logged);
  recipesCard.classList.toggle("hidden", !logged);

  hideAlert();
};

/* ── HTTP helper ──────────────────────────────────────────── */
const authHeaders = () => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const request = async (path, options = {}) => {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
        ...(options.headers || {}),
      },
      ...options,
    });
  } catch (networkError) {
    throw new Error("No se pudo conectar con el servidor. Verifica tu conexión.");
  }

  /* Handle 401 – expired or invalid token → force logout */
  if (response.status === 401) {
    clearToken();
    updateUI();
    throw new Error("Sesión expirada. Inicia sesión nuevamente.");
  }

  if (!response.ok) {
    let errorMsg = `Error ${response.status}`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") {
        errorMsg = body.detail;
      } else if (Array.isArray(body.detail)) {
        /* FastAPI validation errors: [{loc:[...], msg:"...", type:"..."}] */
        errorMsg = body.detail.map((e) => e.msg).join(", ");
      } else if (body.message) {
        errorMsg = body.message;
      }
    } catch {
      /* Response wasn't JSON – use status text */
      errorMsg = response.statusText || errorMsg;
    }
    throw new Error(errorMsg);
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
};

/* ── Load ingredients ─────────────────────────────────────── */
const loadIngredients = async () => {
  try {
    const items = await request("/ingredientes");
    ingredientList.innerHTML = "";

    if (items.length === 0) {
      ingredientList.innerHTML = '<li class="empty-state">Sin ingredientes. ¡Agrega algunos!</li>';
      return;
    }

    items.forEach((item) => {
      const li = document.createElement("li");
      li.innerHTML = `<span>${item.nombre} · ${item.cantidad} ${item.unidad || ""}</span>`;

      const del = document.createElement("button");
      del.textContent = "✕";
      del.title = "Eliminar";
      del.addEventListener("click", async () => {
        try {
          await request(`/ingredientes/${item.id}`, { method: "DELETE" });
          loadIngredients();
        } catch (error) {
          showAlert(error.message);
        }
      });

      li.appendChild(del);
      ingredientList.appendChild(li);
    });
  } catch (error) {
    showAlert(error.message);
  }
};

/* ── Load recipes ─────────────────────────────────────────── */
const loadRecipes = async () => {
  try {
    const items = await request("/recetas");
    recipesList.innerHTML = "";

    if (items.length === 0) {
      recipesList.innerHTML = '<div class="empty-state">Sin recetas. ¡Genera una!</div>';
      return;
    }

    items.forEach((recipe) => {
      const card = document.createElement("div");
      card.className = "recipe";

      card.innerHTML = `
        <h3>${recipe.nombre_plato}</h3>
        <div class="muted">${recipe.tiempo_estimado} · ${recipe.nivel_dificultad}</div>
        <strong>Ingredientes</strong>
        <ul>
          ${recipe.ingredientes
            .map((ing) => `<li>${ing.nombre} - ${ing.cantidad} ${ing.unidad || ""}</li>`)
            .join("")}
        </ul>
        <strong>Pasos</strong>
        <ol>
          ${recipe.pasos.map((paso) => `<li>${paso}</li>`).join("")}
        </ol>
        <div class="recipe__actions">
          <button class="btn ghost" data-delete>Eliminar</button>
        </div>
      `;

      card.querySelector("[data-delete]").addEventListener("click", async () => {
        try {
          await request(`/recetas/${recipe.id}`, { method: "DELETE" });
          loadRecipes();
        } catch (error) {
          showAlert(error.message);
        }
      });

      recipesList.appendChild(card);
    });
  } catch (error) {
    showAlert(error.message);
  }
};

/* ── Register ─────────────────────────────────────────────── */
registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideAlert();

  const formData = new FormData(registerForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    await request("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    registerForm.reset();
    showAlert("¡Cuenta creada! Ahora inicia sesión.", true);
    setActiveTab("login");
  } catch (error) {
    showAlert(error.message);
  }
});

/* ── Login ────────────────────────────────────────────────── */
loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideAlert();

  const formData = new FormData(loginForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const data = await request("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setToken(data.access_token);
    loginForm.reset();
    updateUI();
    await Promise.all([loadIngredients(), loadRecipes()]);
  } catch (error) {
    showAlert(error.message);
  }
});

/* ── Add ingredient ───────────────────────────────────────── */
ingredientForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideAlert();

  const formData = new FormData(ingredientForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    await request("/ingredientes", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    ingredientForm.reset();
    loadIngredients();
  } catch (error) {
    showAlert(error.message);
  }
});

/* ── Generate recipe ──────────────────────────────────────── */
generateBtn.addEventListener("click", async () => {
  hideAlert();
  generateBtn.disabled = true;
  generateBtn.textContent = "Generando…";

  try {
    await request("/recetas/generar", { method: "POST" });
    await loadRecipes();
  } catch (error) {
    showAlert(error.message);
  } finally {
    generateBtn.disabled = false;
    generateBtn.textContent = "Generar receta";
  }
});

/* ── Logout ───────────────────────────────────────────────── */
logoutBtn.addEventListener("click", () => {
  clearToken();
  ingredientList.innerHTML = "";
  recipesList.innerHTML = "";
  updateUI();
});

/* ── Boot ─────────────────────────────────────────────────── */
const boot = async () => {
  /* Set initial UI state */
  updateUI();

  /* Health check */
  try {
    const data = await request("/health");
    healthStatus.textContent = `API: ${data.status}`;
  } catch (error) {
    healthStatus.textContent = "API: no disponible";
  }

  /* If there's a saved token, try loading data */
  if (isLoggedIn()) {
    try {
      await Promise.all([loadIngredients(), loadRecipes()]);
    } catch {
      /* Token was invalid – updateUI already ran via 401 handler */
    }
  }
};

boot();
