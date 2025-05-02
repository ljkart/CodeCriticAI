"""Module to manage review tasks."""

import uuid
from threading import Thread


class TaskManager:
    """
    Manages asynchronous tasks using threads.

    This class provides functionality to start background tasks, track their
    status,
    and retrieve their results.

    Attributes:
        tasks (dict): Dictionary storing task information with task_id as keys.
    """

    def __init__(self):
        """
        Initialize a new TaskManager instance.

        Creates an empty dictionary to store task information.
        """
        self.tasks = {}

    def start_task(self, target, *args, **kwargs):
        """
        Start a new asynchronous task in a separate thread.

        Args:
            target (callable): The function to be executed in the thread.
            *args: Variable length argument list to pass to the target
                function.
            **kwargs: Arbitrary keyword arguments to pass to the target
                function.

        Returns:
            str: A unique task_id (UUID) that can be used to track the task's
                status.
        """
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {"status": "starting", "result": None}

        thread = Thread(
            target=target, args=(task_id, *args, self), kwargs=kwargs
        )
        thread.start()
        return task_id

    def update_status(self, task_id, status):
        """
        Update the status of a task.

        Args:
            task_id (str): The unique identifier of the task.
            status (str): The new status to set for the task.
        """
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status

    def complete(self, task_id, result):
        """
        Mark a task as complete and store its result.

        Args:
            task_id (str): The unique identifier of the task.
            result (any): The result data to store for the completed task.
        """
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "done"
            self.tasks[task_id]["result"] = result

    def get_task_status(self, task_id):
        """
        Retrieve the current status and result of a task.

        Args:
            task_id (str): The unique identifier of the task.

        Returns:
            dict: A dictionary containing the task's status and result.
                 If the task_id doesn't exist, returns a dictionary with
                 status "not_found" and result None.
        """
        return self.tasks.get(task_id, {"status": "not_found", "result": None})
