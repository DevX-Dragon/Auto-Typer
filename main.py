import pyautogui
import random
import time
import keyboard
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox

# Global Performance Settings
pyautogui.PAUSE = 0
pyautogui.MINIMUM_SLEEP = 0

class DevXMiniPro:
    def __init__(self, root):
        self.root = root
        self.root.title("DevX Mini Pro")
        self.root.geometry("320x340") # Adjusted for footer space
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True) 
        
        self.running = False
        self.payload = ""
        self.start_key = "F8"
        self.stop_key = "F9"
        self.error_chance = tk.DoubleVar(value=0.05)
        
        self.setup_ui()
        self.safe_hook_hotkeys(self.start_key, self.stop_key)

    def setup_ui(self):
        style = ttk.Style()
        try: style.theme_use('vista')
        except: style.theme_use('clam')

        # --- TAB CONTROL ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.tab_main = ttk.Frame(self.notebook)
        self.tab_adv = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_main, text="  Main  ")
        self.notebook.add(self.tab_adv, text="  Advanced  ")

        # --- MAIN TAB ---
        main = tk.Frame(self.tab_main, padx=10, pady=5)
        main.pack(fill=tk.BOTH)

        tk.Button(main, text="SET PAYLOAD", command=self.open_payload_window, 
                  bg="#e1e1e1", relief=tk.GROOVE, font=("Segoe UI", 8, "bold")).pack(fill=tk.X, pady=5)

        self.char_count_lbl = tk.Label(main, text="Chars Loaded: 0", font=("Segoe UI", 7), fg="#666")
        self.char_count_lbl.pack()

        row1 = tk.Frame(main)
        row1.pack(fill=tk.X, pady=5)
        tk.Label(row1, text="Speed:", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="Fast")
        ttk.Combobox(row1, textvariable=self.speed_var, values=("Slow", "Medium", "Fast", "Very Fast"), 
                     state="readonly", width=12).pack(side=tk.RIGHT)

        self.auto_min = tk.BooleanVar(value=True)
        tk.Checkbutton(main, text="Auto-minimize on start", variable=self.auto_min, font=("Segoe UI", 8)).pack(anchor=tk.W)

        self.progress = ttk.Progressbar(main, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        self.status_lbl = tk.Label(main, text="Ready", fg="#007ACC", font=("Segoe UI", 8, "bold"))
        self.status_lbl.pack()

        btn_f = tk.Frame(main)
        btn_f.pack(fill=tk.X, pady=5)
        self.start_btn = tk.Button(btn_f, text="START", command=self.begin_thread, bg="#DFF0D8", width=10, relief=tk.GROOVE)
        self.start_btn.pack(side=tk.LEFT, expand=True, padx=2)
        self.stop_btn = tk.Button(btn_f, text="STOP", command=self.kill_process, bg="#F2DEDE", width=10, relief=tk.GROOVE)
        self.stop_btn.pack(side=tk.LEFT, expand=True, padx=2)

        # --- ADVANCED TAB ---
        adv = tk.Frame(self.tab_adv, padx=10, pady=10)
        adv.pack(fill=tk.BOTH)

        tk.Label(adv, text="Hotkey Configuration", font=("Segoe UI", 8, "bold")).pack(anchor=tk.W)
        h_frame = tk.Frame(adv, pady=5)
        h_frame.pack(fill=tk.X)
        
        tk.Label(h_frame, text="Start:", font=("Segoe UI", 8)).grid(row=0, column=0)
        self.sk_entry = ttk.Entry(h_frame, width=8)
        self.sk_entry.insert(0, self.start_key)
        self.sk_entry.grid(row=0, column=1, padx=5)

        tk.Label(h_frame, text="Stop:", font=("Segoe UI", 8)).grid(row=0, column=2)
        self.tk_entry = ttk.Entry(h_frame, width=8)
        self.tk_entry.insert(0, self.stop_key)
        self.tk_entry.grid(row=0, column=3, padx=5)

        tk.Label(adv, text="Mistake Probability (Humanize)", font=("Segoe UI", 8, "bold")).pack(anchor=tk.W, pady=(15,0))
        tk.Scale(adv, from_=0.0, to=0.3, resolution=0.01, variable=self.error_chance, 
                 orient=tk.HORIZONTAL, bg="#F5F5F5", font=("Segoe UI", 7), highlightthickness=0).pack(fill=tk.X)
        
        tk.Button(adv, text="Apply All Changes", command=self.refresh_settings, font=("Segoe UI", 8), bg="#e1e1e1").pack(pady=15, fill=tk.X)

        # --- BRANDED FOOTER ---
        footer = tk.Frame(self.root, bg="#F5F5F5", pady=3)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Label(footer, text="Made by ", font=("Segoe UI", 7), bg="#F5F5F5", fg="#666").pack(side=tk.LEFT, padx=(10, 0))
        
        link = tk.Label(footer, text="DevX-Dragon", font=("Segoe UI", 7, "underline"), 
                        bg="#F5F5F5", fg="#007ACC", cursor="hand2")
        link.pack(side=tk.LEFT)
        link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/DevX-Dragon")) # Update with your real URL

    def open_payload_window(self):
        win = tk.Toplevel(self.root)
        win.title("Payload Editor")
        win.geometry("350x300")
        win.attributes('-topmost', True)
        
        # Priority: Pack Button at the BOTTOM first so it stays visible
        done_btn = tk.Button(win, text="CONFIRM & DONE", command=win.destroy, bg="#e1e1e1", height=2, font=("Segoe UI", 8, "bold"))
        done_btn.pack(side=tk.BOTTOM, fill=tk.X)

        txt = tk.Text(win, font=("Consolas", 10), undo=True, padx=5, pady=5)
        txt.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        txt.insert("1.0", self.payload)
        txt.focus_set()

        def sync_text(event=None):
            self.payload = txt.get("1.0", tk.END).strip()
            self.char_count_lbl.config(text=f"Chars Loaded: {len(self.payload)}")
        
        txt.bind("<KeyRelease>", sync_text)

    def safe_hook_hotkeys(self, start, stop):
        try: keyboard.unhook_all_hotkeys()
        except: pass
        try:
            keyboard.add_hotkey(start, self.begin_thread)
            keyboard.add_hotkey(stop, self.kill_process)
            self.start_key, self.stop_key = start, stop
            return True
        except: return False

    def refresh_settings(self):
        s = self.sk_entry.get().strip()
        t = self.tk_entry.get().strip()
        if self.safe_hook_hotkeys(s, t):
            messagebox.showinfo("Success", "Settings and Hotkeys updated!")
            self.notebook.select(self.tab_main)

    def typing_logic(self):
        current_text = self.payload
        if not current_text:
            messagebox.showwarning("Empty", "Set text in 'SET PAYLOAD' first!")
            self.kill_process()
            return

        if self.auto_min.get(): self.root.iconify()
        
        mode = self.speed_var.get()
        prob = self.error_chance.get()
        total = len(current_text)
        
        for i, char in enumerate(current_text):
            if not self.running: break
            
            # Mistake logic
            if mode != "Very Fast" and prob > 0 and random.random() < prob:
                pyautogui.write(random.choice("abcdefghijklmnopqrstuvwxyz"))
                time.sleep(random.uniform(0.1, 0.2))
                pyautogui.press('backspace')
                time.sleep(0.05)

            pyautogui.write(char)
            self.progress['value'] = ((i + 1) / total) * 100
            
            if mode != "Very Fast":
                delay = {"Slow": 0.4, "Medium": 0.15, "Fast": 0.05}[mode]
                time.sleep(random.uniform(delay*0.8, delay*1.2))

        if self.auto_min.get(): self.root.deiconify()
        self.kill_process()

    def begin_thread(self):
        if not self.running:
            self.running = True
            self.status_lbl.config(text="ACTIVE", fg="orange")
            threading.Thread(target=self.typing_logic, daemon=True).start()

    def kill_process(self):
        self.running = False
        self.status_lbl.config(text="Ready", fg="#007ACC")
        self.progress['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = DevXMiniPro(root)
    root.mainloop()

