import json
import os
import hashlib
import re

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup


USERS_FILE = "users.json"
TASKS_FILE = "tasks.json"

Window.size = (520, 860)
Window.clearcolor = (0.08, 0.10, 0.14, 1)

PRIMARY = (0.12, 0.34, 0.80, 1)
SUCCESS = (0.06, 0.55, 0.32, 1)
WARNING = (0.95, 0.55, 0.12, 1)
DANGER = (0.78, 0.12, 0.16, 1)
SECONDARY = (0.32, 0.35, 0.42, 1)
BG = (0.94, 0.96, 0.99, 1)
CARD = (1, 1, 1, 1)
TEXT = (0.12, 0.14, 0.18, 1)
MUTED = (0.45, 0.48, 0.55, 1)


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


class RoundedBox(BoxLayout):
    def __init__(self, bg_color=CARD, radius=18, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(radius=[radius])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class RoundedButton(Button):
    def __init__(self, text="", bg_color=PRIMARY, **kwargs):
        super().__init__(**kwargs)

        self.text = text
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self.color = (1, 1, 1, 1)
        self.font_size = 13
        self.bold = True

        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(radius=[16])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


def app_input(hint, password=False, multiline=False, height=48):
    return TextInput(
        hint_text=hint,
        password=password,
        multiline=multiline,
        size_hint_y=None,
        height=height,
        padding=(14, 12),
        font_size=15,
        background_normal="",
        background_active="",
        background_color=(1, 1, 1, 1),
        foreground_color=TEXT,
        cursor_color=PRIMARY
    )


def make_phone(content):

    outer = AnchorLayout(anchor_x="center", anchor_y="center")

    phone = RoundedBox(
        orientation="vertical",
        bg_color=BG,
        radius=40,
        size_hint=(None, None),
        size=(420, 760),
        padding=14,
        spacing=6
    )

    status_bar = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=28
    )

    status_bar.add_widget(Label(
        text="9:41",
        font_size=12,
        bold=True,
        color=TEXT
    ))

    status_bar.add_widget(Label(
        text="Smart Planner",
        font_size=11,
        color=MUTED
    ))

    status_bar.add_widget(Label(
        text="● ● ●",
        font_size=10,
        color=TEXT
    ))

    phone.add_widget(status_bar)
    phone.add_widget(content)

    outer.add_widget(phone)

    return outer


def popup_message(title, message, color=PRIMARY):

    content = BoxLayout(
        orientation="vertical",
        padding=15,
        spacing=10
    )

    content.add_widget(Label(
        text=message,
        color=TEXT,
        font_size=15
    ))

    popup = Popup(
        title=title,
        content=content,
        size_hint=(0.75, 0.28),
        auto_dismiss=True
    )

    popup.open()

    Clock.schedule_once(lambda dt: popup.dismiss(), 3)


class ProtectedScreen(Screen):
    def on_pre_enter(self):

        app = App.get_running_app()

        if app.current_user is None:
            self.manager.current = "login"


class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        content = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=16
        )

        content.add_widget(Label(
            text="Smart Student Planner",
            font_size=28,
            bold=True,
            color=PRIMARY,
            size_hint_y=None,
            height=80
        ))

        card = RoundedBox(
            orientation="vertical",
            spacing=10,
            padding=16,
            size_hint_y=None,
            height=320
        )

        self.username = app_input("Username")
        card.add_widget(self.username)

        self.password = app_input("Password", password=True)
        card.add_widget(self.password)

        self.message = Label(
            text="",
            color=DANGER,
            size_hint_y=None,
            height=30
        )

        card.add_widget(self.message)

        login_button = RoundedButton(
            "LOGIN",
            PRIMARY,
            size_hint_y=None,
            height=48
        )

        login_button.bind(on_press=self.login_user)
        card.add_widget(login_button)

        signup_button = RoundedButton(
            "CREATE ACCOUNT",
            SUCCESS,
            size_hint_y=None,
            height=48
        )

        signup_button.bind(on_press=self.open_signup)
        card.add_widget(signup_button)

        content.add_widget(card)

        self.add_widget(make_phone(content))

    def login_user(self, instance):

        username = self.username.text.strip()
        password = self.password.text.strip()

        users = load_json(USERS_FILE, {})

        if username == "" or password == "":
            self.message.text = "Enter username and password"
            return

        if username not in users:
            self.message.text = "Account not found"
            return

        if users[username]["password"] != hash_password(password):
            self.message.text = "Incorrect password"
            return

        App.get_running_app().current_user = username

        self.manager.get_screen("dashboard").refresh_dashboard()
        self.manager.get_screen("tasks").load_user_tasks()

        self.manager.current = "dashboard"

    def open_signup(self, instance):
        self.manager.current = "signup"


class SignupScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        content = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=16
        )

        content.add_widget(Label(
            text="Create Account",
            font_size=26,
            bold=True,
            color=PRIMARY,
            size_hint_y=None,
            height=60
        ))

        card = RoundedBox(
            orientation="vertical",
            spacing=10,
            padding=16
        )

        self.full_name = app_input("Full name")
        card.add_widget(self.full_name)

        self.username = app_input("Username")
        card.add_widget(self.username)

        self.password = app_input("Password", password=True)
        card.add_widget(self.password)

        self.confirm_password = app_input("Confirm password", password=True)
        card.add_widget(self.confirm_password)

        self.message = Label(
            text="",
            color=DANGER,
            size_hint_y=None,
            height=30
        )

        card.add_widget(self.message)

        signup_button = RoundedButton(
            "SIGN UP",
            SUCCESS,
            size_hint_y=None,
            height=48
        )

        signup_button.bind(on_press=self.signup_user)
        card.add_widget(signup_button)

        back_button = RoundedButton(
            "BACK TO LOGIN",
            SECONDARY,
            size_hint_y=None,
            height=48
        )

        back_button.bind(on_press=self.go_back)
        card.add_widget(back_button)

        content.add_widget(card)

        self.add_widget(make_phone(content))

    def signup_user(self, instance):

        full_name = self.full_name.text.strip()
        username = self.username.text.strip()
        password = self.password.text.strip()
        confirm_password = self.confirm_password.text.strip()

        users = load_json(USERS_FILE, {})

        if full_name == "" or username == "" or password == "" or confirm_password == "":
            self.message.text = "All fields required"
            return

        if len(username) < 3:
            self.message.text = "Username too short"
            return

        if len(password) < 6:
            self.message.text = "Password too short"
            return

        if password != confirm_password:
            self.message.text = "Passwords do not match"
            return

        if username in users:
            self.message.text = "Username already exists"
            return

        users[username] = {
            "full_name": full_name,
            "password": hash_password(password)
        }

        save_json(USERS_FILE, users)

        popup_message("Success", "Account created successfully", SUCCESS)

        self.manager.current = "login"

    def go_back(self, instance):
        self.manager.current = "login"


class DashboardScreen(ProtectedScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        content = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=16
        )

        content.add_widget(Label(
            text="Dashboard",
            font_size=28,
            bold=True,
            color=PRIMARY,
            size_hint_y=None,
            height=60
        ))

        self.welcome = Label(
            text="",
            font_size=18,
            color=TEXT,
            size_hint_y=None,
            height=40
        )

        content.add_widget(self.welcome)

        task_button = RoundedButton(
            "TASK MANAGEMENT",
            PRIMARY,
            size_hint_y=None,
            height=50
        )

        task_button.bind(on_press=self.open_tasks)
        content.add_widget(task_button)

        add_button = RoundedButton(
            "ADD NEW TASK",
            SUCCESS,
            size_hint_y=None,
            height=50
        )

        add_button.bind(on_press=self.open_add_task)
        content.add_widget(add_button)

        settings_button = RoundedButton(
            "SETTINGS / PROFILE",
            SECONDARY,
            size_hint_y=None,
            height=50
        )

        settings_button.bind(on_press=self.open_settings)
        content.add_widget(settings_button)

        logout_button = RoundedButton(
            "LOGOUT",
            DANGER,
            size_hint_y=None,
            height=50
        )

        logout_button.bind(on_press=self.logout)
        content.add_widget(logout_button)

        self.add_widget(make_phone(content))

    def refresh_dashboard(self):

        app = App.get_running_app()

        users = load_json(USERS_FILE, {})

        if app.current_user in users:
            self.welcome.text = f"Welcome, {users[app.current_user]['full_name']}"

    def open_tasks(self, instance):
        self.manager.current = "tasks"

    def open_add_task(self, instance):

        screen = self.manager.get_screen("add_task")
        screen.prepare_for_add()

        self.manager.current = "add_task"

    def open_settings(self, instance):
        self.manager.current = "settings"

    def logout(self, instance):

        App.get_running_app().current_user = None
        self.manager.current = "login"


class TaskManagementScreen(ProtectedScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tasks = []

        content = BoxLayout(
            orientation="vertical",
            spacing=8,
            padding=10
        )

        header = BoxLayout(
            orientation="horizontal",
            spacing=6,
            size_hint_y=None,
            height=48
        )

        back = RoundedButton(
            "‹",
            SECONDARY,
            size_hint_x=None,
            width=45
        )

        back.bind(on_press=self.go_back)
        header.add_widget(back)

        header.add_widget(Label(
            text="Tasks",
            font_size=24,
            bold=True,
            color=PRIMARY
        ))

        refresh = RoundedButton(
            "↻",
            PRIMARY,
            size_hint_x=None,
            width=45
        )

        refresh.bind(on_press=self.refresh_tasks)
        header.add_widget(refresh)

        content.add_widget(header)

        add_button = RoundedButton(
            "ADD NEW TASK",
            SUCCESS,
            size_hint_y=None,
            height=48
        )

        add_button.bind(on_press=self.open_add_task)
        content.add_widget(add_button)

        self.search_input = app_input(
            "Search tasks",
            height=44
        )

        self.search_input.bind(text=self.search_tasks)

        content.add_widget(self.search_input)

        self.feedback = Label(
            text="",
            color=SUCCESS,
            size_hint_y=None,
            height=24
        )

        content.add_widget(self.feedback)

        scroll = ScrollView()

        self.tasks_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None
        )

        self.tasks_layout.bind(
            minimum_height=self.tasks_layout.setter("height")
        )

        scroll.add_widget(self.tasks_layout)
        content.add_widget(scroll)

        self.add_widget(make_phone(content))

    def on_pre_enter(self):

        super().on_pre_enter()

        self.load_user_tasks()
        self.display_tasks()

    def load_user_tasks(self):

        app = App.get_running_app()

        all_tasks = load_json(TASKS_FILE, [])

        self.tasks = [
            t for t in all_tasks
            if t.get("username") == app.current_user
        ]

    def save_user_tasks(self):

        app = App.get_running_app()

        all_tasks = load_json(TASKS_FILE, [])

        others = [
            t for t in all_tasks
            if t.get("username") != app.current_user
        ]

        save_json(TASKS_FILE, others + self.tasks)

    def display_tasks(self, filtered_tasks=None):

        self.tasks_layout.clear_widgets()

        task_list = filtered_tasks if filtered_tasks else self.tasks

        if not task_list:

            empty = RoundedBox(
                orientation="vertical",
                size_hint_y=None,
                height=100
            )

            empty.add_widget(Label(
                text="No saved tasks",
                color=TEXT,
                font_size=18
            ))

            self.tasks_layout.add_widget(empty)

            return

        for task in task_list:

            index = self.tasks.index(task)

            card = RoundedBox(
                orientation="horizontal",
                spacing=10,
                padding=10,
                size_hint_y=None,
                height=150
            )

            left = BoxLayout(
                orientation="vertical",
                spacing=2,
                size_hint_x=0.70,
                padding=(5, 0)
            )

            left.add_widget(Label(
                text=task["title"],
                font_size=16,
                bold=True,
                color=SUCCESS if task["completed"] else TEXT,
                halign="left",
                text_size=(240, None)
            ))

            left.add_widget(Label(
                text=f"Status: {'Completed' if task['completed'] else 'Incomplete'}",
                font_size=13,
                color=SUCCESS if task["completed"] else WARNING,
                halign="left",
                text_size=(240, None)
            ))

            left.add_widget(Label(
                text=f"Module: {task['module']}",
                font_size=13,
                color=MUTED,
                halign="left",
                text_size=(240, None)
            ))

            left.add_widget(Label(
                text=f"Due: {task['due_date']} | {task['priority']}",
                font_size=13,
                color=MUTED,
                halign="left",
                text_size=(240, None)
            ))

            left.add_widget(Label(
                text=f"Notes: {task['notes']}",
                font_size=12,
                color=TEXT,
                halign="left",
                text_size=(240, None)
            ))

            right = BoxLayout(
                orientation="vertical",
                spacing=5,
                size_hint_x=0.30
            )

            complete = RoundedButton(
                "DONE" if not task["completed"] else "UNDO",
                SUCCESS,
                size_hint_y=None,
                height=36
            )

            complete.bind(
                on_press=lambda instance, i=index: self.toggle_complete(i)
            )

            right.add_widget(complete)

            edit = RoundedButton(
                "EDIT",
                WARNING,
                size_hint_y=None,
                height=36
            )

            edit.bind(
                on_press=lambda instance, i=index: self.open_edit_task(i)
            )

            right.add_widget(edit)

            delete = RoundedButton(
                "DELETE",
                DANGER,
                size_hint_y=None,
                height=36
            )

            delete.bind(
                on_press=lambda instance, i=index: self.delete_task(i)
            )

            right.add_widget(delete)

            card.add_widget(left)
            card.add_widget(right)

            self.tasks_layout.add_widget(card)

    def toggle_complete(self, index):

        self.tasks[index]["completed"] = not self.tasks[index]["completed"]

        self.save_user_tasks()

        self.feedback.text = "Task status updated"

        self.display_tasks()

    def open_edit_task(self, index):

        screen = self.manager.get_screen("add_task")

        screen.prepare_for_edit(index, self.tasks[index])

        self.manager.current = "add_task"

    def delete_task(self, index):

        self.tasks.pop(index)

        self.save_user_tasks()

        popup_message("Deleted", "Task deleted successfully", DANGER)

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
                or keyword in task["notes"].lower()
                or keyword in task["priority"].lower()
                or keyword in status
            ):
                filtered.append(task)

        self.display_tasks(filtered)

    def refresh_tasks(self, instance):

        self.load_user_tasks()

        self.display_tasks()

        popup_message("Refresh", "Tasks refreshed successfully", PRIMARY)

    def open_add_task(self, instance):

        screen = self.manager.get_screen("add_task")

        screen.prepare_for_add()

        self.manager.current = "add_task"

    def go_back(self, instance):

        self.manager.current = "dashboard"


class AddTaskScreen(ProtectedScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.edit_index = None

        content = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=16
        )

        self.page_title = Label(
            text="Add Task",
            font_size=26,
            bold=True,
            color=PRIMARY,
            size_hint_y=None,
            height=60
        )

        content.add_widget(self.page_title)

        card = RoundedBox(
            orientation="vertical",
            spacing=10,
            padding=16
        )

        self.title_input = app_input("Task title")
        card.add_widget(self.title_input)

        self.module_input = app_input("Module name")
        card.add_widget(self.module_input)

        self.due_date_input = app_input("Due date YYYY-MM-DD")
        card.add_widget(self.due_date_input)

        self.priority_input = Spinner(
            text="Select priority",
            values=("Low", "Medium", "High"),
            size_hint_y=None,
            height=48
        )

        card.add_widget(self.priority_input)

        self.notes_input = app_input(
            "Notes",
            multiline=True,
            height=90
        )

        card.add_widget(self.notes_input)

        self.message = Label(
            text="",
            color=DANGER,
            size_hint_y=None,
            height=30
        )

        card.add_widget(self.message)

        row = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=48
        )

        self.save_button = RoundedButton("SAVE", SUCCESS)

        self.save_button.bind(on_press=self.save_task)

        row.add_widget(self.save_button)

        clear = RoundedButton("CLEAR", SECONDARY)

        clear.bind(on_press=self.clear_form)

        row.add_widget(clear)

        card.add_widget(row)

        content.add_widget(card)

        back = RoundedButton(
            "BACK TO TASKS",
            PRIMARY,
            size_hint_y=None,
            height=48
        )

        back.bind(on_press=self.go_back)

        content.add_widget(back)

        self.add_widget(make_phone(content))

    def prepare_for_add(self):

        self.edit_index = None

        self.page_title.text = "Add Task"

        self.save_button.text = "SAVE"

        self.clear_form(None)

    def prepare_for_edit(self, index, task):

        self.edit_index = index

        self.page_title.text = "Edit Task"

        self.save_button.text = "UPDATE"

        self.title_input.text = task["title"]
        self.module_input.text = task["module"]
        self.due_date_input.text = task["due_date"]
        self.priority_input.text = task["priority"]
        self.notes_input.text = task["notes"]

    def save_task(self, instance):

        app = App.get_running_app()

        title = self.title_input.text.strip()
        module = self.module_input.text.strip()
        due_date = self.due_date_input.text.strip()
        priority = self.priority_input.text
        notes = self.notes_input.text.strip()

        if title == "" or module == "" or due_date == "":
            self.message.text = "Required fields missing"
            return

        if not re.match(r"^\d{4}-\d{2}-\d{2}$", due_date):
            self.message.text = "Use YYYY-MM-DD format"
            return

        all_tasks = load_json(TASKS_FILE, [])

        user_tasks = [
            t for t in all_tasks
            if t.get("username") == app.current_user
        ]

        others = [
            t for t in all_tasks
            if t.get("username") != app.current_user
        ]

        task = {
            "username": app.current_user,
            "title": title,
            "module": module,
            "due_date": due_date,
            "priority": priority,
            "notes": notes,
            "completed": False
        }

        if self.edit_index is None:

            user_tasks.append(task)

            popup_message("Success", "Task added successfully", SUCCESS)

        else:

            task["completed"] = user_tasks[self.edit_index]["completed"]

            user_tasks[self.edit_index] = task

            popup_message("Success", "Task updated successfully", SUCCESS)

        save_json(TASKS_FILE, others + user_tasks)

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

        content = BoxLayout(
            orientation="vertical",
            spacing=12,
            padding=16
        )

        content.add_widget(Label(
            text="Profile",
            font_size=26,
            bold=True,
            color=PRIMARY,
            size_hint_y=None,
            height=60
        ))

        card = RoundedBox(
            orientation="vertical",
            padding=16
        )

        self.profile_info = Label(
            text="",
            color=TEXT,
            font_size=15
        )

        card.add_widget(self.profile_info)

        content.add_widget(card)

        back = RoundedButton(
            "BACK TO DASHBOARD",
            PRIMARY,
            size_hint_y=None,
            height=48
        )

        back.bind(on_press=self.go_back)

        content.add_widget(back)

        logout = RoundedButton(
            "LOGOUT",
            DANGER,
            size_hint_y=None,
            height=48
        )

        logout.bind(on_press=self.logout)

        content.add_widget(logout)

        self.add_widget(make_phone(content))

    def on_pre_enter(self):

        super().on_pre_enter()

        app = App.get_running_app()

        users = load_json(USERS_FILE, {})

        if app.current_user in users:

            user = users[app.current_user]

            self.profile_info.text = (
                f"Full Name: {user['full_name']}\n\n"
                f"Username: {app.current_user}\n\n"
                f"Authentication: Local Login\n\n"
                f"Storage: JSON Local Storage"
            )

    def go_back(self, instance):

        self.manager.current = "dashboard"

    def logout(self, instance):

        App.get_running_app().current_user = None

        self.manager.current = "login"


class SmartStudentPlannerApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_user = None

    def build(self):

        sm = ScreenManager(
            transition=FadeTransition(duration=0.15)
        )

        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(TaskManagementScreen(name="tasks"))
        sm.add_widget(AddTaskScreen(name="add_task"))
        sm.add_widget(SettingsScreen(name="settings"))

        return sm


if __name__ == "__main__":
    SmartStudentPlannerApp().run()