from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.FloatField(default=0)
    importance = models.IntegerField(default=5)  # 1-10
    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependents')

    def __str__(self):
        return f"{self.title} (id={self.id})"
