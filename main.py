import hashlib
import json
import os
import flet as ft


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def main(page: ft.Page):
    page.title = "NetPadlock"
    page.bgcolor = "#1e1e1e"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 24
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    storage_dir = os.getenv("FLET_APP_STORAGE_DATA") or "."
    os.makedirs(storage_dir, exist_ok=True)
    config_file = os.path.join(storage_dir, "config.json")

    def load_config():
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_config(data):
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    config = load_config()

    def show_snack(msg: str, color: str = "#d32f2f"):
        page.show_dialog(ft.SnackBar(content=ft.Text(msg, color="white"), bgcolor=color))

    def render():
        page.controls.clear()

        # 1. Setup Screen
        if "password_hash" not in config:
            pw_field = ft.TextField(
                label="New Master Password",
                password=True,
                can_reveal_password=True,
                bgcolor="#2d2d2d",
                border_color="#ffb300",
            )

            def on_save(e):
                pw = (pw_field.value or "").strip()
                if len(pw) < 4:
                    show_snack("Enter at least 4 characters.")
                    return
                config["password_hash"] = hash_password(pw)
                config["locked"] = False
                save_config(config)
                render()

            page.add(
                ft.Icon(ft.Icons.VPN_KEY_ROUNDED, size=64, color="#ffb300"),
                ft.Text("CREATE MASTER PASSWORD", size=20, weight=ft.FontWeight.BOLD, color="#ffb300"),
                ft.Text(
                    "Set this once. You will use it to unlock NetPadlock.",
                    size=13,
                    color="#aaaaaa",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=12),
                pw_field,
                ft.Container(height=8),
                ft.Button(
                    content="SAVE MASTER PASSWORD",
                    bgcolor="#1976d2",
                    color="white",
                    width=320,
                    height=50,
                    on_click=on_save,
                ),
            )

        # 2. Locked Screen
        elif config.get("locked", False):
            unlock_field = ft.TextField(
                label="Enter Master Password",
                password=True,
                can_reveal_password=True,
                bgcolor="#2d2d2d",
                border_color="#f44336",
            )

            def on_unlock(e):
                pw = (unlock_field.value or "").strip()
                if hash_password(pw) == config.get("password_hash"):
                    config["locked"] = False
                    save_config(config)
                    render()
                else:
                    unlock_field.value = ""
                    show_snack("Incorrect master password.")

            page.add(
                ft.Icon(ft.Icons.LOCK_ROUNDED, size=72, color="#f44336"),
                ft.Text("INTERNET LOCKED", size=22, weight=ft.FontWeight.BOLD, color="#f44336"),
                ft.Text(
                    "Lock persists across restarts.\nEnter your master password to unlock.",
                    size=13,
                    color="#cccccc",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=12),
                unlock_field,
                ft.Container(height=8),
                ft.Button(
                    content="UNLOCK INTERNET ACCESS",
                    bgcolor="#388e3c",
                    color="white",
                    width=320,
                    height=50,
                    on_click=on_unlock,
                ),
            )

        # 3. Unlocked Screen
        else:
            def on_lock(e):
                config["locked"] = True
                save_config(config)
                render()

            def on_reset(e):
                config.pop("password_hash", None)
                config["locked"] = False
                save_config(config)
                render()

            page.add(
                ft.Icon(ft.Icons.LOCK_OPEN_ROUNDED, size=72, color="#4caf50"),
                ft.Text("INTERNET UNLOCKED", size=22, weight=ft.FontWeight.BOLD, color="#4caf50"),
                ft.Text(
                    "Master password is saved. Tap below to engage lock.",
                    size=13,
                    color="#aaaaaa",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=16),
                ft.Button(
                    content="LOCK INTERNET NOW",
                    bgcolor="#d32f2f",
                    color="white",
                    width=320,
                    height=54,
                    on_click=on_lock,
                ),
                ft.TextButton(content="Reset Master Password", on_click=on_reset),
            )

        page.update()

    render()


ft.run(main)
