from django.test import TestCase
from .scoring import score_tasks, detect_cycles, DependencyCycleError
from datetime import date, timedelta

class ScoringTests(TestCase):
    def test_basic_scoring_sorts_by_score(self):
        t1 = {'id': '1', 'title': 'low effort', 'due_date': (date.today() + timedelta(days=1)).isoformat(), 'estimated_hours': 1, 'importance': 5}
        t2 = {'id': '2', 'title': 'high effort', 'due_date': (date.today() + timedelta(days=10)).isoformat(), 'estimated_hours': 10, 'importance': 8}
        results = score_tasks([t1, t2], strategy='smart')
        self.assertTrue(results[0]['score'] >= results[1]['score'])

    def test_past_due_gets_high_urgency(self):
        t = {'id': 'p', 'title': 'past due', 'due_date': (date.today() - timedelta(days=2)).isoformat(), 'estimated_hours': 5, 'importance': 5}
        results = score_tasks([t], strategy='deadline')
        self.assertTrue(results[0]['explanation']['urgency_component'] > 0.8)

    def test_detect_cycle_raises(self):
        tasks = [
            {'id': 'a', 'title': 'A', 'dependencies': ['b']},
            {'id': 'b', 'title': 'B', 'dependencies': ['a']}
        ]
        with self.assertRaises(DependencyCycleError):
            detect_cycles({t['id']: {**t, 'dependencies': t.get('dependencies', [])} for t in tasks})
