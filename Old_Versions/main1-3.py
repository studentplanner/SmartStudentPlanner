import json
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView


DATA_FILE = "tasks.json"


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", spacing=10, padding=20)

        layout.add_widget(Label(text="Smart Student Planner Login", font_size=24))

        self.username = TextInput(hint_text="Enter Username", multiline=False)
        layout.add_widget(self.username)

        self.password = TextInput(hint_text="Enter Password", password=True, multiline=False)
        layout.add_widget(self.password)

        self.message = Label(text="")
        layout.add_widget(self.message)

        login_button = Button(text="Login")
        login_button.bind(on_press=self.validate_login)
        layout.add_widget(login_button)

        self.add_widget(layout)

    def validate_login(self, instance):
        if self.username.text.strip() == "" or self.password.text.strip() == "":
            self.message.text = "Please enter username and password"
        else:
            self.manager.current = "dashboard"


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", spacing=12, padding=20)

        layout.add_widget(Label(text="Dashboard", font_size=30))
        layout.add_widget(Label(text="Welcome to Smart Student Planner"))

        task_button = Button(text="Open Task Management")
        task_button.bind(on_press=self.open_tasks)
        layout.add_widget(task_button)

        settings_button = Button(text="Settings / Profile")
        settings_button.bind(on_press=self.open_settings)
        layout.add_widget(settings_button)

        logout_button = Button(text="Logout")
        logout_button.bind(on_press=self.logout)
        layout.add_widget(logout_button)

        self.add_widget(layout)

    def open_tasks(self, instance):
        self.manager.current = "tasks"

    def open_settings(self, instance):
        self.manager.current = "settings"

    def logout(self, instance):
        self.manager.current = "login"


class TaskManagementScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tasks = []
        self.edit_index = None

        main_layout = BoxLayout(orientation="vertical", spacing=8, padding=10)

        header_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.1), spacing=5)

        back_button = Button(text="Back")
        back_button.bind(on_press=self.go_back)
        header_row.add_widget(back_button)

        header_row.add_widget(Label(text="Task Management", font_size=24))

        main_layout.add_widget(header_row)

        self.title_input = TextInput(hint_text="Task title", multiline=False, size_hint=(1, 0.09))
        main_layout.add_widget(self.title_input)

        self.module_input = TextInput(hint_text="Module name", multiline=False, size_hint=(1, 0.09))
        main_layout.add_widget(self.module_input)

        self.due_date_input = TextInput(
            hint_text="Due date e.g. 2026-06-11",
            multiline=False,
            size_hint=(1, 0.09)
        )
        main_layout.add_widget(self.due_date_input)

        self.priority_input = Spinner(
            text="Select priority",
            values=("Low", "Medium", "High"),
            size_hint=(1, 0.09)
        )
        main_layout.add_widget(self.priority_input)

        self.notes_input = TextInput(hint_text="Notes", multiline=False, size_hint=(1, 0.09))
        main_layout.add_widget(self.notes_input)

        self.message = Label(text="", size_hint=(1, 0.07))
        main_layout.add_widget(self.message)

        button_row = BoxLayout(orientation="horizontal", spacing=5, size_hint=(1, 0.1))

        self.save_button = Button(text="Add Task")
        self.save_button.bind(on_press=self.save_task)
        button_row.add_widget(self.save_button)

        clear_button = Button(text="Clear")
        clear_button.bind(on_press=self.clear_form)
        button_row.add_widget(clear_button)

        main_layout.add_widget(button_row)

        self.search_input = TextInput(hint_text="Search tasks", multiline=False, size_hint=(1, 0.09))
        self.search_input.bind(text=self.search_tasks)
        main_layout.add_widget(self.search_input)

        scroll = ScrollView(size_hint=(1, 1))

        self.tasks_layout = BoxLayout(
            orientation="vertical",
            spacing=5,
            size_hint_y=None
        )
        self.tasks_layout.bind(minimum_height=self.tasks_layout.setter("height"))

        scroll.add_widget(self.tasks_layout)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

        self.load_tasks()
        self.display_tasks()

    def save_task(self, instance):
        title = self.title_input.text.strip()
        module = self.module_input.text.strip()
        due_date = self.due_date_input.text.strip()
        priority = self.priority_input.text
        notes = self.notes_input.text.strip()

        if title == "" or module == "" or due_date == "":
            self.message.text = "Title, module, and due date are required"
            return

        if priority == "Select priority":
            self.message.text = "Please select task priority"
            return

        task = {
            "title": title,
            "module": module,
            "due_date": due_date,
            "priority": priority,
            "notes": notes,
            "completed": False
        }

        if self.edit_index is None:
            self.tasks.append(task)
            self.message.text = "Task added successfully"
        else:
            previous_status = self.tasks[self.edit_index]["completed"]
            task["completed"] = previous_status
            self.tasks[self.edit_index] = task
            self.edit_index = None
            self.save_button.text = "Add Task"
            self.message.text = "Task updated successfully"

        self.save_tasks_to_file()
        self.clear_form(None)
        self.display_tasks()

    def display_tasks(self, filtered_tasks=None):
        self.tasks_layout.clear_widgets()

        task_list = filtered_tasks if filtered_tasks is not None else self.tasks

        if len(task_list) == 0:
            self.tasks_layout.add_widget(Label(text="No tasks found", size_hint_y=None, height=40))
            return

        for task in task_list:
            real_index = self.tasks.index(task)

            task_box = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=145,
                spacing=3,
                padding=5
            )

            status = "Completed" if task["completed"] else "Incomplete"

            task_text = (
                f"Title: {task['title']}\n"
                f"Module: {task['module']} | Due: {task['due_date']} | Priority: {task['priority']}\n"
                f"Notes: {task['notes']} | Status: {status}"
            )

            task_box.add_widget(Label(text=task_text, size_hint_y=None, height=70))

            action_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=5)

            complete_button = Button(text="Complete/Incomplete")
            complete_button.bind(on_press=lambda instance, i=real_index: self.toggle_complete(i))
            action_row.add_widget(complete_button)

            edit_button = Button(text="Edit")
            edit_button.bind(on_press=lambda instance, i=real_index: self.edit_task(i))
            action_row.add_widget(edit_button)

            delete_button = Button(text="Delete")
            delete_button.bind(on_press=lambda instance, i=real_index: self.delete_task(i))
            action_row.add_widget(delete_button)

            task_box.add_widget(action_row)
            self.tasks_layout.add_widget(task_box)

    def toggle_complete(self, index):
        self.tasks[index]["completed"] = not self.tasks[index]["completed"]
        self.save_tasks_to_file()
        self.display_tasks()

    def edit_task(self, index):
        task = self.tasks[index]

        self.title_input.text = task["title"]
        self.module_input.text = task["module"]
        self.due_date_input.text = task["due_date"]
        self.priority_input.text = task["priority"]
        self.notes_input.text = task["notes"]

        self.edit_index = index
        self.save_button.text = "Update Task"
        self.message.text = "Editing selected task"

    def delete_task(self, index):
        self.tasks.pop(index)
        self.save_tasks_to_file()
        self.message.text = "Task deleted"
        self.display_tasks()

    def search_tasks(self, instance, value):
        keyword = value.lower().strip()

        if keyword == "":
            self.display_tasks()
            return

        filtered = []

        for task in self.tasks:
            if (
                keyword in task["title"].lower()
                or keyword in task["module"].lower()
                or keyword in task["priority"].lower()
                or keyword in task["notes"].lower()
            ):
                filtered.append(task)

        self.display_tasks(filtered)

    def clear_form(self, instance):
        self.title_input.text = ""
        self.module_input.text = ""
        self.due_date_input.text = ""
        self.priority_input.text = "Select priority"
        self.notes_input.text = ""
        self.edit_index = None
        self.save_button.text = "Add Task"

    def save_tasks_to_file(self):
        with open(DATA_FILE, "w") as file:
            json.dump(self.tasks, file, indent=4)

    def load_tasks(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as file:
                    self.tasks = json.load(file)
            except:
                self.tasks = []
                self.message.text = "Could not load saved tasks"

    def go_back(self, instance):
        self.manager.current = "dashboard"


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", spacing=10, padding=20)

        layout.add_widget(Label(text="Settings / Profile", font_size=26))

        layout.add_widget(Label(text="Student Name: Demo Student"))
        layout.add_widget(Label(text="App Theme: Default"))
        layout.add_widget(Label(text="Storage: Local JSON file"))
        layout.add_widget(Label(text="Version: 1.0"))

        back_button = Button(text="Back to Dashboard")
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "dashboard"


class SmartStudentPlannerApp(App):
    def build(self):
        sm = ScreenManager()

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(TaskManagementScreen(name="tasks"))
        sm.add_widget(SettingsScreen(name="settings"))

        return sm


if __name__ == "__main__":
    SmartStudentPlannerApp().run()