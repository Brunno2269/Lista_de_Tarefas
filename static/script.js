document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    setupEventListeners();
});

async function loadTasks() {
    showLoading();
    try {
        const response = await fetch('/tasks');
        if (!response.ok) throw new Error('Falha ao carregar tarefas');
        const tasks = await response.json();
        renderTasks(tasks);
        updateStats(tasks);
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

function renderTasks(tasks) {
    const taskList = document.getElementById('taskList');
    taskList.innerHTML = '';
    tasks.forEach(task => {
        const taskElement = createTaskElement(task);
        taskList.appendChild(taskElement);
    });
}

function createTaskElement(task) {
    const li = document.createElement('li');
    li.className = `task-item ${task.completed ? 'completed' : ''}`;
    li.dataset.taskId = task.id;
    li.innerHTML = `
        <input type="checkbox" 
               ${task.completed ? 'checked' : ''} 
               onchange="toggleTask(${task.id})"
               aria-label="${task.completed ? 'Marcar como não concluída' : 'Marcar como concluída'}">
        <span class="task-title" onclick="startEdit(${task.id})">${escapeHTML(task.title)}</span>
        <div class="actions">
            <button class="edit-btn" onclick="startEdit(${task.id})">✏️ Editar</button>
            <button class="delete-btn" onclick="deleteTask(${task.id})">🗑️ Excluir</button>
        </div>
    `;
    return li;
}

async function addTask() {
    const input = document.getElementById('taskInput');
    const title = input.value.trim();
    
    if (!title) {
        showError('Por favor, digite uma tarefa válida');
        return;
    }

    showLoading();
    try {
        const response = await fetch('/tasks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ title })
        });
        
        if (!response.ok) throw new Error('Falha ao adicionar tarefa');
        
        const newTask = await response.json();
        const taskElement = createTaskElement(newTask);
        document.getElementById('taskList').prepend(taskElement);
        updateStats();
        input.value = '';
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

async function toggleTask(taskId) {
    const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
    const completed = taskElement.querySelector('input').checked;

    try {
        const response = await fetch(`/tasks/${taskId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ completed })
        });
        
        if (!response.ok) throw new Error('Falha ao atualizar tarefa');
        
        taskElement.classList.toggle('completed', completed);
        updateStats();
    } catch (error) {
        showError(error.message);
        taskElement.querySelector('input').checked = !completed;
    }
}

async function deleteTask(taskId) {
    if (!confirm('Tem certeza que deseja excluir esta tarefa?')) return;

    showLoading();
    try {
        const response = await fetch(`/tasks/${taskId}`, { method: 'DELETE' });
        
        if (!response.ok) throw new Error('Falha ao excluir tarefa');
        
        document.querySelector(`[data-task-id="${taskId}"]`).remove();
        updateStats();
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

function startEdit(taskId) {
    const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
    const titleSpan = taskElement.querySelector('.task-title');
    const currentTitle = titleSpan.textContent;

    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentTitle;
    input.className = 'edit-input';
    input.style.width = `${titleSpan.offsetWidth}px`;

    const saveEdit = async () => {
        const newTitle = input.value.trim();
        if (!newTitle || newTitle === currentTitle) {
            input.replaceWith(titleSpan);
            return;
        }

        try {
            const response = await fetch(`/tasks/${taskId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ title: newTitle })
            });
            
            if (!response.ok) throw new Error('Falha ao editar tarefa');
            
            titleSpan.textContent = newTitle;
        } catch (error) {
            showError(error.message);
        } finally {
            input.replaceWith(titleSpan);
        }
    };

    input.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') saveEdit();
        if (e.key === 'Escape') input.replaceWith(titleSpan);
    });

    input.addEventListener('blur', saveEdit);
    titleSpan.replaceWith(input);
    input.focus();
}

function updateStats() {
    const tasks = document.querySelectorAll('.task-item');
    const completed = document.querySelectorAll('.completed').length;
    document.getElementById('totalTasks').textContent = `${tasks.length} ${tasks.length === 1 ? 'tarefa' : 'tarefas'}`;
    document.getElementById('completedTasks').textContent = `${completed} concluída${completed !== 1 ? 's' : ''}`;
}

function showHelp() {
    alert([
        '📌 Como usar:',
        '- Clique no texto para editar',
        '- Enter para salvar edição',
        '- Esc para cancelar edição',
        '- Clique no ícone 🌓 para mudar o tema',
        '- Arraste tarefas para reordenar'
    ].join('\n'));
}

function setupEventListeners() {
    document.getElementById('taskInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addTask();
    });

    window.addEventListener('beforeunload', () => {
        fetch('/shutdown', { method: 'POST' });
    });
}

function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => errorDiv.style.display = 'none', 5000);
}

function escapeHTML(str) {
    return str.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#39;');
}

window.addEventListener('beforeunload', () => {
    fetch('/shutdown', { method: 'POST' });
});