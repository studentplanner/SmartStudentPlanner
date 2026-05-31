import json
import os
import hashlib
import re

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup


USERS_FILE = "users.json"
TASKS_FILE = "tasks.json"

Window.size = (430, 720)
Window.clearcolor = (0.94, 0.96, 0.98, 1)


PRIMARY = (0.12, 0.36, 0.78, 1)
SUCCESS = (0.10, 0.55, 0.25, 1)
WARNING = (0.95, 0.55, 0.10, 1)
DANGER = (0.75, 0.10, 0.10, 1)
SECONDARY = (0.35, 0.35, 0.35, 1)
LIGHT = (0.98, 0.98, 0.98, 1)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_json(filename, default_data):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except:
            return default_data
    return default_data


def save_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def styled_button(text, color=PRIMARY):
    return Button(
        text=text,
        background_normal="",
        background_color=color,
        color=(1, 1, 1, 1),
        font_size=15,
        bold=True
    )


def message_popup(title, message, color=PRIMARY):
    content = BoxLayout(orientation="vertical", padding=15, spacing=10)
    content.add_widget(Label(text=message, font_size=16))

    close_button = styled_button("OK", color)
    content.add_widget(close_button)

    popup = Popup(
        title=title,
        content=content,
        size_hint=(0.82, 0.42),
        auto_dismiss=False
    )

    close_button.bind(on_press=popup.dismiss)
    popup.open()


class Card(BoxLayout):
    def __init__(self, bg_color=LIGHT, **kwargs):
        super().__init__(**kwargs)
        self.padding = 10
        self.spacing = 8

        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(radius=[12])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ProtectedScreen(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()
        if app.current_user is None:
            self.manager.current = "login"


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=25, spacing=12)

        layout.add_widget(Label(
            text="Smart Student Planner",
            font_size=28,
            bold=True,
            color=PRIMARY,
            size_hint=(1, 0.18)
        ))

        layout.add_widget(Label(
            text="Login to continue",
            font_size=18,
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(1, 0.08)
        ))

        self.username = TextInput(hint_text="Username", multiline=False, size_hint=(1, 0.1))
        layout.add_widget(self.username)

        self.password = TextInput(hint_text="Password", password=True, multiline=False, size_hint=(1, 0.1))
        layout.add_widget(self.password)

        self.message = Label(text="", color=DANGER, size_hint=(1, 0.08))
        layout.add_widget(self.message)

        login_button = styled_button("LOGIN", PRIMARY)
        login_button.size_hint = (1, 0.11)
        login_button.bind(on_press=self.login_user)
        layout.add_widget(login_button)

        signup_button = styled_button("CREATE ACCOUNT", SUCCESS)
        signup_button.size_hint = (1, 0.11)
        signup_button.bind(on_press=self.open_signup)
        layout.add_widget(signup_button)

        self.add_widget(layout)

    def login_user(self, instance):
        username = self.username.text.strip()
        password = self.password.text.strip()

        if username == "" or password == "":
            self.message.text = "Username and password are required"
            return

        users = load_json(USERS_FILE, {})

        if username not in users:
            self.message.text = "Account does not exist"
            return

        if users[username]["password"] != hash_password(password):
            self.message.text = "Incorrect password"
            return

        app = App.get_running_app()
        app.current_user = username

        self.username.text = ""
        self.password.text = ""
        self.message.text = ""

        self.manager.get_screen("dashboard").refresh_dashboard()
        self.manager.get_screen("tasks").load_user_tasks()
        self.manager.get_screen("tasks").display_tasks()

        self.manager.current = "dashboard"

    def open_signup(self, instance):
        self.manager.current = "signup"


class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=25, spacing=10)

        layout.add_widget(Label(
            text="Create Account",
            font_size=26,
            bold=True,
            color=PRIMARY,
            size_hint=(1, 0.14)
        ))

        self.full_name = TextInput(hint_text="Full name", multiline=False, size_hint=(1, 0.1))
        layout.add_widget(self.full_name)

        self.username = TextInput(hint_text="Username", multiline=False, size_hint=(1, 0.1))
        layout.add_widget(self.username)

        self.password = TextInput(hint_text="Password", password=True, multiline=False, size_hint=(1, 0.1))
        layout.add_widget(self.password)

        self.confirm_password = TextInput(
            hint_text="Confirm password",
            password=True,
            multiline=False,
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.confirm_password)

        self.message = Label(text="", color=DANGER, size_hint=(1, 0.08))
        layout.add_widget(self.message)

        signup_button = styled_button("SIGN UP", SUCCESS)
        signup_button.size_hint = (1, 0.11)
        signup_button.bind(on_press=self.signup_user)
        layout.add_widget(signup_button)

        back_button = styled_button("BACK TO LOGIN", SECONDARY)
        back_button.size_hint = (1, 0.11)
        back_button.bind(on_press=self.go_to_login)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def signup_user(self, instance):
        full_name = self.full_name.text.strip()
        username = self.username.text.strip()
        password = self.password.text.strip()
        confirm_password = self.confirm_password.text.strip()

        if full_name == "" or username == "" or password == "" or confirm_password == "":
            self.message.text = "All fields are required"
            return

        if len(username) < 3:
            self.message.text = "Username must be at least 3 characters"
            return

        if len(password) < 6:
            self.message.text = "Password must be at least 6 characters"
            return

        if password != confirm_password:
            self.message.text = "Passwords do not match"
            return

        users = load_json(USERS_FILE, {})

        if username in users:
            self.message.text = "Username already exists"
            return

        users[username] = {
            "full_name": full_name,
            "password": hash_password(password)
        }

        save_json(USERS_FILE, users)

        self.full_name.text = ""
        self.username.text = ""
        self.password.text = ""
        self.confirm_password.text = ""
        self.message.text = ""

        message_popup("Success", "Account created successfully. You can now login.", SUCCESS)
        self.manager.current = "login"

    def go_to_login(self, instance):
        self.manager.current = "login"


class DashboardScreen(ProtectedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=25, spacing=15)

        layout.add_widget(Label(
            text="Dashboard",
            font_size=30,
            bold=True,
            color=PRIMARY,
            size_hint=(1, 0.18)
        ))

        self.welcome = Label(text="", font_size=18, color=(0.2, 0.2, 0.2, 1), size_hint=(1, 0.12))
        layout.add_widget(self.welcome)

        task_button = styled_button("OPEN TASK MANAGEMENT", PRIMARY)
        task_button.size_hint = (1, 0.13)
        task_button.bind(on_press=self.open_tasks)
        layout.add_widget(task_button)

        add_button = styled_button("ADD NEW TASK", SUCCESS)
        add_button.size_hint = (1, 0.13)
        add_button.bind(on_press=self.open_add_task)
        layout.add_widget(add_button)

        settings_button = styled_button("SETTINGS / PROFILE", SECONDARY)
        settings_button.size_hint = (1, 0.13)
        settings_button.bind(on_press=self.open_settings)
        layout.add_widget(settings_button)

        logout_button = styled_button("LOGOUT", DANGER)
        logout_button.size_hint = (1, 0.13)
        logout_button.bind(on_press=self.logout)
        layout.add_widget(logout_button)

        self.add_widget(layout)

    def refresh_dashboard(self):
        app = App.get_running_app()
        users = load_json(USERS_FILE, {})

        if app.current_user in users:
            self.welcome.text = f"Welcome, {users[app.current_user]['full_name']}"
        else:
            self.welcome.text = "Welcome"

    def open_tasks(self, instance):
        self.manager.current = "tasks"

    def open_add_task(self, instance):
        add_screen = self.manager.get_screen("add_task")
        add_screen.prepare_for_add()
        self.manager.current = "add_task"

    def open_settings(self, instance):
        self.manager.current = "settings"

    def logout(self, instance):
        app = App.get_running_app()
        app.current_user = None
        self.manager.current = "login"


class TaskManagementScreen(ProtectedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tasks = []

        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        header = BoxLayout(orientation="horizontal", spacing=6, size_hint=(1, 0.08))

        back_button = styled_button("BACK", SECONDARY)
        back_button.size_hint = (0.25, 1)
        back_button.bind(on_press=self.go_back)
        header.add_widget(back_button)

        header.add_widget(Label(
            text="Task Management",
            font_size=22,
            bold=True,
            color=PRIMARY
        ))

        root.add_widget(header)

        add_button = styled_button("ADD NEW TASK", SUCCESS)
        add_button.size_hint = (1, 0.08)
        add_button.bind(on_press=self.open_add_task)
        root.add_widget(add_button)

        self.search_input = TextInput(
            hint_text="Search tasks by title, module, priority, status, or notes",
            multiline=False,
            size_hint=(1, 0.07)
        )
        self.search_input.bind(text=self.search_tasks)
        root.add_widget(self.search_input)

        self.feedback = Label(text="", color=SUCCESS, size_hint=(1, 0.05))
        root.add_widget(self.feedback)

        task_scroll = ScrollView(size_hint=(1, 1))

        self.tasks_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.tasks_layout.bind(minimum_height=self.tasks_layout.setter("height"))

        task_scroll.add_widget(self.tasks_layout)
        root.add_widget(task_scroll)

        self.add_widget(root)

    def on_pre_enter(self):
        super().on_pre_enter()
        self.load_user_tasks()
        self.display_tasks()

    def load_user_tasks(self):
        app = App.get_running_app()
        all_tasks = load_json(TASKS_FILE, [])

        if app.current_user is None:
            self.tasks = []
        else:
            self.tasks = [
                task for task in all_tasks
                if task.get("username") == app.current_user
            ]

    def save_user_tasks(self):
        app = App.get_running_app()
        all_tasks = load_json(TASKS_FILE, [])

        other_users_tasks = [
            task for task in all_tasks
            if task.get("username") != app.current_user
        ]

        save_json(TASKS_FILE, other_users_tasks + self.tasks)

    def display_tasks(self, filtered_tasks=None):
        self.tasks_layout.clear_widgets()

        task_list = filtered_tasks if filtered_tasks is not None else self.tasks

        if len(task_list) == 0:
            empty_card = Card(orientation="vertical", size_hint_y=None, height=100)
            empty_card.add_widget(Label(
                text="No saved tasks found.\nClick ADD NEW TASK to create one.",
                font_size=16,
                color=(0.25, 0.25, 0.25, 1)
            ))
            self.tasks_layout.add_widget(empty_card)
            return

        for task in task_list:
            real_index = self.tasks.index(task)

            status = "Completed" if task["completed"] else "Incomplete"

            card = Card(orientation="horizontal", size_hint_y=None, height=135)

            left_side = BoxLayout(orientation="vertical", spacing=3, size_hint=(0.68, 1))

            title_color = SUCCESS if task["completed"] else PRIMARY

            left_side.add_widget(Label(
                text=f"{task['title']} [{status}]",
                font_size=16,
                bold=True,
                color=title_color,
                halign="left",
                valign="middle"
            ))

            left_side.add_widget(Label(
                text=f"Module: {task['module']}",
                font_size=14,
                color=(0.15, 0.15, 0.15, 1),
                halign="left"
            ))

            left_side.add_widget(Label(
                text=f"Due: {task['due_date']} | Priority: {task['priority']}",
                font_size=14,
                color=(0.15, 0.15, 0.15, 1),
                halign="left"
            ))

            left_side.add_widget(Label(
                text=f"Notes: {task['notes']}",
                font_size=13,
                color=(0.25, 0.25, 0.25, 1),
                halign="left"
            ))

            right_side = BoxLayout(orientation="vertical", spacing=5, size_hint=(0.32, 1))

            complete_button = styled_button("COMPLETE" if not task["completed"] else "INCOMPLETE", SUCCESS)
            complete_button.bind(on_press=lambda instance, i=real_index: self.toggle_complete(i))
            right_side.add_widget(complete_button)

            edit_button = styled_button("EDIT", WARNING)
            edit_button.bind(on_press=lambda instance, i=real_index: self.open_edit_task(i))
            right_side.add_widget(edit_button)

            delete_button = styled_button("DELETE", DANGER)
            delete_button.bind(on_press=lambda instance, i=real_index: self.delete_task(i))
            right_side.add_widget(delete_button)

            card.add_widget(left_side)
            card.add_widget(right_side)

            self.tasks_layout.add_widget(card)

    def toggle_complete(self, index):
        self.tasks[index]["completed"] = not self.tasks[index]["completed"]
        self.save_user_tasks()
        self.feedback.text = "Task status updated"
        self.display_tasks()

    def open_edit_task(self, index):
        add_screen = self.manager.get_screen("add_task")
        add_screen.prepare_for_edit(index, self.tasks[index])
        self.manager.current = "add_task"

    def delete_task(self, index):
        self.tasks.pop(index)
        self.save_user_tasks()
        self.feedback.text = "Task deleted successfully"
        message_popup("Deleted", "Task deleted successfully.", DANGER)
        self.display_tasks()

    def search_tasks(self, instance, value):
        keyword = value.lower().strip()

        if keyword == "":
            self.display_tasks()
            return

        filtered = []

        for task in self.tasks:
            status = "completed" if task["completed"] else "incomplete"

            if (
                keyword in task["title"].lower()
                or keyword in task["module"].lower()
                or keyword in task["due_date"].lower()
                or keyword in task["priority"].lower()
                or keyword in task["notes"].lower()
                or keyword in status
            ):
                filtered.append(task)

        self.display_tasks(filtered)

    def open_add_task(self, instance):
        add_screen = self.manager.get_screen("add_task")
        add_screen.prepare_for_add()
        self.manager.current = "add_task"

    def go_back(self, instance):
        self.manager.current = "dashboard"


class AddTaskScreen(ProtectedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.edit_index = None

        root = BoxLayout(orientation="vertical", padding=18, spacing=10)

        self.page_title = Label(
            text="Add New Task",
            font_size=25,
            bold=True,
            color=PRIMARY,
            size_hint=(1, 0.12)
        )
        root.add_widget(self.page_title)

        self.title_input = TextInput(hint_text="Task title", multiline=False, size_hint=(1, 0.09))
        root.add_widget(self.title_input)

        self.module_input = TextInput(hint_text="Module name", multiline=False, size_hint=(1, 0.09))
        root.add_widget(self.module_input)

        self.due_date_input = TextInput(hint_text="Due date e.g. 2026-06-11", multiline=False, size_hint=(1, 0.09))
        root.add_widget(self.due_date_input)

        self.priority_input = Spinner(
            text="Select priority",
            values=("Low", "Medium", "High"),
            size_hint=(1, 0.09)
        )
        root.add_widget(self.priority_input)

        self.notes_input = TextInput(hint_text="Notes", multiline=True, size_hint=(1, 0.18))
        root.add_widget(self.notes_input)

        self.message = Label(text="", color=DANGER, size_hint=(1, 0.07))
        root.add_widget(self.message)

        button_row = BoxLayout(orientation="horizontal", spacing=6, size_hint=(1, 0.1))

        self.save_button = styled_button("SAVE TASK", SUCCESS)
        self.save_button.bind(on_press=self.save_task)
        button_row.add_widget(self.save_button)

        clear_button = styled_button("CLEAR", SECONDARY)
        clear_button.bind(on_press=self.clear_form)
        button_row.add_widget(clear_button)

        root.add_widget(button_row)

        back_button = styled_button("BACK TO TASKS", PRIMARY)
        back_button.size_hint = (1, 0.1)
        back_button.bind(on_press=self.go_back)
        root.add_widget(back_button)

        self.add_widget(root)

    def prepare_for_add(self):
        self.edit_index = None
        self.page_title.text = "Add New Task"
        self.save_button.text = "SAVE TASK"
        self.clear_form(None)

    def prepare_for_edit(self, index, task):
        self.edit_index = index
        self.page_title.text = "Edit Task"
        self.save_button.text = "UPDATE TASK"

        self.title_input.text = task["title"]
        self.module_input.text = task["module"]
        self.due_date_input.text = task["due_date"]
        self.priority_input.text = task["priority"]
        self.notes_input.text = task["notes"]
        self.message.text = ""

    def save_task(self, instance):
        app = App.get_running_app()

        if app.current_user is None:
            message_popup("Access Denied", "Please login first.", DANGER)
            self.manager.current = "login"
            return

        title = self.title_input.text.strip()
        module = self.module_input.text.strip()
        due_date = self.due_date_input.text.strip()
        priority = self.priority_input.text
        notes = self.notes_input.text.strip()

        if title == "" or module == "" or due_date == "":
            self.message.text = "Title, module, and due date are required"
            return

        if priority == "Select priority":
            self.message.text = "Please select a priority"
            return

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", due_date):
            self.message.text = "Use date format YYYY-MM-DD"
            return

        all_tasks = load_json(TASKS_FILE, [])

        user_tasks = [
            task for task in all_tasks
            if task.get("username") == app.current_user
        ]

        other_tasks = [
            task for task in all_tasks
            if task.get("username") != app.current_user
        ]

        new_task = {
            "username": app.current_user,
            "title": title,
            "module": module,
            "due_date": due_date,
            "priority": priority,
            "notes": notes,
            "completed": False
        }

        if self.edit_index is None:
            user_tasks.append(new_task)
            message_popup("Success", "Task added successfully.", SUCCESS)
        else:
            new_task["completed"] = user_tasks[self.edit_index]["completed"]
            user_tasks[self.edit_index] = new_task
            message_popup("Success", "Task updated successfully.", SUCCESS)

        save_json(TASKS_FILE, other_tasks + user_tasks)

        self.clear_form(None)

        tasks_screen = self.manager.get_screen("tasks")
        tasks_screen.load_user_tasks()
        tasks_screen.display_tasks()

        self.manager.current = "tasks"

    def clear_form(self, instance):
        self.title_input.text = ""
        self.module_input.text = ""
        self.due_date_input.text = ""
        self.priority_input.text = "Select priority"
        self.notes_input.text = ""
        self.message.text = ""

    def go_back(self, instance):
        self.manager.current = "tasks"


class SettingsScreen(ProtectedScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=25, spacing=14)

        layout.add_widget(Label(
            text="Settings / Profile",
            font_size=26,
            bold=True,
            color=PRIMARY,
            size_hint=(1, 0.16)
        ))

        self.profile_info = Label(
            text="",
            font_size=16,
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(1, 0.46)
        )
        layout.add_widget(self.profile_info)

        back_button = styled_button("BACK TO DASHBOARD", PRIMARY)
        back_button.size_hint = (1, 0.12)
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        logout_button = styled_button("LOGOUT", DANGER)
        logout_button.size_hint = (1, 0.12)
        logout_button.bind(on_press=self.logout)
        layout.add_widget(logout_button)

        self.add_widget(layout)

    def on_pre_enter(self):
        super().on_pre_enter()

        app = App.get_running_app()
        users = load_json(USERS_FILE, {})
        all_tasks = load_json(TASKS_FILE, [])

        task_count = len([
            task for task in all_tasks
            if task.get("username") == app.current_user
        ])

        if app.current_user in users:
            user = users[app.current_user]
            self.profile_info.text = (
                f"Full Name: {user['full_name']}\n"
                f"Username: {app.current_user}\n"
                f"Saved Tasks: {task_count}\n"
                f"Authentication: Local username/password\n"
                f"Password Security: SHA-256 hashing\n"
                f"Task Storage: Local JSON file\n"
                f"App Version: 1.0"
            )

    def go_back(self, instance):
        self.manager.current = "dashboard"

    def logout(self, instance):
        app = App.get_running_app()
        app.current_user = None
        self.manager.current = "login"


class SmartStudentPlannerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None

    def build(self):
        sm = ScreenManager()

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(TaskManagementScreen(name="tasks"))
        sm.add_widget(AddTaskScreen(name="add_task"))
        sm.add_widget(SettingsScreen(name="settings"))

        return sm


if __name__ == "__main__":
    SmartStudentPlannerApp().run()