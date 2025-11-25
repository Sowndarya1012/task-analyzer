from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    title = serializers.CharField()
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.FloatField(required=False, default=0)
    importance = serializers.IntegerField(required=False, default=5)
    dependencies = serializers.ListField(child=serializers.CharField(), required=False)

    def validate_importance(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError("importance must be between 1 and 10")
        return value
