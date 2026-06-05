const API_BASE = "http://localhost:8000";

const registerForm = document.getElementById("register-form");
const loginForm = document.getElementById("login-form");
const ingredientForm = document.getElementById("ingredient-form");
const ingredientList = document.getElementById("ingredient-list");
const recipesList = document.getElementById("recipes-list");
const generateBtn = document.getElementById("generate-btn");
const logoutBtn = document.getElementById("logout-btn");
const authAlert = document.getElementById("auth-alert");
const healthStatus = document.getElementById("health-status");

const tabs = document.querySelectorAll(".tab");

const tokenKey = "tw_token";

const showAlert = (message) => {
  authAlert.textContent = message;
  authAlert.classList.add("show");
};

const hideAlert = () => {
  authAlert.textContent = "";
  authAlert.classList.remove("show");
};

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

const getToken = () => localStorage.getItem(tokenKey);
const setToken = (token) => localStorage.setItem(tokenKey, token);
const clearToken = () => localStorage.removeItem(tokenKey);

const authHeaders = () => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const request = async (path, options = {}) => {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || "Error en la solicitud");
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
};

const loadIngredients = async () => {
  const items = await request("/ingredientes");
  ingredientList.innerHTML = "";

  items.forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = `<span>${item.nombre} · ${item.cantidad} ${item.unidad || ""}</span>`;

    const del = document.createElement("button");
    del.textContent = "Eliminar";
    del.addEventListener("click", async () => {
      await request(`/ingredientes/${item.id}`, { method: "DELETE" });
      loadIngredients();
    });

    li.appendChild(del);
    ingredientList.appendChild(li);
  });
};

const loadRecipes = async () => {
  const items = await request("/recetas");
  recipesList.innerHTML = "";

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
      await request(`/recetas/${recipe.id}`, { method: "DELETE" });
      loadRecipes();
    });

    recipesList.appendChild(card);
  });
};

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
    showAlert("Cuenta creada. Ahora inicia sesion.");
    setActiveTab("login");
  } catch (error) {
    showAlert(error.message);
  }
});

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
    await Promise.all([loadIngredients(), loadRecipes()]);
  } catch (error) {
    showAlert(error.message);
  }
});

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

generateBtn.addEventListener("click", async () => {
  hideAlert();
  generateBtn.disabled = true;
  generateBtn.textContent = "Generando...";

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

logoutBtn.addEventListener("click", () => {
  clearToken();
  ingredientList.innerHTML = "";
  recipesList.innerHTML = "";
});

const boot = async () => {
  try {
    const data = await request("/health");
    healthStatus.textContent = `API: ${data.status}`;
  } catch (error) {
    healthStatus.textContent = "API: no disponible";
  }

  if (getToken()) {
    loadIngredients();
    loadRecipes();
  }
};

boot();
