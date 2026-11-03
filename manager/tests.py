import datetime

from django.test import TestCase
from django.urls import reverse

from manager.forms import TaskForm
from manager.models import Tag, Task


class TagModelTests(TestCase):
    def setUp(self) -> None:
        self.tag = Tag.objects.create(name="test_tag1")

    def test_task_type_max_length(self):
        name_max_length = self.tag._meta.get_field(
            "name"
        ).max_length

        self.assertEqual(255, name_max_length)

    def test_task_type_str(self):
        self.assertEqual(
            self.tag.name,
            str(self.tag)
        )

    def test_task_type_ordering(self):
        Tag.objects.create(name="test_tag3")
        Tag.objects.create(name="test_tag2")

        tags = Tag.objects.all()

        self.assertEqual(
            ["test_tag1", "test_tag2", "test_tag3"],
            list(tags.values_list("name", flat=True))
        )


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


class TaskModelTests(TestCase):
    def setUp(self) -> None:
        self.tag = Tag.objects.create(name="test_tag1")

        self.task = Task.objects.create(
            content="Task description 1",
            deadline=datetime.date.today(),
        )

    def test_task_str(self):
        self.assertEqual(
            self.task.content,
            str(self.task)
        )

    def test_task_ordering(self):
        Task.objects.create(
            content="Task description 3",
            is_completed=True
        )
        Task.objects.create(
            content="Task description 2",
        )

        task = Task.objects.all()

        self.assertEqual(
            ["Task description 2", "Task description 1", "Task description 3"],
            list(task.values_list("content", flat=True))
        )

    def test_tag_relationship(self):
        self.task.tags.add(self.tag)
        self.assertIn(self.tag, self.task.tags.all())
        self.assertIn(self.task, self.tag.tasks.all())


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
        self.assertEqual(
            Task.objects.get(id=self.task.id).content,
            "Task description 2"
        )
        self.assertEqual(
            Task.objects.get(id=self.task.id).deadline.date(),
            deadline
        )
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


class TaskFormTests(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name="test_tag1")
        self.tag2 = Tag.objects.create(name="test_tag2")

        self.task = Task.objects.create(
            content="Task description 1",
            deadline=datetime.date.today(),
        )

    def test_form_saves_task_with_selected_tags(self):
        deadline = datetime.date.today() - datetime.timedelta(days=1)
        form = TaskForm(
            data={
                "content": "Task description 2",
                "deadline": deadline,
                "tags": [self.tag1.pk, self.tag2.pk],
            },
            instance=self.task,
        )

        self.assertTrue(form.is_valid(), form.errors)

        task = form.save()

        self.assertEqual(task.content, "Task description 2")
        self.assertEqual(task.deadline.date(), deadline)
        self.assertCountEqual(
            task.tags.all(),
            [self.tag1, self.tag2],
        )

    def test_missing_required_fields(self):
        form = TaskForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)
