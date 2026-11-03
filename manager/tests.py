import datetime

from django.test import TestCase
from django.urls import reverse

from manager.models import Tag, Task


class TagViewsTest(TestCase):
    def setUp(self) -> None:
        self.tag = Tag.objects.create(name="test_tag1")

    def test_create_tag(self):
        self.client.post(
            reverse(
                "manager:tag-create"
            ),
            {"name": "test_tag2"},
        )
        self.assertEqual(Tag.objects.get(id=2).name, "test_tag2")

    def test_update_tag(self):
        response = self.client.post(
            reverse(
                "manager:tag-update", kwargs={"pk": self.tag.id}
            ),
            {"name": "new_test_tag1"},
        )
        Tag.objects.get(id=self.tag.id).refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Tag.objects.get(id=self.tag.id).name, "new_test_tag1"
        )

    def test_delete_tag(self):
        response = self.client.post(
            reverse("manager:tag-delete", kwargs={"pk": self.tag.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Tag.objects.filter(id=self.tag.id).exists()
        )


class TaskViewsTest(TestCase):
    def setUp(self) -> None:
        self.tag = Tag.objects.create(name="test_tag1")

        self.task = Task.objects.create(
            content="Task description 1",
            deadline=datetime.date.today(),
        )

    def test_create_task(self):
        response = self.client.post(
            reverse("manager:task-create"),
            {
                "content": "Task description 2",
            },
        )
        self.assertEqual(response.status_code, 302)

        task = Task.objects.get(content="Task description 2")

        self.assertEqual(task.content, "Task description 2")
        self.assertEqual(task.tags.count(), 0)

    def test_update_task_status(self):
        deadline = datetime.date.today() - datetime.timedelta(days=1)
        response = self.client.post(
            reverse("manager:task-update", kwargs={"pk": self.task.id}),
            {
                "pk": self.task.id,
                "content": "Task description 2",
                "deadline": deadline,
                "tags": [self.tag.id],
            },
        )
        Task.objects.get(id=self.task.id).refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.get(id=self.task.id).content, "Task description 2")
        self.assertEqual(Task.objects.get(id=self.task.id).deadline.date(), deadline)
        self.assertEqual(Task.objects.get(id=self.task.id).tags.count(), 1)

    def test_swap_task_status(self):
        response = self.client.post(
            reverse("manager:task-swap", kwargs={"pk": self.task.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.get(id=self.task.id).is_completed)

    def test_delete_task(self):
        response = self.client.post(
            reverse("manager:task-delete", kwargs={"pk": self.task.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())
