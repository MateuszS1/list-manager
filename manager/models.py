from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    content = models.CharField(max_length=255)
    datetime = models.DateTimeField()
    deadline = models.DateTimeField(null=True)
    is_completed = models.BooleanField(default=False)
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="tasks",
    )

    class Meta:
        ordering = ["content"]

    def __str__(self):
        return self.content
