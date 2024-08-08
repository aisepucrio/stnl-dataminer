import tkinter as tk
import platform
import os
import psutil
from tkinter import PhotoImage 
from PIL import Image, ImageTk, ImageDraw
from tkinter import font as tkfont
from view.jira_view import JiraApp
from view.gh_view import GitHubApp
from view.settings_view import SettingsApp
from dotenv import load_dotenv, dotenv_values, set_key

# Classe principal da aplicação de mineração de dados
class DataMinerApp():
    def __init__(self, root):
        self.root = root
        self.root.title("Data Miner")
        self.root.configure(bg='#1e1e1e')

        load_dotenv()

        if platform.system() == "Linux":
            self.root.iconphoto(True, PhotoImage(file='view/icons/datamining.png'))
        else:
            self.root.iconbitmap('view/icons/datamining.ico')

        self.window_width = 800
        self.window_height = 450
        self.center_window()

        self.bree_serif = tkfont.Font(family="Bree Serif", size=30, weight="bold")
        self.bree_serif_small = tkfont.Font(family="Bree Serif", size=15, weight="bold")

        self.image_refs = {}

        self.env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env')
        self.env_values  = dotenv_values(self.env_file)
        
        self.set_initial_env_variables()

        self.load_env()

        self.create_widgets()

        self.check_for_exit_key()

    # Função para garantir que uma chave está presente no arquivo .env
    def ensure_env_key(self, key, default_value=''):
        if key not in dotenv_values(self.env_file):
            set_key(self.env_file, key, default_value)

    def number_of_threads(self):
        number_of_threads = psutil.cpu_count(logical=True)
        return number_of_threads

        # Função para carregar as variáveis de ambiente
    def load_env(self):
        default_env_content = f"""TOKENS=
    USERNAMES=
    EMAIL=
    API_TOKEN=
    SAVE_PATH=
    MAX_WORKERS={self.number_of_threads()//2}
    PG_HOST=opus.servehttp.com
    PG_DATABASE=aise-stone
    PG_USER=aise-stone
    PG_PASSWORD=#St@n3L@b2@24!
    PG_PORT=54321
    USE_DATABASE='0'
    """
        if not os.path.exists(self.env_file):
            with open(self.env_file, 'w') as f:
                f.write(default_env_content)

        load_dotenv(self.env_file)

        self.env_values = dotenv_values(self.env_file)
        self.tokens = self.env_values.get('TOKENS', '').split(',')
        self.usernames = self.env_values.get('USERNAMES', '').split(',')
        self.emails = self.env_values.get('EMAIL', '').split(',')
        self.api_tokens = self.env_values.get('API_TOKEN', '').split(',')
        self.save_path = self.env_values.get('SAVE_PATH', os.path.join(os.path.expanduser("~"), "Downloads"))
        self.max_workers_str = self.env_values.get('MAX_WORKERS', f'{self.number_of_threads()//2}')
        self.max_workers = int(self.max_workers_str) if self.max_workers_str else 1
        self.use_database = self.env_values.get('USE_DATABASE', '0') == '1'

        # Garante que todas as chaves necessárias estão presentes no arquivo .env
        self.ensure_env_key('TOKENS')
        self.ensure_env_key('USERNAMES')
        self.ensure_env_key('EMAIL')
        self.ensure_env_key('API_TOKEN')
        self.ensure_env_key('SAVE_PATH')
        self.ensure_env_key('MAX_WORKERS', f'{self.number_of_threads()//2}')
        self.ensure_env_key('PG_HOST', 'opus.servehttp.com')
        self.ensure_env_key('PG_DATABASE', 'aise-stone')
        self.ensure_env_key('PG_USER', 'aise-stone')
        self.ensure_env_key('PG_PASSWORD', '#St@n3L@b2@24!')
        self.ensure_env_key('PG_PORT', '54321')
        self.ensure_env_key('USE_DATABASE', '0')

    # Definindo valores iniciais para as variáveis de ambiente
    def set_initial_env_variables(self):
        if 'USE_DATABASE' not in self.env_values:
            set_key(self.env_file, 'USE_DATABASE', '0')
        else:
            if self.env_values['USE_DATABASE'] == '1':
                set_key(self.env_file, 'USE_DATABASE', '0')

    # Função para verificar a tecla 'q'
    def check_for_exit_key(self):
        self.root.bind_all('<KeyPress-q>', self.on_exit_key)
        self.root.after(100, self.check_for_exit_key)

    def on_exit_key(self, event):
        print("Saindo...")
        self.exit()

    # Função para centralizar a janela na tela
    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f'{self.window_width}x{self.window_height}+{x}+{y}')

    # Função para criar os widgets
    def create_widgets(self):
        title_label = tk.Label(self.root, text="Select a Platform", font=self.bree_serif, fg="#606060", bg='#1e1e1e')
        title_label.pack(pady=30)

        frame = tk.Frame(self.root, bg='#1e1e1e')
        frame.pack(pady=20)

        self.create_platform_button(frame, "view/icons/jira_icon_black.png", "JIRA", 0, 0, self.on_jira_click)
        self.create_platform_button(frame, "view/icons/gh_icon_black.png", "GitHub", 0, 1, self.on_github_click)

        self.create_settings_button()
        self.create_close_button()

    # Função para criar um botão de plataforma
    def create_platform_button(self, frame, image_path, label_text, row, column, click_command):
        try:
            image = Image.open(image_path)
            image = image.resize((180, 180), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading {label_text} image: {e}")
            photo = None

        circle_image = self.create_circle_image(200, (60, 60, 60), (0, 0, 0, 0))
        circle_photo = ImageTk.PhotoImage(circle_image)

        canvas = tk.Canvas(frame, width=250, height=250, bg='#1e1e1e', highlightthickness=0)
        canvas.grid(row=row, column=column, padx=60)
        canvas.create_image(125, 125, image=circle_photo)
        if photo:
            canvas.create_image(125, 125, image=photo)
        canvas.bind("<Button-1>", lambda e: click_command())
        canvas.bind("<Enter>", lambda e: self.zoom_in(e, canvas, image, label_text))
        canvas.bind("<Leave>", lambda e: self.zoom_out(e, canvas, photo))

        self.image_refs[f"{label_text}_circle"] = circle_photo
        self.image_refs[label_text] = photo

        canvas.circle_photo = circle_photo

    # Função para criar uma imagem circular
    def create_circle_image(self, diameter, color, bg_color):
        image = Image.new('RGBA', (diameter, diameter), bg_color)
        draw = ImageDraw.Draw(image)
        for i in range(diameter):
            for j in range(diameter):
                distance_to_center = ((i - diameter/2)**2 + (j - diameter/2)**2)**0.5
                if distance_to_center < diameter/2:
                    alpha = 255
                    if distance_to_center > diameter/2 - 1:
                        alpha = int(255 * (1 - (distance_to_center - (diameter/2 - 1))))
                    image.putpixel((i, j), color + (alpha,))
        return image

    # Função para criar um botão de configurações
    def create_settings_button(self):
        try:
            settings_image = Image.open("view/icons/settings_icon.png")
            settings_image = settings_image.resize((30, 30), Image.LANCZOS)
            settings_photo = ImageTk.PhotoImage(settings_image)
            settings_image_zoomed = settings_image.resize((36, 36), Image.LANCZOS)
            settings_photo_zoomed = ImageTk.PhotoImage(settings_image_zoomed)
        except Exception as e:
            print(f"Error loading settings image: {e}")
            settings_photo = None

        if settings_photo:
            settings_button = tk.Button(self.root, image=settings_photo, command=self.on_settings_click, bg='#1e1e1e', bd=0, highlightthickness=0, activebackground='#1e1e1e')
            settings_button.place(relx=0.97, rely=0.95, anchor='center')
            settings_button.bind("<Enter>", lambda e: settings_button.config(image=settings_photo_zoomed))
            settings_button.bind("<Leave>", lambda e: settings_button.config(image=settings_photo))

            self.image_refs['settings'] = settings_photo
            self.image_refs['settings_zoomed'] = settings_photo_zoomed

    # Função para sair da aplicação
    def exit(self):
        exit(1)

    # Função para criar um botão de fechar
    def create_close_button(self):
        try:
            close_image = Image.open("view/icons/close.png")
            close_image = close_image.resize((20, 20), Image.LANCZOS)
            close_photo = ImageTk.PhotoImage(close_image)
            close_image_zoomed = close_image.resize((24, 24), Image.LANCZOS)
            close_photo_zoomed = ImageTk.PhotoImage(close_image_zoomed)
        except Exception as e:
            print(f"Error loading close image: {e}")
            close_photo = None

        if close_photo:
            close_button = tk.Button(self.root, image=close_photo, command=self.exit, bg='#1e1e1e', bd=0, highlightthickness=0, activebackground='#1e1e1e')
            close_button.place(relx=0.98, rely=0.02, anchor='ne')
            close_button.bind("<Enter>", lambda e: close_button.config(image=close_photo_zoomed))
            close_button.bind("<Leave>", lambda e: close_button.config(image=close_photo))
            self.image_refs['close'] = close_photo
            self.image_refs['close_zoomed'] = close_photo_zoomed

    # Função para lidar com o clique no botão do Jira
    def on_jira_click(self): 
        self.root.withdraw()  
        jira_app = JiraApp(self.root)
        jira_app.run()

    # Função para lidar com o clique no botão do GitHub
    def on_github_click(self): 
        self.root.withdraw()  
        gh_app = GitHubApp(self.root)
        gh_app.run()  

    # Função para lidar com o clique no botão de configurações
    def on_settings_click(self):
        self.root.withdraw()
        settings_app = SettingsApp(self.root)
        settings_app.mainloop()

    # Função para aumentar o zoom de uma imagem ao passar o mouse
    def zoom_in(self, event, widget, image, label_text=None):
        if isinstance(widget, tk.Canvas):
            zoomed_image = image.resize((int(image.width * 1.1), int(image.height * 1.1)), Image.LANCZOS)
            zoomed_photo = ImageTk.PhotoImage(zoomed_image)
            widget.delete("all")
            widget.create_image(125, 125, image=widget.circle_photo)
            widget.create_image(125, 125, image=zoomed_photo)
            widget.image = zoomed_photo

            if label_text:
                label = tk.Label(self.root, text=label_text, font=self.bree_serif_small, fg="#606060", bg='#1e1e1e')
                widget_x = widget.winfo_rootx() - self.root.winfo_rootx()
                widget_y = widget.winfo_rooty() - self.root.winfo_rooty()
                label_width = label.winfo_reqwidth()
                label.place(x=widget_x + (widget.winfo_width() - label_width) // 2, y=widget_y + 250)
                widget.label = label
        elif isinstance(widget, tk.Button):
            zoomed_image = image.resize((int(image.width * 1.2), int(image.height * 1.2)), Image.LANCZOS)
            zoomed_photo = ImageTk.PhotoImage(zoomed_image)
            widget.config(image=zoomed_photo)
            widget.image = zoomed_photo

    # Função para diminuir o zoom de uma imagem ao retirar o mouse
    def zoom_out(self, event, widget, image):
        if isinstance(widget, tk.Canvas):
            widget.delete("all")
            widget.create_image(125, 125, image=widget.circle_photo)
            widget.create_image(125, 125, image=image)
            if hasattr(widget, 'label'):
                widget.label.destroy()
            widget.image = image
        elif isinstance(widget, tk.Button):
            widget.config(image=image)
            widget.image = image