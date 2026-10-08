import threading
import time
import subprocess
import sys

# --- BOOTSTRAP DE DEPENDÊNCIAS AUTOMÁTICO ---
def install_dependencies():
    packages = ["customtkinter", "pynput"]
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Instalando {package} automaticamente...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_dependencies()

import customtkinter as ctk
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener, Key, KeyCode

# Configuração de Aparência Global
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class SabKingAutoClicker:
    def __init__(self):
        self.mouse = MouseController()
        
        self.running = False
        self.mode = "interval"  # "interval" ou "cps"
        self.interval = 0.1
        self.button_type = Button.left
        self.click_type = "single"
        
        # Hotkey padrão: Tab
        self.hotkey = Key.tab
        self.binding_mode = False
        
        # Janela Principal
        self.root = ctk.CTk()
        self.root.title("S.a.B King Best Auto Clicker")
        self.root.geometry("420x540")
        self.root.resizable(False, False)
        
        # Paleta de Cores Exclusiva: Preto Absoluto & Roxo Neon (High-End Gaming)
        self.bg_color = "#050308"        # Preto Profundo Espacial
        self.card_color = "#0D0814"      # Roxo Escuro Texturizado
        self.border_color = "#25143D"    # Borda Roxo Magnético
        self.neon_purple = "#B026FF"     # Roxo Neon Vibrante
        self.purple_glow = "#8A2BE2"     # Roxo Elétrico
        self.danger_red = "#FF2A6D"      # Vermelho Neon
        self.success_green = "#05FFA1"   # Verde Neon
        
        self.root.configure(fg_color=self.bg_color)
        
        self.setup_ui()
        
        # Threads de Background
        self.click_thread = threading.Thread(target=self._click_worker, daemon=True)
        self.click_thread.start()
        
        self.listener = Listener(on_press=self._on_press)
        self.listener.start()

    def setup_ui(self):
        # --- HEADER ESTILIZADO ---
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(pady=(18, 10))
        
        title = ctk.CTkLabel(
            header_frame, 
            text="S.a.B KING BEST", 
            font=("Segoe UI", 22, "bold"), 
            text_color=self.neon_purple
        )
        title.pack()
        
        sub = ctk.CTkLabel(
            header_frame, 
            text="ULTIMATE AUTO CLICKER", 
            font=("Segoe UI", 9, "bold"), 
            text_color="#6B5B95"
        )
        sub.pack()

        # --- CONTAINER PRINCIPAL ---
        card = ctk.CTkFrame(
            self.root, 
            fg_color=self.card_color, 
            corner_radius=18, 
            border_width=1, 
            border_color=self.border_color
        )
        card.pack(fill="both", expand=True, padx=16, pady=4)

        # 1. SELETOR DE MODO (Click/s vs CPS)
        mode_frame = ctk.CTkFrame(card, fg_color="transparent")
        mode_frame.pack(fill="x", pady=14, padx=16)

        self.mode_var = ctk.StringVar(value="interval")
        
        self.rb_interval = ctk.CTkRadioButton(
            mode_frame, text="Click/s (Intervalo)", variable=self.mode_var, value="interval",
            command=self.update_mode_ui, font=("Segoe UI", 11, "bold"),
            fg_color=self.neon_purple, border_color=self.border_color, hover_color=self.purple_glow
        )
        self.rb_interval.pack(side="left", padx=5)

        self.rb_cps = ctk.CTkRadioButton(
            mode_frame, text="CPS (Cliques/s)", variable=self.mode_var, value="cps",
            command=self.update_mode_ui, font=("Segoe UI", 11, "bold"),
            fg_color=self.neon_purple, border_color=self.border_color, hover_color=self.purple_glow
        )
        self.rb_cps.pack(side="right", padx=5)

        # PAINEL DE CONFIGURAÇÃO DE VELOCIDADE DINÂMICO
        self.speed_panel = ctk.CTkFrame(card, fg_color="#08040F", corner_radius=12, border_width=1, border_color=self.border_color)
        self.speed_panel.pack(fill="x", padx=16, pady=4)

        # Sub-container 1: Click/s (Segundos / Milissegundos)
        self.frame_interval = ctk.CTkFrame(self.speed_panel, fg_color="transparent")
        self.s_val = self.create_input_box(self.frame_interval, "SEGUNDOS", 0, 0, "0")
        self.ms_val = self.create_input_box(self.frame_interval, "MILISSEGUNDOS", 0, 1, "50")
        self.frame_interval.pack(fill="x", padx=12, pady=12)

        # Sub-container 2: CPS + Botão CPS Máximo Embutido
        self.frame_cps = ctk.CTkFrame(self.speed_panel, fg_color="transparent")
        
        lbl_cps_desc = ctk.CTkLabel(self.frame_cps, text="VELOCIDADE CPS:", font=("Segoe UI", 9, "bold"), text_color="#6B5B95")
        lbl_cps_desc.pack(anchor="w", padx=2, pady=(0, 2))
        
        cps_input_row = ctk.CTkFrame(self.frame_cps, fg_color="transparent")
        cps_input_row.pack(fill="x", padx=0)
        
        self.cps_entry = ctk.CTkEntry(
            cps_input_row, width=130, height=36, justify="center", fg_color=self.card_color,
            border_color=self.border_color, text_color=self.neon_purple, font=("Segoe UI", 13, "bold"), corner_radius=8
        )
        self.cps_entry.insert(0, "20")
        self.cps_entry.pack(side="left", padx=(0, 8), fill="x", expand=True)

        self.btn_max_cps = ctk.CTkButton(
            cps_input_row, text="⚡ CPS MÁXIMO", width=115, height=36,
            fg_color="#1A0D2E", hover_color="#2A134D", text_color=self.neon_purple,
            font=("Segoe UI", 10, "bold"), corner_radius=8, command=self.set_max_cps
        )
        self.btn_max_cps.pack(side="right")
        
        # Inicialmente oculto
        self.frame_cps.pack_forget()

        # Divisor sutil
        divider = ctk.CTkFrame(card, height=1, fg_color=self.border_color)
        divider.pack(fill="x", padx=16, pady=12)

        # 2. CONFIGURAÇÕES DO MOUSE
        mouse_frame = ctk.CTkFrame(card, fg_color="transparent")
        mouse_frame.pack(fill="x", pady=4, padx=16)

        self.combo_btn = ctk.CTkComboBox(
            mouse_frame, values=["Esquerdo", "Direito", "Meio"], width=135, height=36,
            fg_color=self.card_color, border_color=self.border_color, button_color=self.border_color,
            button_hover_color=self.purple_glow, dropdown_fg_color=self.card_color, font=("Segoe UI", 11, "bold")
        )
        self.combo_btn.set("Esquerdo")
        self.combo_btn.pack(side="left", padx=4, expand=True)

        self.combo_type = ctk.CTkComboBox(
            mouse_frame, values=["Single", "Double"], width=135, height=36,
            fg_color=self.card_color, border_color=self.border_color, button_color=self.border_color,
            button_hover_color=self.purple_glow, dropdown_fg_color=self.card_color, font=("Segoe UI", 11, "bold")
        )
        self.combo_type.set("Single")
        self.combo_type.pack(side="left", padx=4, expand=True)

        # 3. BOTÃO DE HOTKEY
        self.btn_hotkey = ctk.CTkButton(
            card, text="⚙ HOTKEY: TAB (MUDAR)", font=("Segoe UI", 11, "bold"),
            fg_color=self.card_color, hover_color="#1A0D2E", border_width=1,
            border_color=self.neon_purple, text_color=self.neon_purple, height=42,
            corner_radius=10, command=self.start_binding
        )
        self.btn_hotkey.pack(fill="x", padx=16, pady=14)

        # --- FOOTER (START / STOP) ---
        footer_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        footer_frame.pack(fill="x", pady=10, padx=16)

        self.btn_start = ctk.CTkButton(
            footer_frame, text="▶ START", height=46, fg_color=self.success_green, 
            hover_color="#03D98A", text_color="#050308", font=("Segoe UI", 13, "bold"), 
            corner_radius=10, command=self.start_clicking
        )
        self.btn_start.pack(side="left", expand=True, padx=5, fill="x")

        self.btn_stop = ctk.CTkButton(
            footer_frame, text="⏹ STOP", height=46, fg_color=self.danger_red, 
            hover_color="#D91E52", text_color="#FFFFFF", font=("Segoe UI", 13, "bold"), 
            corner_radius=10, command=self.stop_clicking
        )
        self.btn_stop.pack(side="left", expand=True, padx=5, fill="x")

        # --- RODAPÉ OFICIAL ---
        footer_info = ctk.CTkFrame(self.root, fg_color="transparent")
        footer_info.pack(fill="x", pady=(0, 10))
        
        self.status_bar = ctk.CTkLabel(
            footer_info, text="● PRONTO PARA ATIVAR", font=("Segoe UI", 9, "bold"), text_color="#6B5B95"
        )
        self.status_bar.pack(pady=(0, 2))
        
        credits_lbl = ctk.CTkLabel(
            footer_info, text="Feito por: NexDigital IA", font=("Segoe UI", 8, "bold"), text_color="#3D3055"
        )
        credits_lbl.pack()

    def create_input_box(self, master, label, row, col, default="0"):
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.grid(row=row, column=col, padx=4, sticky="nsew")
        master.grid_columnconfigure(col, weight=1)
        
        lbl = ctk.CTkLabel(f, text=label, font=("Segoe UI", 8, "bold"), text_color="#6B5B95")
        lbl.pack(pady=(0, 2))
        
        e = ctk.CTkEntry(
            f, width=130, height=34, justify="center", fg_color=self.card_color, 
            border_color=self.border_color, text_color="#FFFFFF", font=("Segoe UI", 12, "bold"), corner_radius=8
        )
        e.insert(0, default)
        e.pack()
        return e

    def update_mode_ui(self):
        self.mode = self.mode_var.get()
        if self.mode == "interval":
            self.frame_cps.pack_forget()
            self.frame_interval.pack(fill="x", padx=12, pady=12)
        else:
            self.frame_interval.pack_forget()
            self.frame_cps.pack(fill="x", padx=12, pady=12)

    def set_max_cps(self):
        self.cps_entry.delete(0, 'end')
        self.cps_entry.insert(0, "MAX")
        self.btn_max_cps.configure(fg_color=self.neon_purple, text_color=self.bg_color)
        self.root.after(800, lambda: self.btn_max_cps.configure(fg_color="#1A0D2E", text_color=self.neon_purple))

    # --- GERENCIAMENTO DE HOTKEY ---
    def start_binding(self):
        self.binding_mode = True
        self.btn_hotkey.configure(text="⌨ APERTE QUALQUER TECLA...", fg_color=self.neon_purple, text_color=self.bg_color)

    def _on_press(self, key):
        if self.binding_mode:
            self.hotkey = key
            self.binding_mode = False
            name = str(key).replace("Key.", "").upper()
            if hasattr(key, 'char') and key.char:
                name = key.char.upper()
            self.root.after(0, lambda: self.btn_hotkey.configure(
                text=f"⚙ HOTKEY: {name} (MUDAR)", fg_color=self.card_color, text_color=self.neon_purple
            ))
            return

        if key == self.hotkey:
            if self.running:
                self.root.after(0, self.stop_clicking)
            else:
                self.root.after(0, self.start_clicking)

    # --- LÓGICA DE CLIQUE ESTÁVEL ---
    def update_values(self):
        try:
            if self.mode == "interval":
                s = float(self.s_val.get() or 0)
                ms = float(self.ms_val.get() or 0) / 1000
                self.interval = s + ms
                if self.interval <= 0: 
                    self.interval = 0.001
            else:
                cps_text = self.cps_entry.get().strip().upper()
                if cps_text == "MAX":
                    self.interval = 0.0  # Máximo absoluto real
                else:
                    cps = float(cps_text or 20)
                    if cps <= 0: 
                        cps = 1
                    self.interval = 1.0 / cps
        except:
            self.interval = 0.1

        b = self.combo_btn.get()
        if b == "Direito": 
            self.button_type = Button.right
        elif b == "Meio": 
            self.button_type = Button.middle
        else: 
            self.button_type = Button.left

        self.click_type = self.combo_type.get().lower()

    def _click_worker(self):
        while True:
            if self.running:
                # Proteção anti-clique na janela do app
                mouse_x, mouse_y = self.mouse.position
                win_x = self.root.winfo_x()
                win_y = self.root.winfo_y()
                win_w = self.root.winfo_width()
                win_h = self.root.winfo_height()
                
                if win_x <= mouse_x <= win_x + win_w and win_y <= mouse_y <= win_y + win_h:
                    time.sleep(0.02)
                    continue

                clicks = 2 if self.click_type == "double" else 1
                self.mouse.click(self.button_type, clicks)
                
                if self.interval > 0:
                    time.sleep(self.interval)
            else:
                time.sleep(0.02)

    def start_clicking(self):
        if self.running:
            return
        self.update_values()
        self.running = True
        self.btn_start.configure(text="▶ RODANDO...", fg_color=self.neon_purple, text_color=self.bg_color)
        self.status_bar.configure(text="● CLICANDO ATIVAMENTE", text_color=self.success_green)

    def stop_clicking(self):
        self.running = False
        self.btn_start.configure(text="▶ START", fg_color=self.success_green, text_color=self.bg_color)
        self.status_bar.configure(text="● SISTEMA PARADO", text_color="#6B5B95")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SabKingAutoClicker()
    app.run()
