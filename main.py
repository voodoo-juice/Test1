import os
import json
import hashlib
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen


# ============================================================
# НАСТРОЙКИ
# ============================================================

Window.size = (400, 700)

APP_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FILE = os.path.join(
    APP_DIR,
    "forum_data.json"
)

SESSION_FILE = os.path.join(
    APP_DIR,
    "session.json"
)


# ============================================================
# ЦВЕТА
# ============================================================

BG_COLOR = (0.045, 0.045, 0.045, 1)
PANEL_COLOR = (0.105, 0.085, 0.085, 1)
PANEL2_COLOR = (0.15, 0.12, 0.12, 1)

RED = (0.72, 0.04, 0.04, 1)
RED_LIGHT = (1.0, 0.16, 0.16, 1)

TEXT = (0.92, 0.92, 0.92, 1)
GRAY = (0.55, 0.55, 0.55, 1)
GREEN = (0.25, 0.9, 0.3, 1)


# ============================================================
# БАЗА ДАННЫХ
# ============================================================

DEFAULT_DATA = {
    "users": [
        {
            "id": 1,
            "username": "admin",
            "password": "admin123",
            "role": "admin"
        }
    ],

    "sections": [
        {
            "id": 1,
            "title": "Общий раздел",
            "description": "Общие обсуждения"
        },
        {
            "id": 2,
            "title": "Разработка & APK",
            "description": "Python, Kivy, Android и разработка"
        },
        {
            "id": 3,
            "title": "Безопасность",
            "description": "Сети, защита и приватность"
        },
        {
            "id": 4,
            "title": "Торговля / Обмен",
            "description": "Объявления и обмен"
        },
        {
            "id": 5,
            "title": "Оффтоп",
            "description": "Свободное общение"
        }
    ],

    "threads": [
        {
            "id": 1,
            "section_id": 1,
            "title": "Добро пожаловать!",
            "author": "admin",
            "replies": 2
        },
        {
            "id": 2,
            "section_id": 2,
            "title": "Обсуждение Kivy",
            "author": "admin",
            "replies": 1
        }
    ],

    "messages": [
        {
            "id": 1,
            "thread_id": 1,
            "username": "admin",
            "text": "Добро пожаловать на форум!",
            "date": "Сегодня"
        },
        {
            "id": 2,
            "thread_id": 1,
            "username": "admin",
            "text": "Здесь можно создавать темы и отвечать.",
            "date": "Сегодня"
        },
        {
            "id": 3,
            "thread_id": 2,
            "username": "admin",
            "text": "Обсуждаем разработку приложений на Kivy.",
            "date": "Сегодня"
        }
    ]
}


def load_data():

    if not os.path.exists(DATA_FILE):

        save_data(DEFAULT_DATA)

        return DEFAULT_DATA.copy()

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        save_data(DEFAULT_DATA)

        return DEFAULT_DATA.copy()


def save_data(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# СЕССИЯ
# ============================================================

def save_session(username):

    with open(
        SESSION_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "username": username
            },
            f
        )


def load_session():

    if not os.path.exists(SESSION_FILE):
        return None

    try:

        with open(
            SESSION_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return None


def clear_session():

    if os.path.exists(SESSION_FILE):

        try:
            os.remove(SESSION_FILE)
        except Exception:
            pass


# ============================================================
# ФОН
# ============================================================

class ColoredBox(BoxLayout):

    def __init__(
        self,
        bg_color=BG_COLOR,
        **kwargs
    ):

        super().__init__(**kwargs)

        with self.canvas.before:

            Color(*bg_color)

            self.rect = Rectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.update_rect,
            size=self.update_rect
        )

    def update_rect(self, *args):

        self.rect.pos = self.pos
        self.rect.size = self.size


# ============================================================
# КНОПКА
# ============================================================

class ForumButton(Button):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.background_normal = ""

        self.background_color = PANEL2_COLOR

        self.color = TEXT

        self.font_size = dp(15)

        self.halign = "left"

        self.valign = "middle"

        self.padding = (
            dp(15),
            dp(10)
        )

        self.bind(
            size=self.update_text
        )

    def update_text(self, *args):

        self.text_size = (
            self.width - dp(30),
            None
        )


# ============================================================
# INPUT
# ============================================================

class DarkInput(TextInput):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.background_color = PANEL2_COLOR

        self.foreground_color = TEXT

        self.cursor_color = RED_LIGHT

        self.padding = [
            dp(12),
            dp(12)
        ]

        self.multiline = False


# ============================================================
# СООБЩЕНИЕ
# ============================================================

def show_message(
    title,
    message
):

    root = ColoredBox(
        orientation="vertical",
        padding=dp(15),
        spacing=dp(15)
    )

    label = Label(
        text=message,
        color=TEXT,
        halign="center",
        valign="middle"
    )

    close = Button(
        text="ЗАКРЫТЬ",
        size_hint_y=None,
        height=dp(45),
        background_normal="",
        background_color=RED,
        color=TEXT
    )

    root.add_widget(label)

    root.add_widget(close)

    from kivy.uix.popup import Popup

    popup = Popup(
        title=title,
        content=root,
        size_hint=(0.9, 0.4),
        separator_color=RED
    )

    close.bind(
        on_release=popup.dismiss
    )

    popup.open()


# ============================================================
# LOGIN
# ============================================================

class LoginScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        root = ColoredBox(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(12)
        )

        title = Label(
            text="[b]UNDERGROUND FORUM[/b]",
            markup=True,
            font_size=dp(25),
            color=RED_LIGHT,
            size_hint_y=None,
            height=dp(65)
        )

        subtitle = Label(
            text="ЗАКРЫТОЕ СООБЩЕСТВО",
            color=GRAY,
            size_hint_y=None,
            height=dp(30)
        )

        self.username = DarkInput(
            hint_text="Логин"
        )

        self.password = DarkInput(
            hint_text="Пароль",
            password=True
        )

        login = Button(
            text="ВОЙТИ",
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_color=RED,
            color=TEXT
        )

        register = Button(
            text="РЕГИСТРАЦИЯ",
            size_hint_y=None,
            height=dp(45),
            background_normal="",
            background_color=PANEL2_COLOR,
            color=RED_LIGHT
        )

        self.status = Label(
            text="",
            color=RED_LIGHT,
            halign="center"
        )

        root.add_widget(title)
        root.add_widget(subtitle)
        root.add_widget(self.username)
        root.add_widget(self.password)
        root.add_widget(login)
        root.add_widget(register)
        root.add_widget(self.status)

        self.add_widget(root)

        login.bind(
            on_release=self.login
        )

        register.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "register"
            )
        )

    def login(self, instance):

        username = self.username.text.strip()

        password = self.password.text

        if not username or not password:

            self.status.text = (
                "Введите логин и пароль."
            )

            return

        data = load_data()

        for user in data["users"]:

            if (
                user["username"] == username
                and
                user["password"] == password
            ):

                save_session(username)

                self.username.text = ""
                self.password.text = ""

                forum = self.manager.get_screen(
                    "forum"
                )

                forum.refresh()

                self.manager.current = "forum"

                return

        self.status.text = (
            "Неверный логин или пароль."
        )


# ============================================================
# REGISTER
# ============================================================

class RegisterScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        root = ColoredBox(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(12)
        )

        title = Label(
            text="[b]РЕГИСТРАЦИЯ[/b]",
            markup=True,
            font_size=dp(23),
            color=RED_LIGHT,
            size_hint_y=None,
            height=dp(55)
        )

        self.username = DarkInput(
            hint_text="Придумайте логин"
        )

        self.password = DarkInput(
            hint_text="Пароль",
            password=True
        )

        self.password2 = DarkInput(
            hint_text="Повторите пароль",
            password=True
        )

        create = Button(
            text="СОЗДАТЬ АККАУНТ",
            size_hint_y=None,
            height=dp(50),
            background_normal="",
            background_color=RED,
            color=TEXT
        )

        back = Button(
            text="< НАЗАД",
            size_hint_y=None,
            height=dp(42),
            background_normal="",
            background_color=PANEL2_COLOR,
            color=RED_LIGHT
        )

        self.status = Label(
            text="",
            color=RED_LIGHT
        )

        root.add_widget(title)
        root.add_widget(self.username)
        root.add_widget(self.password)
        root.add_widget(self.password2)
        root.add_widget(create)
        root.add_widget(back)
        root.add_widget(self.status)

        self.add_widget(root)

        create.bind(
            on_release=self.register
        )

        back.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "login"
            )
        )

    def register(self, instance):

        username = self.username.text.strip()

        password = self.password.text

        password2 = self.password2.text

        if len(username) < 3:

            self.status.text = (
                "Логин должен быть минимум 3 символа."
            )

            return

        if len(password) < 4:

            self.status.text = (
                "Пароль должен быть минимум 4 символа."
            )

            return

        if password != password2:

            self.status.text = (
                "Пароли не совпадают."
            )

            return

        data = load_data()

        for user in data["users"]:

            if user["username"].lower() == username.lower():

                self.status.text = (
                    "Такой пользователь уже существует."
                )

                return

        new_id = 1

        for user in data["users"]:

            new_id = max(
                new_id,
                user["id"] + 1
            )

        data["users"].append(
            {
                "id": new_id,
                "username": username,
                "password": password,
                "role": "user"
            }
        )

        save_data(data)

        show_message(
            "Готово",
            "Аккаунт создан.\n\n"
            "Теперь можно войти."
        )

        self.username.text = ""
        self.password.text = ""
        self.password2.text = ""

        self.manager.current = "login"


# ============================================================
# ФОРУМ
# ============================================================

class ForumScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        root = ColoredBox(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        header = BoxLayout(
            size_hint_y=None,
            height=dp(55)
        )

        title = Label(
            text="[b]UNDERGROUND[/b]",
            markup=True,
            font_size=dp(22),
            color=RED_LIGHT
        )

        profile = Button(
            text="ПРОФИЛЬ",
            size_hint_x=None,
            width=dp(100),
            background_normal="",
            background_color=PANEL2_COLOR,
            color=TEXT
        )

        header.add_widget(title)
        header.add_widget(profile)

        root.add_widget(header)

        self.scroll = ScrollView()

        self.list_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        self.list_layout.bind(
            minimum_height=
            self.list_layout.setter("height")
        )

        self.scroll.add_widget(
            self.list_layout
        )

        root.add_widget(
            self.scroll
        )

        self.add_widget(root)

        profile.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "profile"
            )
        )

    def on_pre_enter(self):

        self.refresh()

    def refresh(self):

        self.list_layout.clear_widgets()

        data = load_data()

        session = load_session()

        if not session:
            return

        username = session["username"]

        current_user = None

        for user in data["users"]:

            if user["username"] == username:

                current_user = user

                break

        if (
            current_user
            and
            current_user["role"] == "admin"
        ):

            admin = Button(
                text="⚙ АДМИН-ПАНЕЛЬ",
                size_hint_y=None,
                height=dp(50),
                background_normal="",
                background_color=RED,
                color=TEXT
            )

            self.list_layout.add_widget(
                admin
            )

            admin.bind(
                on_release=lambda x:
                setattr(
                    self.manager,
                    "current",
                    "admin"
                )
            )

        for section in data["sections"]:

            thread_count = 0

            for thread in data["threads"]:

                if (
                    thread["section_id"]
                    ==
                    section["id"]
                ):

                    thread_count += 1

            text = (
                "[b]"
                + section["title"]
                + "[/b]\n"
                "[size=12]"
                + section["description"]
                + "[/size]\n"
                "[size=10]"
                + "Тем: "
                + str(thread_count)
                + "[/size]"
            )

            button = ForumButton(
                text=text,
                markup=True,
                size_hint_y=None,
                height=dp(85)
            )

            button.bind(
                on_release=
                lambda x, s=section:
                self.open_section(s)
            )

            self.list_layout.add_widget(
                button
            )

    def open_section(self, section):

        screen = self.manager.get_screen(
            "threads"
        )

        screen.load_threads(
            section["id"],
            section["title"]
        )

        self.manager.current = "threads"


# ============================================================
# ТЕМЫ
# ============================================================

class ThreadScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.section_id = None

        root = ColoredBox(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        back = Button(
            text="< РАЗДЕЛЫ",
            size_hint_y=None,
            height=dp(42),
            background_normal="",
            background_color=PANEL2_COLOR,
            color=RED_LIGHT
        )

        self.title = Label(
            text="Раздел",
            markup=True,
            font_size=dp(20),
            color=TEXT,
            size_hint_y=None,
            height=dp(45)
        )

        self.scroll = ScrollView()

        self.list_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        self.list_layout.bind(
            minimum_height=
            self.list_layout.setter("height")
        )

        self.scroll.add_widget(
            self.list_layout
        )

        root.add_widget(back)
        root.add_widget(self.title)
        root.add_widget(self.scroll)

        self.add_widget(root)

        back.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "forum"
            )
        )

    def load_threads(
        self,
        section_id,
        title
    ):

        self.section_id = section_id

        self.title.text = (
            "[b]"
            + title
            + "[/b]"
        )

        self.list_layout.clear_widgets()

        create = Button(
            text="+ СОЗДАТЬ НОВУЮ ТЕМУ",
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_color=RED,
            color=TEXT
        )

        self.list_layout.add_widget(
            create
        )

        create.bind(
            on_release=lambda x:
            self.open_create()
        )

        data = load_data()

        found = False

        for thread in data["threads"]:

            if (
                thread["section_id"]
                ==
                section_id
            ):

                found 
