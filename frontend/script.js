const localTasks = [];
const localList = document.getElementById("localList");
const resultsDiv = document.getElementById("results");
const errorBox = document.getElementById("error");

// Update local preview
function refreshLocal() {
    localList.textContent = JSON.stringify(localTasks, null, 2);
}

// Add Task Manually
document.getElementById("addTask").onclick = () => {
    const t = {
        id: (Math.random() * 100000).toFixed(0),
        title: document.getElementById("title").value.trim(),
        due_date: document.getElementById("due_date").value || null,
        estimated_hours: parseFloat(document.getElementById("hours").value || 0),
        importance: parseInt(document.getElementById("importance").value || 5),
        dependencies: document.getElementById("dependencies").value
            ? document.getElementById("dependencies").value.split(",").map(s => s.trim())
            : []
    };

    if (!t.title) {
        alert("Title is required.");
        return;
    }

    localTasks.push(t);
    refreshLocal();
    errorBox.textContent = "";
};

// Analyze Tasks
document.getElementById("analyze").onclick = async () => {
    let tasks = [];
    const bulk = document.getElementById("bulk").value.trim();

    if (bulk) {
        try {
            tasks = JSON.parse(bulk);
        } catch (e) {
            errorBox.textContent = "Invalid JSON in bulk input.";
            return;
        }
    } else {
        tasks = localTasks.slice();
    }

    if (tasks.length === 0) {
        errorBox.textContent = "No tasks to analyze.";
        return;
    }

    const strategy = document.getElementById("strategy").value;

    try {
        const resp = await fetch("http://127.0.0.1:8000/api/tasks/analyze/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tasks, strategy })
        });

        const data = await resp.json();

        if (!resp.ok) {
            errorBox.textContent = data.message || "API error.";
            return;
        }

        renderResults(data.results);

    } catch (err) {
        errorBox.textContent = "Network error: " + err;
    }
};

// Suggest Top 3 Tasks
document.getElementById("suggest").onclick = async () => {
    let tasks = localTasks.slice();
    const bulk = document.getElementById("bulk").value.trim();

    if (bulk) {
        try {
            tasks = JSON.parse(bulk);
        } catch (e) {
            errorBox.textContent = "Invalid JSON in bulk input.";
            return;
        }
    }

    if (!tasks || tasks.length === 0) {
        errorBox.textContent = "No tasks available.";
        return;
    }

    const q = encodeURIComponent(JSON.stringify(tasks));
    const strategy = document.getElementById("strategy").value;

    try {
        const resp = await fetch(
            `http://127.0.0.1:8000/api/tasks/suggest/?tasks=${q}&strategy=${strategy}`
        );
        const data = await resp.json();

        if (!resp.ok) {
            errorBox.textContent = data.message || "API error.";
            return;
        }

        renderSuggestions(data.suggestions);

    } catch (err) {
        errorBox.textContent = "Network error: " + err;
    }
};

// Render results from /analyze
function renderResults(results) {
    resultsDiv.innerHTML = "";

    results.forEach(r => {
        const card = document.createElement("div");
        card.className = "task-card";

        if (r.score > 0.7) card.classList.add("high");
        else if (r.score > 0.4) card.classList.add("medium");
        else card.classList.add("low");

        card.innerHTML = `
            <strong>${r.title}</strong> (Score: ${r.score})
            <br>
            <em>Due:</em> ${r.due_date || "N/A"}
            <br>
            <em>Hours:</em> ${r.estimated_hours} |
            <em>Importance:</em> ${r.importance}
            <br>
            <p><strong>Explanation:</strong><br>
            Urgency: ${r.explanation.urgency_component},
            Importance: ${r.explanation.importance_component},
            Effort: ${r.explanation.effort_component},
            Dependency: ${r.explanation.dependency_component}
            </p>
        `;

        resultsDiv.appendChild(card);
    });
}

// Render suggestions (top 3)
function renderSuggestions(suggestions) {
    resultsDiv.innerHTML = "<h3>Top 3 Suggestions</h3>";

    suggestions.forEach(s => {
        const r = s.task;
        const card = document.createElement("div");
        card.className = "task-card";

        if (r.score > 0.7) card.classList.add("high");
        else if (r.score > 0.4) card.classList.add("medium");
        else card.classList.add("low");

        card.innerHTML = `
            <strong>${r.title}</strong> (Score: ${r.score})
            <p>${s.explanation_text}</p>
        `;

        resultsDiv.appendChild(card);
    });
}
