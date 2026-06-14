const API = "/api";
let editingId = null;

const statusLabels = { pending: "Pendiente", in_progress: "En Progreso", completed: "Completado" };

const icons = {
  total: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>`,
  pending: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  in_progress: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>`,
  completed: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`,
};

async function api(path, method = "GET", body = null) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Error en la solicitud");
  return data;
}

function showToast(msg, type = "") {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = `toast ${type}`;
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.add("hidden"), 3000);
}

function escapeHtml(str = "") {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function formatDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("es", { day: "2-digit", month: "short", year: "numeric" });
}

function renderStats(tasks) {
  const c = { total: tasks.length, pending: 0, in_progress: 0, completed: 0 };
  tasks.forEach(t => c[t.status]++);

  const labels = { total: "Total", pending: "Pendientes", in_progress: "En Progreso", completed: "Completadas" };
  document.getElementById("stats").innerHTML = ["total", "pending", "in_progress", "completed"].map(k => `
    <div class="stat-card">
      <div class="stat-icon ${k}">${icons[k]}</div>
      <div class="stat-info">
        <div class="stat-num">${c[k]}</div>
        <div class="stat-label">${labels[k]}</div>
      </div>
    </div>
  `).join("");
}

function renderKanban(tasks) {
  const cols = { pending: [], in_progress: [], completed: [] };
  tasks.forEach(t => cols[t.status].push(t));

  Object.keys(cols).forEach(status => {
    const cards = cols[status];
    document.getElementById(`count-${status}`).textContent = cards.length;
    document.getElementById(`cards-${status}`).innerHTML = cards.length
      ? cards.map(t => `
        <div class="task-card ${t.status}" data-id="${t.id}">
          <div class="task-title">${escapeHtml(t.title)}</div>
          ${t.description ? `<div class="task-desc">${escapeHtml(t.description)}</div>` : ""}
          <div class="task-footer">
            <span class="task-date">${formatDate(t.created_at)}</span>
            <div class="task-actions">
              <button class="task-btn edit" onclick="startEdit(${t.id})">Editar</button>
              <button class="task-btn delete" onclick="deleteTask(${t.id})">Eliminar</button>
            </div>
          </div>
        </div>`).join("")
      : `<p style="font-size:.8rem;color:#94a3b8;text-align:center;padding:.8rem 0">Sin tareas</p>`;
  });
}

async function loadTasks() {
  const filter = document.getElementById("filter-status").value;
  const url = filter ? `/tasks?status=${filter}` : "/tasks";
  try {
    const tasks = await api(url);
    renderStats(tasks);
    renderKanban(tasks);
  } catch (e) {
    showToast(e.message, "error");
  }
}

function openModal(title = "Nueva Tarea", submitLabel = "Crear Tarea") {
  document.getElementById("modal-title").textContent = title;
  document.getElementById("submit-btn").textContent = submitLabel;
  document.getElementById("modal-backdrop").classList.remove("hidden");
  setTimeout(() => document.getElementById("title").focus(), 50);
}

function closeModal() {
  document.getElementById("modal-backdrop").classList.add("hidden");
  document.getElementById("task-form").reset();
  editingId = null;
}

async function startEdit(id) {
  try {
    const task = await api(`/tasks/${id}`);
    editingId = id;
    document.getElementById("title").value = task.title;
    document.getElementById("description").value = task.description || "";
    document.getElementById("status").value = task.status;
    openModal("Editar Tarea", "Guardar Cambios");
  } catch (e) {
    showToast(e.message, "error");
  }
}

async function deleteTask(id) {
  if (!confirm("¿Eliminar esta tarea?")) return;
  try {
    await api(`/tasks/${id}`, "DELETE");
    showToast("Tarea eliminada", "success");
    loadTasks();
  } catch (e) {
    showToast(e.message, "error");
  }
}

document.getElementById("task-form").addEventListener("submit", async e => {
  e.preventDefault();
  const body = {
    title: document.getElementById("title").value.trim(),
    description: document.getElementById("description").value.trim(),
    status: document.getElementById("status").value,
  };
  try {
    if (editingId) {
      await api(`/tasks/${editingId}`, "PUT", body);
      showToast("Tarea actualizada", "success");
    } else {
      await api("/tasks", "POST", body);
      showToast("Tarea creada", "success");
    }
    closeModal();
    loadTasks();
  } catch (e) {
    showToast(e.message, "error");
  }
});

document.getElementById("open-modal-btn").addEventListener("click", () => openModal());
document.getElementById("cancel-btn").addEventListener("click", closeModal);
document.getElementById("modal-close").addEventListener("click", closeModal);
document.getElementById("modal-backdrop").addEventListener("click", e => {
  if (e.target === document.getElementById("modal-backdrop")) closeModal();
});
document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });
document.getElementById("filter-status").addEventListener("change", loadTasks);

loadTasks();
