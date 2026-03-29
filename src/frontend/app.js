const logEl = document.querySelector("#log");
const meOutput = document.querySelector("#meOutput");
const lastActionEl = document.querySelector("#lastAction");
const lastResponseEl = document.querySelector("#lastResponse");
const networkStatusEl = document.querySelector("#networkStatus");
const toastEl = document.querySelector("#toast");

const projectsList = document.querySelector("#projectsList");
const tasksList = document.querySelector("#tasksList");
const commentsList = document.querySelector("#commentsList");

let pendingRequests = 0;

const forms = {
  registerForm: document.querySelector("#registerForm"),
  loginForm: document.querySelector("#loginForm"),
  createProjectForm: document.querySelector("#createProjectForm"),
  updateProjectForm: document.querySelector("#updateProjectForm"),
  deleteProjectForm: document.querySelector("#deleteProjectForm"),
  addMemberForm: document.querySelector("#addMemberForm"),
  removeMemberForm: document.querySelector("#removeMemberForm"),
  projectDetailsForm: document.querySelector("#projectDetailsForm"),
  createTaskForm: document.querySelector("#createTaskForm"),
  loadTasksForm: document.querySelector("#loadTasksForm"),
  updateTaskForm: document.querySelector("#updateTaskForm"),
  deleteTaskForm: document.querySelector("#deleteTaskForm"),
  createCommentForm: document.querySelector("#createCommentForm"),
  loadCommentsForm: document.querySelector("#loadCommentsForm"),
  updateCommentForm: document.querySelector("#updateCommentForm"),
  deleteCommentForm: document.querySelector("#deleteCommentForm"),
};

function setNetworkState(kind, text) {
  networkStatusEl.className = `badge state-badge ${kind}`;
  networkStatusEl.textContent = text;
}

function formatValue(value) {
  if (Array.isArray(value)) return value.join(", ") || "—";
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "object") return Object.entries(value).map(([k, v]) => `${k}: ${formatValue(v)}`).join("; ");
  return String(value);
}

function formatForText(payload) {
  if (typeof payload === "string") return payload;
  if (Array.isArray(payload)) {
    if (!payload.length) return "Список пуст.";
    return payload.map((item, i) => `${i + 1}) ${formatForText(item)}`).join("\n");
  }
  if (payload && typeof payload === "object") {
    return Object.entries(payload).map(([key, value]) => `${key}: ${formatValue(value)}`).join("\n");
  }
  return String(payload ?? "—");
}

function setLastAction(action, payload) {
  lastActionEl.textContent = action;
  if (payload !== undefined) lastResponseEl.textContent = formatForText(payload);
}

function showToast(message, type = "success") {
  toastEl.className = `toast-box ${type}`;
  toastEl.textContent = message;
  toastEl.classList.remove("hidden");
  setTimeout(() => toastEl.classList.add("hidden"), 2800);
}

function log(message, data) {
  const line = `[${new Date().toLocaleTimeString()}] ${message}`;
  const details = data ? `\n${formatForText(data)}` : "";
  logEl.textContent = `${line}${details}\n\n${logEl.textContent}`;
}

function markFormStatus(form, message, type) {
  const statusId = form?.dataset?.statusId;
  if (!statusId) return;
  const statusEl = document.getElementById(statusId);
  if (!statusEl) return;
  statusEl.className = `status-text ${type || ""}`.trim();
  statusEl.textContent = message;
}

function toggleFormButtons(form, disabled) {
  if (!form) return;
  form.querySelectorAll("button").forEach((btn) => (btn.disabled = disabled));
}

function formDataObject(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function clearList(el, text) {
  el.innerHTML = `<li class="list-item-card text-secondary-emphasis">${text}</li>`;
}

function renderUser(user) {
  meOutput.className = "output-box";
  meOutput.innerHTML = `
    <div class="line"><strong>ID:</strong> ${formatValue(user.id)}</div>
    <div class="line"><strong>Имя:</strong> ${formatValue(user.name)}</div>
    <div class="line"><strong>Email:</strong> ${formatValue(user.email)}</div>
  `;
}

function renderProjects(projects) {
  if (!projects.length) return clearList(projectsList, "Проекты не найдены.");
  projectsList.innerHTML = projects.map((p) => `
    <li class="list-item-card">
      <div class="line"><strong>ID проекта:</strong> ${formatValue(p.id)}</div>
      <div class="line"><strong>Название:</strong> ${formatValue(p.name)}</div>
      <div class="line"><strong>Участники:</strong> ${(p.members || []).map((m) => `${m.user_id} (${m.role})`).join(", ") || "—"}</div>
    </li>
  `).join("");
}

function renderProjectDetails(project) {
  renderProjects([project]);
}

function renderTasks(tasks) {
  if (!tasks.length) return clearList(tasksList, "Задачи не найдены.");
  tasksList.innerHTML = tasks.map((t) => `
    <li class="list-item-card">
      <div class="line"><strong>ID задачи:</strong> ${formatValue(t.id)}</div>
      <div class="line"><strong>Название:</strong> ${formatValue(t.title)}</div>
      <div class="line"><strong>Описание:</strong> ${formatValue(t.description)}</div>
      <div class="line"><strong>Статус:</strong> ${formatValue(t.status)}</div>
      <div class="line"><strong>Исполнитель:</strong> ${formatValue(t.assignee_id)}</div>
    </li>
  `).join("");
}

function renderComments(comments) {
  if (!comments.length) return clearList(commentsList, "Комментарии не найдены.");
  commentsList.innerHTML = comments.map((c) => `
    <li class="list-item-card">
      <div class="line"><strong>ID комментария:</strong> ${formatValue(c.id)}</div>
      <div class="line"><strong>Автор:</strong> ${formatValue(c.author_id)}</div>
      <div class="line"><strong>Текст:</strong> ${formatValue(c.text)}</div>
    </li>
  `).join("");
}

async function api(path, { method = "GET", body, actionName = path } = {}) {
  pendingRequests += 1;
  setNetworkState("loading", `Отправка запроса (${pendingRequests})…`);
  setLastAction(`Выполняется — ${method} ${path}`);
  log(`Запрос: ${method} ${path}`, body || null);

  try {
    const response = await fetch(path, {
      method,
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: body ? JSON.stringify(body) : undefined,
    });

    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json") ? await response.json() : await response.text();

    if (!response.ok) {
      const detail = typeof payload === "object" ? payload?.detail || formatForText(payload) : payload;
      throw new Error(`${response.status} ${response.statusText}: ${detail}`);
    }

    setLastAction(`Успешно — ${actionName}`, payload);
    log(`Ответ: ${method} ${path}`, payload);
    return payload;
  } finally {
    pendingRequests = Math.max(0, pendingRequests - 1);
    setNetworkState(pendingRequests ? "loading" : "success", pendingRequests ? `Ожидание ${pendingRequests} запроса(ов)…` : "Готов");
  }
}

async function runFormAction(form, action) {
  toggleFormButtons(form, true);
  markFormStatus(form, "Запрос отправлен…", "");
  try {
    await action();
    markFormStatus(form, "Готово ✅", "success");
  } catch (err) {
    markFormStatus(form, `Ошибка: ${err.message}`, "error");
    setNetworkState("error", "Есть ошибка");
    setLastAction("Ошибка запроса", err.message);
    log("Ошибка", { reason: err.message });
    showToast(err.message, "error");
  } finally {
    toggleFormButtons(form, false);
  }
}

forms.registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    await api("/users/registration", { method: "POST", body: formDataObject(form), actionName: "Регистрация" });
    showToast("Пользователь зарегистрирован");
  });
});

forms.loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    await api("/users/auth/login", { method: "POST", body: formDataObject(form), actionName: "Вход" });
    showToast("Вход выполнен");
  });
});

document.querySelector("#logoutBtn").addEventListener("click", async () => {
  await runFormAction(forms.loginForm, async () => {
    await api("/users/auth/logout", { method: "POST", actionName: "Выход" });
    meOutput.className = "output-box";
    meOutput.textContent = "Профиль пока не загружен.";
    showToast("Выход выполнен");
  });
});

document.querySelector("#meBtn").addEventListener("click", async () => {
  await runFormAction(forms.loginForm, async () => {
    const user = await api("/users/me", { actionName: "Получение профиля" });
    renderUser(user);
    showToast("Профиль загружен");
  });
});

forms.createProjectForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    const project = await api("/projects", { method: "POST", body: { name: data.name }, actionName: "Создание проекта" });
    showToast(`Проект создан: ${project.id}`);
    form.reset();
  });
});

forms.updateProjectForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    await api(`/projects/${data.projectId}`, { method: "PATCH", body: { name: data.name }, actionName: "Обновление проекта" });
    showToast("Название проекта обновлено");
  });
});

forms.deleteProjectForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    await api(`/projects/${data.projectId}`, { method: "DELETE", actionName: "Удаление проекта" });
    showToast("Проект удалён");
  });
});

forms.addMemberForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    await api(`/projects/${data.projectId}/members`, { method: "POST", body: { user_id: Number(data.userId) }, actionName: "Добавление участника" });
    showToast("Участник добавлен");
  });
});

forms.removeMemberForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    await api(`/projects/${data.projectId}/members`, { method: "DELETE", body: { user_id: Number(data.userId) }, actionName: "Удаление участника" });
    showToast("Участник удалён");
  });
});

document.querySelector("#loadProjectsBtn").addEventListener("click", async () => {
  await runFormAction(forms.projectDetailsForm, async () => {
    const projects = await api("/projects", { actionName: "Список проектов" });
    renderProjects(projects);
    showToast(`Проектов: ${projects.length}`);
  });
});

forms.projectDetailsForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    const project = await api(`/projects/${data.projectId}`, { actionName: "Детали проекта" });
    renderProjectDetails(project);
    showToast("Детали проекта загружены");
  });
});

forms.createTaskForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    const task = await api(`/projects/${data.projectId}/tasks`, {
      method: "POST",
      body: { title: data.title, description: data.description, assignee_id: Number(data.assignee_id) },
      actionName: "Создание задачи",
    });
    showToast(`Задача создана: ${task.id}`);
  });
});

forms.loadTasksForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    const tasks = await api(`/projects/${data.projectId}/tasks`, { actionName: "Список задач" });
    renderTasks(tasks);
    showToast(`Задач: ${tasks.length}`);
  });
});

forms.updateTaskForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    await api(`/tasks/${data.taskId}`, {
      method: "PATCH",
      body: { title: data.title || "", description: data.description || "", status: data.status || "" },
      actionName: "Обновление задачи",
    });
    showToast("Задача обновлена");
  });
});

forms.deleteTaskForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    await api(`/tasks/${data.taskId}`, { method: "DELETE", actionName: "Удаление задачи" });
    showToast("Задача удалена");
  });
});

forms.createCommentForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    await api(`/tasks/${data.taskId}/comments`, { method: "POST", body: { text: data.text }, actionName: "Создание комментария" });
    showToast("Комментарий создан");
  });
});

forms.loadCommentsForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    const comments = await api(`/${data.taskId}/comments`, { actionName: "Список комментариев" });
    renderComments(comments);
    showToast(`Комментариев: ${comments.length}`);
  });
});

forms.updateCommentForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    await api(`/comments/${data.commentId}`, { method: "PATCH", body: { text: data.text }, actionName: "Обновление комментария" });
    showToast("Комментарий обновлён");
  });
});

forms.deleteCommentForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  await runFormAction(form, async () => {
    const data = formDataObject(form);
    await api(`/comments/${data.commentId}`, { method: "DELETE", actionName: "Удаление комментария" });
    showToast("Комментарий удалён");
  });
});

setNetworkState("success", "Готов");
setLastAction("Ожидание действий", "Интерфейс готов. Выберите нужное действие в одном из блоков ниже.");
clearList(projectsList, "Список проектов пока пуст.");
clearList(tasksList, "Список задач пока пуст.");
clearList(commentsList, "Список комментариев пока пуст.");
log("Интерфейс загружен. Поддержаны все endpoints из API.");
