import ctypes
import hashlib
import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

CONFIG_DIR = os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "NetPadlock")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
RULE_NAME_OUT = "NetPadlock_Block_Out"
RULE_NAME_IN = "NetPadlock_Block_In"
TASK_NAME = "NetPadlock_BootLock"


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    if getattr(sys, "frozen", False):
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, "", None, 1
        )
    else:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{os.path.abspath(__file__)}"', None, 1
        )
    sys.exit()


def run_cmd(cmd):
    subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def is_firewall_locked():
    result = subprocess.run(
        f'netsh advfirewall firewall show rule name="{RULE_NAME_OUT}"',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    return result.returncode == 0


def set_boot_autostart(enable):
    if enable:
        if getattr(sys, "frozen", False):
            target = f'\\"{sys.executable}\\"'
        else:
            py_dir = os.path.dirname(sys.executable)
            pythonw = os.path.join(py_dir, "pythonw.exe")
            exe_to_use = pythonw if os.path.exists(pythonw) else sys.executable
            script_path = os.path.abspath(__file__)
            target = f'\\"{exe_to_use}\\" \\"{script_path}\\"'
        run_cmd(
            f'schtasks /create /tn "{TASK_NAME}" /tr "{target}" /sc onlogon /rl highest /f'
        )
    else:
        run_cmd(f'schtasks /delete /tn "{TASK_NAME}" /f')


def lock_internet():
    unlock_internet()
    run_cmd(
        f'netsh advfirewall firewall add rule name="{RULE_NAME_OUT}" dir=out action=block profile=any'
    )
    run_cmd(
        f'netsh advfirewall firewall add rule name="{RULE_NAME_IN}" dir=in action=block profile=any'
    )
    set_boot_autostart(True)


def unlock_internet():
    run_cmd(f'netsh advfirewall firewall delete rule name="{RULE_NAME_OUT}"')
    run_cmd(f'netsh advfirewall firewall delete rule name="{RULE_NAME_IN}"')
    set_boot_autostart(False)


class NetPadlockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NetPadlock - Hardware-Style Kill Switch")
        self.root.geometry("420x390")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e1e")

        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.config = self.load_config()

        self.main_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.main_frame.pack(expand=True, fill="both", padx=30, pady=25)

        self.render_screen()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def render_screen(self):
        self.clear_frame()
        if "password_hash" not in self.config:
            self.build_setup_screen()
        elif is_firewall_locked():
            self.build_locked_screen()
        else:
            self.build_unlocked_screen()

    def build_setup_screen(self):
        tk.Label(
            self.main_frame,
            text="🔑",
            font=("Segoe UI Emoji", 48),
            bg="#1e1e1e",
            fg="#ffb300",
        ).pack(pady=(5, 5))

        tk.Label(
            self.main_frame,
            text="CREATE MASTER PASSWORD",
            font=("Segoe UI", 13, "bold"),
            bg="#1e1e1e",
            fg="#ffb300",
        ).pack()

        tk.Label(
            self.main_frame,
            text="Set this once. You will use it to unlock your internet.",
            font=("Segoe UI", 9),
            bg="#1e1e1e",
            fg="#aaaaaa",
        ).pack(pady=(2, 18))

        self.setup_entry = tk.Entry(
            self.main_frame,
            show="*",
            font=("Segoe UI", 12),
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="white",
            relief="flat",
        )
        self.setup_entry.pack(fill="x", ipady=6, pady=(4, 18))
        self.setup_entry.focus()
        self.setup_entry.bind("<Return>", lambda e: self.handle_save_master_password())

        tk.Button(
            self.main_frame,
            text="SAVE MASTER PASSWORD",
            font=("Segoe UI", 11, "bold"),
            bg="#1976d2",
            fg="white",
            activebackground="#1565c0",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.handle_save_master_password,
        ).pack(fill="x", ipady=10)

    def build_unlocked_screen(self):
        tk.Label(
            self.main_frame,
            text="🔓",
            font=("Segoe UI Emoji", 60),
            bg="#1e1e1e",
            fg="#4caf50",
        ).pack(pady=(10, 5))

        tk.Label(
            self.main_frame,
            text="INTERNET UNLOCKED",
            font=("Segoe UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#4caf50",
        ).pack()

        tk.Label(
            self.main_frame,
            text="Master password is saved. Click below for instant kill switch.",
            font=("Segoe UI", 9),
            bg="#1e1e1e",
            fg="#aaaaaa",
        ).pack(pady=(2, 24))

        tk.Button(
            self.main_frame,
            text="LOCK INTERNET NOW",
            font=("Segoe UI", 12, "bold"),
            bg="#d32f2f",
            fg="white",
            activebackground="#b71c1c",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.handle_lock,
        ).pack(fill="x", ipady=12)

        tk.Button(
            self.main_frame,
            text="Change Master Password",
            font=("Segoe UI", 9, "underline"),
            bg="#1e1e1e",
            fg="#888888",
            activebackground="#1e1e1e",
            activeforeground="#cccccc",
            relief="flat",
            cursor="hand2",
            command=self.handle_reset_password_prompt,
        ).pack(pady=(14, 0))

    def build_locked_screen(self):
        tk.Label(
            self.main_frame,
            text="🔒",
            font=("Segoe UI Emoji", 54),
            bg="#1e1e1e",
            fg="#f44336",
        ).pack(pady=(5, 5))

        tk.Label(
            self.main_frame,
            text="INTERNET LOCKED",
            font=("Segoe UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#f44336",
        ).pack()

        tk.Label(
            self.main_frame,
            text="Windows remains usable. Survives power loss & reboot.\nEnter your master password to restore internet access.",
            font=("Segoe UI", 9),
            bg="#1e1e1e",
            fg="#cccccc",
            justify="center",
        ).pack(pady=(4, 16))

        self.unlock_entry = tk.Entry(
            self.main_frame,
            show="*",
            font=("Segoe UI", 12),
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="white",
            relief="flat",
        )
        self.unlock_entry.pack(fill="x", ipady=6, pady=(4, 16))
        self.unlock_entry.focus()
        self.unlock_entry.bind("<Return>", lambda e: self.handle_unlock())

        tk.Button(
            self.main_frame,
            text="UNLOCK INTERNET ACCESS",
            font=("Segoe UI", 11, "bold"),
            bg="#388e3c",
            fg="white",
            activebackground="#2e7d32",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.handle_unlock,
        ).pack(fill="x", ipady=10)

    def handle_save_master_password(self):
        pwd = self.setup_entry.get().strip()
        if not pwd:
            messagebox.showwarning("Password Required", "Please enter a master password.")
            return
        self.config["password_hash"] = hash_password(pwd)
        self.save_config()
        self.render_screen()

    def handle_lock(self):
        lock_internet()
        self.render_screen()

    def handle_unlock(self):
        pwd = self.unlock_entry.get().strip()
        saved_hash = self.config.get("password_hash", "")
        if hash_password(pwd) == saved_hash:
            unlock_internet()
            self.render_screen()
        else:
            messagebox.showerror("Access Denied", "Incorrect password. Internet remains locked.")
            self.unlock_entry.delete(0, tk.END)

    def handle_reset_password_prompt(self):
        del self.config["password_hash"]
        self.save_config()
        self.render_screen()


if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
    root = tk.Tk()
    app = NetPadlockApp(root)
    root.mainloop()
