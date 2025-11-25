from datetime import date
from dateutil.parser import parse as parse_date

class DependencyCycleError(Exception):
    pass

def parse_tasks_input(tasks_input):
    tasks = {}
    for idx, t in enumerate(tasks_input):
        tid = str(t.get('id', idx))
        due = t.get('due_date')
        if due:
            try:
                if isinstance(due, str):
                    due_parsed = parse_date(due).date()
                elif isinstance(due, date):
                    due_parsed = due
                else:
                    due_parsed = None
            except Exception:
                due_parsed = None
        else:
            due_parsed = None
        tasks[tid] = {
            'id': tid,
            'title': t.get('title', '').strip() or f'Untitled {tid}',
            'due_date': due_parsed,
            'estimated_hours': float(t.get('estimated_hours', 0) or 0),
            'importance': int(t.get('importance', 5) or 5),
            'dependencies': [str(x) for x in t.get('dependencies', [])] if t.get('dependencies') else []
        }
    return tasks

def detect_cycles(tasks):
    visited = {}
    path = []

    def visit(node):
        if node not in tasks:
            return False
        if visited.get(node) == 'temp':
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            raise DependencyCycleError("Cycle detected: " + " -> ".join(cycle))
        if visited.get(node) == 'perm':
            return False
        visited[node] = 'temp'
        path.append(node)
        for dep in tasks[node]['dependencies']:
            visit(dep)
        path.pop()
        visited[node] = 'perm'
        return False

    for n in list(tasks.keys()):
        if visited.get(n) is None:
            visit(n)

def score_tasks(tasks_input, strategy='smart', weights=None):
    tasks = parse_tasks_input(tasks_input)
    detect_cycles(tasks)

    dependent_count = {tid: 0 for tid in tasks}
    for tid, t in tasks.items():
        for dep in t['dependencies']:
            if dep in dependent_count:
                dependent_count[dep] += 1

    default_weights = {
        'urgency': 0.4,
        'importance': 0.3,
        'effort': 0.15,
        'dependency': 0.15
    }
    if strategy == 'fastest':
        default_weights = {'urgency': 0.2, 'importance': 0.1, 'effort': 0.6, 'dependency': 0.1}
    elif strategy == 'impact':
        default_weights = {'urgency': 0.2, 'importance': 0.6, 'effort': 0.1, 'dependency': 0.1}
    elif strategy == 'deadline':
        default_weights = {'urgency': 0.7, 'importance': 0.15, 'effort': 0.1, 'dependency': 0.05}

    if weights:
        w = default_weights.copy()
        w.update(weights)
    else:
        w = default_weights

    today = date.today()

    def urgency_score(due_date):
        if due_date is None:
            return 0.1
        delta = (due_date - today).days
        if delta < 0:
            return min(1.0, 0.9 + min(0.1, abs(delta)/30))
        if delta == 0:
            return 1.0
        return max(0.0, 1 - (delta / 30.0))

    def importance_score(importance):
        return max(0.0, min(1.0, (importance - 1) / 9.0))

    def effort_score(hours):
        if hours <= 0:
            return 1.0
        val = 1 - min(1.0, hours / 20.0)
        return val

    max_deps = max(dependent_count.values()) if dependent_count else 0
    def dependency_score(tid):
        if max_deps == 0:
            return 0.0
        return dependent_count.get(tid, 0) / max_deps

    results = []
    for tid, t in tasks.items():
        u = urgency_score(t['due_date'])
        imp = importance_score(t['importance'])
        eff = effort_score(t['estimated_hours'])
        dep = dependency_score(tid)
        score = u * w['urgency'] + imp * w['importance'] + eff * w['effort'] + dep * w['dependency']
        explanation = {
            'urgency_component': round(u, 3),
            'importance_component': round(imp, 3),
            'effort_component': round(eff, 3),
            'dependency_component': round(dep, 3),
            'weights': w
        }
        results.append({
            **t,
            'score': round(score, 4),
            'explanation': explanation
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results
