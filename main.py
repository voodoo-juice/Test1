import os
import ssl
import threading
import requests

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock


# ============================================================
# НАСТРОЙКИ СЕРВЕРА
# ============================================================

SERVER_URL = "https://6aad5eb7a2413bf0ec119cf8.mockapi.io/api"


LOGIN_URL = SERVER_URL + "/api/login"
MESSAGE_URL = SERVER_URL + "/api/message"


# ============================================================
# ANDROID FLAG_SECURE
# Запрещает обычные скриншоты и запись экрана приложения
# ============================================================

def enable_secure_screen():
    try:
        from jnius import autoclass

        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        activity = PythonActivity.mActivity
        window = activity.getWindow()

        WindowManager = autoclass(
            "android.view.WindowManager$LayoutParams"
        )

        window.setFlags(
            WindowManager.FLAG_SECURE,
            WindowManager.FLAG_SECURE
        )

        return True

    except Exception:
        return False


# ============================================================
# HTTPS / SSL
# ============================================================

class StrictHTTPSAdapter(requests.adapters.HTTPAdapter):

    def init_poolmanager(self, *args, **kwargs):

        context = ssl.create_default_context()

        cert_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "server_cert.pem"
        )

        if not os.path.isfile(cert_path):
            raise FileNotFoundError(
                "Файл server_cert.pem не найден. "
                "Соединение заблокировано."
            )

        context.load_verify_locations(
            cafile=cert_path
        )

        kwargs["ssl_context"] = context

        return super().init_poolmanager(
            *args,
            **kwargs
        )


def create_secure_session():

    session = requests.Session()

    session.mount(
        "https://",
        StrictHTTPSAdapter()
    )

    return session


# ============================================================
# ЭКРАН ВХОДА
# ============================================================

class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=40,
            spacing=15
        )

        title = Label(
            text="[b]Закрытый корпоративный контур[/b]",
            markup=True,
            font_size=22,
            size_hint_y=None,
            height=60
        )

        layout.add_widget(title)

        self.user_input = TextInput(
            hint_text="Корпоративный логин",
            multiline=False,
            size_hint_y=None,
            height=55
        )

        layout.add_widget(self.user_input)

        self.pass_input = TextInput(
            hint_text="Пароль",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=55
        )

        layout.add_widget(self.pass_input)

        self.login_button = Button(
            text="Войти в систему",
            size_hint_y=None,
            height=55
        )

        self.login_button.bind(
            on_press=self.do_login
        )

        layout.add_widget(self.login_button)

        self.status_label = Label(
            text="",
            halign="center",
            valign="middle"
        )

        layout.add_widget(
            self.status_label
        )

        self.add_widget(layout)


    def do_login(self, instance):

        username = self.user_input.text.strip()
        password = self.pass_input.text

        if not username or not password:

            self.status_label.text = (
                "Введите логин и пароль."
            )

            return

        self.login_button.disabled = True

        self.status_label.text = (
            "Проверка учетных данных..."
        )

        thread = threading.Thread(
            target=self.login_request,
            args=(username, password),
            daemon=True
        )

        thread.start()


    def login_request(self, username, password):

        try:

            session = create_secure_session()

            response = session.post(
                LOGIN_URL,
                json={
                    "username": username,
                    "password": password
                },
                timeout=10
            )

            if response.status_code == 200:

                try:
                    data = response.json()
                except Exception:
                    data = {}

                token = data.get("token")

                if not token:

                    Clock.schedule_once(
                        lambda dt: self.login_failed(
                            "Сервер не вернул токен."
                        )
                    )

                    return

                app = App.get_running_app()

                app.auth_token = token

                Clock.schedule_once(
                    lambda dt: self.login_success()
                )

            elif response.status_code in (401, 403):

                Clock.schedule_once(
                    lambda dt: self.login_failed(
                        "Неверный логин или пароль."
                    )
                )

            else:

                Clock.schedule_once(
                    lambda dt: self.login_failed(
                        "Сервер вернул ошибку: "
                        + str(response.status_code)
                    )
                )

        except Exception as e:

            Clock.schedule_once(
                lambda dt: self.login_failed(
                    "Ошибка соединения:\n" + str(e)
                )
            )


    def login_success(self):

        self.login_button.disabled = False

        self.pass_input.text = ""

        self.status_label.text = ""

        self.manager.current = "workspace"


    def login_failed(self, message):

        self.login_button.disabled = False

        self.status_label.text = message


# ============================================================
# РАБОЧИЙ ЭКРАН
# ============================================================

class WorkspaceScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=12
        )

        title = Label(
            text="[b]Рабочий контур активен[/b]",
            markup=True,
            font_size=20,
            size_hint_y=None,
            height=50
        )

        layout.add_widget(title)

        self.msg_input = TextInput(
            hint_text="Введите сообщение...",
            multiline=True,
            size_hint_y=None,
            height=100
        )

        layout.add_widget(
            self.msg_input
        )

        self.send_button = Button(
            text="Отправить в закрытый контур",
            size_hint_y=None,
            height=55
        )

        self.send_button.bind(
            on_press=self.send_message
        )

        layout.add_widget(
            self.send_button
        )

        scroll = ScrollView()

        self.output_label = Label(
            text="Статус: готов к работе.",
            halign="left",
            valign="top",
            size_hint_y=None,
            markup=True
        )

        self.output_label.bind(
            texture_size=self.output_label.setter(
                "size"
            )
        )

        scroll.add_widget(
            self.output_label
        )

        layout.add_widget(
            scroll
        )

        logout_button = Button(
            text="Выйти",
            size_hint_y=None,
            height=50
        )

        logout_button.bind(
            on_press=self.logout
        )

        layout.add_widget(
            logout_button
        )

        self.add_widget(layout)


    def send_message(self, instance):

        app = App.get_running_app()

        if not app.auth_token:

            self.output_label.text = (
                "[color=ff3333]"
                "Ошибка: пользователь не авторизован."
                "[/color]"
            )

            return

        message = self.msg_input.text.strip()

        if not message:

            self.output_label.text = (
                "Введите сообщение."
            )

            return

        self.send_button.disabled = True

        self.output_label.text = (
            "Отправка сообщения..."
        )

        thread = threading.Thread(
            target=self.message_request,
            args=(message,),
            daemon=True
        )

        thread.start()


    def message_request(self, message):

        try:

            app = App.get_running_app()

            session = create_secure_session()

            headers = {
                "Authorization":
                    "Bearer " + app.auth_token
            }

            response = session.post(
                MESSAGE_URL,
                json={
                    "payload": message
                },
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:

                try:
                    server_answer = response.text
                except Exception:
                    server_answer = "OK"

                Clock.schedule_once(
                    lambda dt: self.message_success(
                        server_answer
                    )
                )

            elif response.status_code == 401:

                Clock.schedule_once(
                    lambda dt: self.session_expired()
                )

            else:

                Clock.schedule_once(
                    lambda dt: self.message_error(
                        "Сервер вернул HTTP "
                        + str(response.status_code)
                    )
                )

        except Exception as e:

            Clock.schedule_once(
                lambda dt: self.message_error(
                    str(e)
                )
            )


    def message_success(self, answer):

        self.send_button.disabled = False

        self.output_label.text = (
            "[color=33ff33]"
            "[b]Сообщение успешно отправлено![/b]"
            "[/color]\n\n"
            "Ответ сервера:\n"
            + answer
        )

        self.msg_input.text = ""


    def message_error(self, error):

        self.send_button.disabled = False

        self.output_label.text = (
            "[color=ff3333]"
            "[b]Ошибка отправки[/b]"
            "[/color]\n\n"
            + error
        )


    def session_expired(self):

        self.send_button.disabled = False

        app = App.get_running_app()

        app.auth_token = None

        self.output_label.text = (
            "Сессия закончилась. "
            "Войдите снова."
        )

        self.manager.current = "login"


    def logout(self, instance):

        app = App.get_running_app()

        app.auth_token = None

        self.msg_input.text = ""

        self.output_label.text = (
            "Статус: выполнен выход."
        )

        self.manager.current = "login"


# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================

class SecureCorporateApp(App):

    auth_token = None

    def build(self):

        self.title = "SecureCorp Client"

        enable_secure_screen()

        manager = ScreenManager()

        manager.add_widget(
            LoginScreen(
                name="login"
            )
        )

        manager.add_widget(
            WorkspaceScreen(
                name="workspace"
            )
        )

        return manager


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    SecureCorporateApp().run()
