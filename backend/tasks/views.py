from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskSerializer
from .scoring import score_tasks, DependencyCycleError
import json

class AnalyzeTasksView(APIView):
    def post(self, request):
        payload = request.data
        if isinstance(payload, dict) and 'tasks' in payload:
            tasks = payload['tasks']
            strategy = payload.get('strategy', 'smart')
            weights = payload.get('weights')
        elif isinstance(payload, list):
            tasks = payload
            strategy = request.query_params.get('strategy', 'smart')
            weights = None
        else:
            return Response({'error': 'Invalid payload. Send list of tasks or {"tasks":[...]}'},
                            status=status.HTTP_400_BAD_REQUEST)

        errors = []
        for i, t in enumerate(tasks):
            ser = TaskSerializer(data=t)
            if not ser.is_valid():
                errors.append({'index': i, 'errors': ser.errors})
        if errors:
            return Response({'error': 'validation failed', 'details': errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            results = score_tasks(tasks, strategy=strategy, weights=weights)
        except DependencyCycleError as e:
            return Response({'error': 'circular_dependency', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'internal_error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'strategy': strategy, 'results': results}, status=status.HTTP_200_OK)

class SuggestTasksView(APIView):
    def get(self, request):
        tasks_json = request.query_params.get('tasks')
        strategy = request.query_params.get('strategy', 'smart')
        if not tasks_json:
            return Response({'error': 'Provide tasks as a JSON-encoded query param "tasks" or use POST.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            tasks = json.loads(tasks_json)
        except Exception as e:
            return Response({'error': 'invalid_json', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            results = score_tasks(tasks, strategy=strategy)
        except DependencyCycleError as e:
            return Response({'error': 'circular_dependency', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        top3 = results[:3]
        suggestions = []
        for t in top3:
            expl = f"Score {t['score']}. Urgency:{t['explanation']['urgency_component']}, " \
                   f"Importance:{t['explanation']['importance_component']}, " \
                   f"Effort:{t['explanation']['effort_component']}, " \
                   f"Dependency:{t['explanation']['dependency_component']}"
            suggestions.append({
                'task': t,
                'explanation_text': expl
            })
        return Response({'strategy': strategy, 'suggestions': suggestions}, status=status.HTTP_200_OK)

    def post(self, request):
        payload = request.data
        if isinstance(payload, dict) and 'tasks' in payload:
            tasks = payload['tasks']
            strategy = payload.get('strategy', 'smart')
        elif isinstance(payload, list):
            tasks = payload
            strategy = request.query_params.get('strategy', 'smart')
        else:
            return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            results = score_tasks(tasks, strategy=strategy)
        except DependencyCycleError as e:
            return Response({'error': 'circular_dependency', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        top3 = results[:3]
        suggestions = []
        for t in top3:
            expl = f"Score {t['score']}. Urgency:{t['explanation']['urgency_component']}, " \
                   f"Importance:{t['explanation']['importance_component']}, " \
                   f"Effort:{t['explanation']['effort_component']}, " \
                   f"Dependency:{t['explanation']['dependency_component']}"
            suggestions.append({
                'task': t,
                'explanation_text': expl
            })
        return Response({'strategy': strategy, 'suggestions': suggestions}, status=status.HTTP_200_OK)
