import requests
import pytest
from django.test import TestCase, TransactionTestCase
from unittest.mock import patch
from .utils import fetch_tasks_from_api, is_task_completed, create_tasks_bulk
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Task


class FetchTaskFromApiTest(TestCase):
    @patch('Tasks.utils.requests.get')
    def test_fetch_tasks_success(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'title': 'Task 1', 'description': 'Description 1', 'due_date': '2023-01-01', 'status': 'pending'},
            {'title': 'Task 2', 'description': 'Description 2', 'due_date': '2023-02-01', 'status': 'completed'}
        ]

        tasks = fetch_tasks_from_api("http://fakeapi.com/tasks")

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['title'], 'Task 1')
        self.assertEqual(tasks[1]['status'], 'completed')

    @patch('Tasks.utils.requests.get')
    def test_fetch_tasks_http_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError

        with self.assertRaises(requests.exceptions.HTTPError):
            fetch_tasks_from_api("http://fakeapi.com/tasks")

    @patch('Tasks.utils.requests.get')
    def test_fetch_tasks_invalid_json(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with self.assertRaises(ValueError):
            fetch_tasks_from_api("http://fakeapi.com/tasks")


class TaskListApiTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        Task.objects.create(title="Test Task 1", description="Description for Task 1", due_date="2024-10-15",
                            status="pending")
        Task.objects.create(title="Test Task 2", description="Description for Task 2", due_date="2024-10-20",
                            status="completed")

    def test_task_list_status_code(self):
        url = reverse('task-api-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_task_list_response_structure(self):
        url = reverse('task-api-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        first_task = response.data[0]
        self.assertIn('id', first_task)
        self.assertIn('title', first_task)
        self.assertIn('description', first_task)
        self.assertIn('due_date', first_task)
        self.assertIn('status', first_task)


@pytest.mark.parametrize("status, expected", [
    ("completed", True),
    ("pending", False),
    ("in_progress", False),
    ("completed", True),
])
def test_is_task_completed(status, expected):
    assert is_task_completed(status) == expected


@pytest.mark.django_db
@patch('Tasks.signals.send_notification')
def test_task_created_signal(mock_send_notification):
    task = Task.objects.create(
        title="New Task",
        description="Test description",
        due_date="2023-12-31",
        status="pending"
    )
    mock_send_notification.assert_called_once_with(task)


@pytest.mark.django_db
@patch('Tasks.signals.send_notification')
def test_task_created_signal_not_called_on_update(mock_send_notification):
    task = Task.objects.create(
        title="New Task",
        description="Test description",
        due_date="2023-12-31",
        status="pending"
    )
    task.title = "Updated Task"
    task.save()

    mock_send_notification.assert_called_once_with(task)


class TaskIntegrationTest(TestCase):

    def test_create_task(self):
        response = self.client.post(reverse('task_create'), {
            'title': 'Test Task',
            'description': 'Description of test task',
            'due_date': '2023-12-31',
            'status': 'pending'
        })

        url = reverse('task-api-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Test Task')

    def test_view_task(self):
        task = Task.objects.create(
            title='View Task',
            description='A task to view',
            due_date='2023-12-31',
            status='pending'
        )
        url = reverse('task-api-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'View Task')
        self.assertContains(response, 'A task to view')

    def test_update_task(self):
        task = Task.objects.create(
            title='Test Task',
            description='Initial description',
            due_date='2023-12-31',
            status='pending'
        )
        url = reverse('task_detail_update_delete', args=[task.id])

        response = self.client.patch(url, {'title': 'Updated Test'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Test')

    def test_delete_task(self):
        task = Task.objects.create(
            title='Task to Delete',
            description='Temporary task',
            due_date='2023-12-31',
            status='pending'
        )
        url = reverse('task_detail_update_delete', args=[task.id])

        response = self.client.delete(url, {'title': 'Task To Delete'})
        self.assertEqual(response.status_code, 204)


class TaskBulkCreateTest(TransactionTestCase):
    def test_create_tasks_built_sucess(self):
        tasks_data = [
            {'title': 'Task 1', 'description': 'Description 1', 'due_date': '2023-12-31', 'status': 'pending'},
            {'title': 'Task 2', 'description': 'Description 2', 'due_date': '2023-12-31', 'status': 'in_progress'},
        ]
        create_tasks_bulk(tasks_data)

        self.assertEqual(Task.objects.count(), 2)
        self.assertTrue(Task.objects.filter(title='Task 1').exists())
        self.assertTrue(Task.objects.filter(title='Task 2').exists())

    def test_create_tasks_bulk_failure(self):
        tasks_data = [
            {'title': 'Task 1', 'description': 'Description 1', 'due_date': '2023-12-31', 'status': 'pending'},
            {'title': 'Task 2', 'description': 'Description 2', 'due_date': '2023-12-31', 'status': 'in_progress'},
            {'title': 'Task 3', 'description': 'Description 3', 'due_date': 'invalid-date', 'status': 'completed'},
        ]

        with self.assertRaises(ValueError):
            create_tasks_bulk(tasks_data)

        self.assertEqual(Task.objects.count(), 0)

