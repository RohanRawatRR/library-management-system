const API_BASE = "/api";
let accessToken = localStorage.getItem("accessToken");

const authStatusEl = document.getElementById("auth-status");
const loginLink = document.getElementById("login-link");
const registerLink = document.getElementById("register-link");
const logoutBtn = document.getElementById("logout-btn");
const booksBody = document.getElementById("books-body");
const loansBody = document.getElementById("loans-body");
const loansPanel = document.getElementById("loans-panel");
const homeLayout = document.getElementById("home-layout");
const searchInput = document.getElementById("search-input");
const availableSelect = document.getElementById("available-select");
const resetFiltersBtn = document.getElementById("reset-filters");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const toastContainer = document.getElementById("toast-container");
const prevPageBtn = document.getElementById("prev-page");
const nextPageBtn = document.getElementById("next-page");
const pageInfo = document.getElementById("page-info");
const applyFiltersBtn = document.getElementById("apply-filters");
const totalCount = document.getElementById("total-count");

let nextPage = null;
let prevPage = null;
let currentPage = 1;
let currentQuery = "";
let currentAvailable = "";

function redirectAuthPagesIfLoggedIn() {
  const path = window.location.pathname;
  if (accessToken && (path.startsWith("/login") || path.startsWith("/register"))) {
    window.location.href = "/";
  }
}

function setAuthStatus(text) {
  if (authStatusEl) authStatusEl.textContent = text;
}

function authHeaders() {
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
}

function formatErrors(body) {
  if (!body || typeof body !== "object") return "";
  if (Array.isArray(body)) return body.join(", ");
  const parts = [];
  Object.entries(body).forEach(([key, value]) => {
    if (key === "detail") return;
    if (Array.isArray(value)) {
      parts.push(`${key}: ${value.join(", ")}`);
    } else if (typeof value === "object") {
      parts.push(`${key}: ${JSON.stringify(value)}`);
    } else {
      parts.push(`${key}: ${value}`);
    }
  });
  return parts.join(" | ");
}

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const message = formatErrors(body) || body.detail || body.error || `Request failed (${res.status})`;
    const err = new Error(message);
    err.payload = body;
    err.status = res.status;
    throw err;
  }
  return res.json();
}

function showToast(type, message) {
  if (!toastContainer) return;
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.innerHTML = `<span>${message}</span><button aria-label="Close">&times;</button>`;
  const close = () => el.remove();
  el.querySelector("button").addEventListener("click", close);
  toastContainer.appendChild(el);
  setTimeout(close, 4000);
}

function updatePagination(meta) {
  nextPage = meta.next;
  prevPage = meta.previous;
  currentPage = meta.current || 1;
  if (prevPageBtn) prevPageBtn.disabled = !prevPage;
  if (nextPageBtn) nextPageBtn.disabled = !nextPage;
  if (pageInfo) pageInfo.textContent = `Page ${currentPage}`;
  if (totalCount && typeof meta.count === "number") {
    totalCount.textContent = `Total: ${meta.count}`;
  }
}

async function loadBooks(url) {
  const targetUrl =
    url ||
    `${API_BASE}/books/?` +
      new URLSearchParams({
        q: currentQuery || "",
        available: currentAvailable || "",
      }).toString();
  const data = await fetchJSON(targetUrl);
  if (!booksBody) return;
  booksBody.innerHTML = "";
  const results = Array.isArray(data.results)
    ? data.results
    : Array.isArray(data)
    ? data
    : [];
  if (!Array.isArray(results)) {
    showToast("error", "Unexpected response format");
    return;
  }
  results.forEach((book) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${book.title}</td>
      <td>${book.author}</td>
      <td>${book.isbn}</td>
      <td>${book.available_copies}</td>
      <td>
        <button ${book.available_copies < 1 ? "disabled" : ""} data-id="${book.id}" class="borrow-btn">Borrow</button>
      </td>
    `;
    booksBody.appendChild(tr);
  });
  updatePagination({
    next: data.next,
    previous: data.previous,
    current: data.current || data.page || currentPage,
    count: data.count,
  });
}

async function loadLoans() {
  if (!loansPanel) return;
  loansPanel.classList.toggle("hidden", !accessToken);
  if (!loansBody) return;
  if (!accessToken) {
    return;
  }
  try {
    const data = await fetchJSON(`${API_BASE}/loans/`, { headers: authHeaders() });
    const results = Array.isArray(data?.results)
      ? data.results
      : Array.isArray(data)
      ? data
      : [];
    loansBody.innerHTML = "";
    results.forEach((loan) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${loan.book.title}</td>
        <td>${new Date(loan.borrowed_at).toLocaleString()}</td>
        <td>${loan.returned_at ? new Date(loan.returned_at).toLocaleString() : "Active"}</td>
      `;
      loansBody.appendChild(tr);
    });
  } catch (e) {
    loansBody.innerHTML = `<tr><td colspan='3'>${e.message}</td></tr>`;
    showToast("error", e.message);
  }
}

function bindHandlers() {
  applyFiltersBtn?.addEventListener("click", () => {
    currentQuery = searchInput.value.trim();
    currentAvailable = availableSelect?.value || "";
    loadBooks();
  });

  resetFiltersBtn?.addEventListener("click", () => {
    currentQuery = "";
    currentAvailable = "";
    if (searchInput) searchInput.value = "";
    if (availableSelect) availableSelect.value = "";
    loadBooks();
  });

  prevPageBtn?.addEventListener("click", () => {
    if (prevPage) loadBooks(prevPage);
  });

  nextPageBtn?.addEventListener("click", () => {
    if (nextPage) loadBooks(nextPage);
  });

  loginForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = new FormData(loginForm);
    try {
      const data = await fetchJSON(`${API_BASE}/auth/login/`, {
        method: "POST",
        body: JSON.stringify({
          username: form.get("username"),
          password: form.get("password"),
        }),
      });
      accessToken = data.access;
      localStorage.setItem("accessToken", accessToken);
      setAuthStatus(`Logged in as ${form.get("username")}`);
      await loadLoans();
      toggleAuthLinks();
      showToast("success", "Logged in");
      // Redirect to home after successful login
      window.location.href = "/";
    } catch (err) {
      showToast("error", err.message);
    }
  });

  registerForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = new FormData(registerForm);
    try {
      await fetchJSON(`${API_BASE}/auth/register/`, {
        method: "POST",
        body: JSON.stringify({
          username: form.get("username"),
          email: form.get("email"),
          password: form.get("password"),
        }),
      });
      showToast("success", "Registered. Please log in.");
      window.location.href = "/login/?registered=1";
    } catch (err) {
      showToast("error", err.message);
    }
  });

  booksBody?.addEventListener("click", async (e) => {
    const btn = e.target.closest(".borrow-btn");
    if (!btn) return;
    if (!accessToken) {
      showToast("error", "Please log in to borrow.");
      return;
    }
    const id = btn.getAttribute("data-id");
    try {
      await fetchJSON(`${API_BASE}/books/${id}/borrow/`, {
        method: "POST",
        headers: authHeaders(),
      });
      await loadBooks();
      await loadLoans();
    } catch (err) {
      showToast("error", err.message);
    }
  });

  logoutBtn?.addEventListener("click", () => {
    accessToken = null;
    localStorage.removeItem("accessToken");
    setAuthStatus("Guest");
    toggleAuthLinks();
    loadLoans();
    showToast("success", "Logged out");
  });
}

function toggleAuthLinks() {
  const isLoggedIn = Boolean(accessToken);
  if (loginLink) loginLink.style.display = isLoggedIn ? "none" : "inline-block";
  if (registerLink) registerLink.style.display = isLoggedIn ? "none" : "inline-block";
  if (logoutBtn) logoutBtn.style.display = isLoggedIn ? "inline-block" : "none";
  if (loansPanel) loansPanel.classList.toggle("hidden", !isLoggedIn);
  if (homeLayout) homeLayout.classList.toggle("one-col", !isLoggedIn);
}

function showLandingMessages() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("registered") === "1") {
    showToast("success", "Registration successful. Please log in.");
    params.delete("registered");
    const newUrl = `${window.location.pathname}${params.toString() ? "?" + params.toString() : ""}`;
    window.history.replaceState({}, "", newUrl);
  }
}

async function init() {
  redirectAuthPagesIfLoggedIn();
  showLandingMessages();
  toggleAuthLinks();
  bindHandlers();
  await loadBooks();
  await loadLoans();
}

init();


