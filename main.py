import hashlib
import json
import os
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.utils import platform

Window.clearcolor = (0.118, 0.118, 0.118, 1)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def open_android_network_settings():
    if platform == "android":
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            intent = Intent(Settings.ACTION_WIRELESS_SETTINGS)
            PythonActivity.mActivity.startActivity(intent)
        except Exception:
            pass


class NetPadlockAndroidApp(App):
    def build(self):
        self.title = "NetPadlock"
        os.makedirs(self.user_data_dir, exist_ok=True)
        self.config_file = os.path.join(self.user_data_dir, "config.json")
        self.config_data = self.load_config()

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=[dp(24), dp(36), dp(24), dp(36)],
            spacing=dp(14),
        )
        self.render_screen()
        return self.root_layout

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f)

    def show_message(self, title: str, text: str):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        lbl = Label(text=text, halign="center", valign="middle")
        lbl.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        btn = Button(
            text="OK",
            size_hint_y=None,
            height=dp(44),
            background_normal="",
            background_color=(0.1, 0.46, 0.82, 1),
        )
        content.add_widget(lbl)
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.85, 0.35))
        btn.bind(on_release=popup.dismiss)
        popup.open()

    def render_screen(self):
        self.root_layout.clear_widgets()
        if "password_hash" not in self.config_data:
            self.build_setup_screen()
        elif self.config_data.get("locked", False):
            self.build_locked_screen()
        else:
            self.build_unlocked_screen()

    def build_setup_screen(self):
        self.root_layout.add_widget(
            Label(text="[KEY]", font_size="32sp", bold=True, color=(1, 0.7, 0, 1), size_hint_y=None, height=dp(50))
        )
        self.root_layout.add_widget(
            Label(text="CREATE MASTER PASSWORD", font_size="20sp", bold=True, color=(1, 0.7, 0, 1), size_hint_y=None, height=dp(36))
        )
        sub = Label(text="Set this once. You will use it to unlock NetPadlock.", font_size="14sp", color=(0.67, 0.67, 0.67, 1), halign="center", size_hint_y=None, height=dp(44))
        sub.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.root_layout.add_widget(sub)

        self.setup_input = TextInput(
            hint_text="Enter new master password", password=True, multiline=False, font_size="18sp",
            size_hint_y=None, height=dp(52), background_color=(0.18, 0.18, 0.18, 1),
            foreground_color=(1, 1, 1, 1), cursor_color=(1, 1, 1, 1), padding=[dp(14), dp(14)],
        )
        self.root_layout.add_widget(self.setup_input)

        save_btn = Button(
            text="SAVE MASTER PASSWORD", font_size="16sp", bold=True, size_hint_y=None, height=dp(54),
            background_normal="", background_color=(0.098, 0.463, 0.824, 1),
        )
        save_btn.bind(on_release=self.handle_save_password)
        self.root_layout.add_widget(save_btn)
        self.root_layout.add_widget(Label())

    def build_unlocked_screen(self):
        self.root_layout.add_widget(
            Label(text="[UNLOCKED]", font_size="28sp", bold=True, color=(0.3, 0.69, 0.31, 1), size_hint_y=None, height=dp(50))
        )
        self.root_layout.add_widget(
            Label(text="INTERNET UNLOCKED", font_size="22sp", bold=True, color=(0.3, 0.69, 0.31, 1), size_hint_y=None, height=dp(36))
        )
        sub = Label(text="Master password is saved. Tap below to engage lock.", font_size="14sp", color=(0.67, 0.67, 0.67, 1), halign="center", size_hint_y=None, height=dp(44))
        sub.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.root_layout.add_widget(sub)

        lock_btn = Button(
            text="LOCK INTERNET NOW", font_size="17sp", bold=True, size_hint_y=None, height=dp(58),
            background_normal="", background_color=(0.827, 0.184, 0.184, 1),
        )
        lock_btn.bind(on_release=self.handle_lock)
        self.root_layout.add_widget(lock_btn)

        reset_btn = Button(
            text="Reset Master Password", font_size="14sp", size_hint_y=None, height=dp(44),
            background_normal="", background_color=(0.18, 0.18, 0.18, 1), color=(0.7, 0.7, 0.7, 1),
        )
        reset_btn.bind(on_release=self.handle_reset_password)
        self.root_layout.add_widget(reset_btn)
        self.root_layout.add_widget(Label())

    def build_locked_screen(self):
        self.root_layout.add_widget(
            Label(text="[LOCKED]", font_size="28sp", bold=True, color=(0.957, 0.263, 0.212, 1), size_hint_y=None, height=dp(50))
        )
        self.root_layout.add_widget(
            Label(text="INTERNET LOCKED", font_size="22sp", bold=True, color=(0.957, 0.263, 0.212, 1), size_hint_y=None, height=dp(36))
        )
        sub = Label(text="Lock state persists across app restarts.\nEnter your master password to unlock.", font_size="14sp", color=(0.8, 0.8, 0.8, 1), halign="center", size_hint_y=None, height=dp(50))
        sub.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.root_layout.add_widget(sub)

        self.unlock_input = TextInput(
            hint_text="Enter master password", password=True, multiline=False, font_size="18sp",
            size_hint_y=None, height=dp(52), background_color=(0.18, 0.18, 0.18, 1),
            foreground_color=(1, 1, 1, 1), cursor_color=(1, 1, 1, 1), padding=[dp(14), dp(14)],
        )
        self.root_layout.add_widget(self.unlock_input)

        unlock_btn = Button(
            text="UNLOCK INTERNET ACCESS", font_size="16sp", bold=True, size_hint_y=None, height=dp(56),
            background_normal="", background_color=(0.22, 0.557, 0.235, 1),
        )
        unlock_btn.bind(on_release=self.handle_unlock)
        self.root_layout.add_widget(unlock_btn)

        net_btn = Button(
            text="Open Android Wireless Settings", font_size="14sp", size_hint_y=None, height=dp(44),
            background_normal="", background_color=(0.2, 0.2, 0.2, 1), color=(0.8, 0.8, 0.8, 1),
        )
        net_btn.bind(on_release=lambda *_: open_android_network_settings())
        self.root_layout.add_widget(net_btn)
        self.root_layout.add_widget(Label())

    def handle_save_password(self, *_):
        pw = self.setup_input.text.strip()
        if len(pw) < 4:
            self.show_message("Too Short", "Please enter at least 4 characters.")
            return
        self.config_data["password_hash"] = hash_password(pw)
        self.config_data["locked"] = False
        self.save_config()
        self.render_screen()

    def handle_lock(self, *_):
        self.config_data["locked"] = True
        self.save_config()
        self.render_screen()
        open_android_network_settings()

    def handle_unlock(self, *_):
        pw = self.unlock_input.text.strip()
        if hash_password(pw) == self.config_data.get("password_hash"):
            self.config_data["locked"] = False
            self.save_config()
            self.render_screen()
        else:
            self.unlock_input.text = ""
            self.show_message("Access Denied", "Incorrect master password.")

    def handle_reset_password(self, *_):
        self.config_data.pop("password_hash", None)
        self.config_data["locked"] = False
        self.save_config()
        self.render_screen()


if __name__ == "__main__":
    NetPadlockAndroidApp().run()
