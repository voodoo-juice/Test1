import os
import ssl
import json
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

# --- 1. ПРОВЕРКА И ПРИМЕНЕНИЕ ЗАЩИТЫ ANDROID (FLAG_SECURE) ---
# Блокирует создание скриншотов и запись экрана на уровне ОС Android
try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity
    window = activity.getWindow()
    WindowManager = autoclass('android.view.WindowManager$LayoutParams')
    window.setFlags(WindowManager.FLAG_SECURE, WindowManager.FLAG_SECURE)
    IS_ANDROID = True
except Exception:
    IS_ANDROID = False  # Если запуск идет на десктопе для теста


# --- 2. СТРОГИЙ SSL PINNING АДАПТЕР ---
class StrictPinningAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        cert_path = os.path.join(os.path.dirname(file), "server_cert.pem")
        
        if not os.path.exists(cert_path):
            raise FileNotFoundError(
                "Критическая ошибка безопасности: файл 'server_cert.pem' не найден! "
                "Приложение заблокировано ради безопасности."
            )
            
        context.load_verify_locations(cafile=cert_path)
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)


# --- 3. ЭКРАН АВТОРИЗАЦИИ (Логин + Пароль) ---
class LoginScreen(Screen):
    def init(self, **kwargs):
        super().init(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        layout.add_widget(Label(text='[b]Закрытый корпоративный контур[/b]', markup=True, font_size=20))
        
        self.user_input = TextInput(hint_text='Корпоративный логин', multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.user_input)
        
        self.pass_input = TextInput(hint_text='Пароль', password=True, multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.pass_input)
        
        btn = Button(text='Войти в систему', size_hint_y=None, height=50)
        btn.bind(on_press=self.do_login)
        layout.add_widget(btn)
        
        self.status_label = Label(text='', color=(1, 0.3, 0.3, 1))
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)

    def do_login(self, instance):
        username = self.user_input.text.strip()
        password = self.pass_input.text.strip()
        
        if not username or not password:
            self.status_label.text = "Заполните все поля!"
            return

        self.status_label.text = "Проверка учетных данных через защищенный VPN..."
        
        # Эндпоинт вашего закрытого сервера (доступного только через WireGuard/VPN)
        endpoint_url = "https://your-internal-server.local/api/login"
        
        session = requests.Session()
        session.mount('https://', StrictPinningAdapter())
        
        try:
            response = session.post(
                endpoint_url, 
                json={"username": username, "password": password}, 
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                session_token = data.get("token")
                
                # Передаем токен сессии на главный экран
                app = App.get_running_app()
                app.auth_token = session_token
                app.root.current = 'main_workspace'
            else:
                self.status_label.text = "Ошибка доступа: неверные данные."
                
        except Exception as e:
            self.status_label.text = f"Сетевая ошибка / Ошибка Pinning: {str(e)}"# --- 4. ОСНОВНОЙ РАБОЧИЙ ЭКРАН (Защищенный чат/лента) ---
class WorkspaceScreen(Screen):
    def init(self, **kwargs):
        super().init(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        layout.add_widget(Label(text='[b]Рабочий контур безопасности активен[/b]', markup=True, size_hint_y=None, height=40))
        
        self.msg_input = TextInput(
            text='Секретное сообщение для команды...',
            multiline=False,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(self.msg_input)
        
        btn = Button(
            text='Отправить в закрытый контур',
            size_hint_y=None,
            height=50
        )
        btn.bind(on_press=self.send_secure_message)
        layout.add_widget(btn)
        
        scroll = ScrollView(size_hint=(1, 1))
        self.output_label = Label(
            text='Статус: Ожидание отправки...',
            halign='left',
            valign='top',
            markup=True
        )
        self.output_label.bind(
            width=lambda *x: setattr(self.output_label, 'text_size', (self.output_label.width, None))
        )
        scroll.add_widget(self.output_label)
        layout.add_widget(scroll)
        
        self.add_widget(layout)

    def send_secure_message(self, instance):
        app = App.get_running_app()
        endpoint_url = "https://your-internal-server.local/api/message"
        message_text = self.msg_input.text
        
        session = requests.Session()
        session.mount('https://', StrictPinningAdapter())
        
        # Передаем токен авторизации в заголовках (Bearer Token)
        headers = {"Authorization": f"Bearer {app.auth_token}"}
        payload = {"payload": message_text}
        
        try:
            response = session.post(endpoint_url, json=payload, headers=headers, timeout=10)
            self.output_label.text = f"[color=33ff33]Успешно отправлено![/color]\nОтвет: {response.text}"
        except Exception as e:
            self.output_label.text = f"[color=ff3333]Ошибка отправки:[/color]\n{str(e)}"


# --- 5. ГЛАВНОЕ ПРИЛОЖЕНИЕ ---
class SecureCorporateApp(App):
    auth_token = None # Токен хранится только в оперативной памяти

    def build(self):
        self.title = "SecureCorp Client"
        
        # Управление экранами
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(WorkspaceScreen(name='main_workspace'))
        
        return sm


if name == 'main':
    SecureCorporateApp().run()
