import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageDraw

def on_jira_click():
    messagebox.showinfo("Plataforma Selecionada", "Você selecionou JIRA")

def on_github_click():
    messagebox.showinfo("Plataforma Selecionada", "Você selecionou GitHub")

def on_settings_click():
    messagebox.showinfo("Configurações", "Abrir configurações")

def create_circle_image(diameter, color, bg_color):
    image = Image.new('RGBA', (diameter, diameter), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Drawing a slightly smooth circle
    for i in range(diameter):
        for j in range(diameter):
            distance_to_center = ((i - diameter/2)**2 + (j - diameter/2)**2)**0.5
            if distance_to_center < diameter/2:
                alpha = 255
                if distance_to_center > diameter/2 - 1:
                    alpha = int(255 * (1 - (distance_to_center - (diameter/2 - 1))))
                image.putpixel((i, j), color + (alpha,))
    return image

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')

def zoom_in(event, widget, image, label_text=None):
    if isinstance(widget, tk.Canvas):
        zoomed_image = image.resize((int(image.width * 1.1), int(image.height * 1.1)), Image.LANCZOS)
        zoomed_photo = ImageTk.PhotoImage(zoomed_image)
        widget.delete("all")
        if label_text:
            widget.create_image(125, 125, image=circle_photo)
        widget.create_image(125, 125, image=zoomed_photo)
        widget.image = zoomed_photo

        if label_text:
            label = tk.Label(root, text=label_text, font=bree_serif_small, fg="#606060", bg='#1e1e1e')
            widget_x = widget.winfo_rootx() - root.winfo_rootx()
            widget_y = widget.winfo_rooty() - root.winfo_rooty()
            label_width = label.winfo_reqwidth()
            label.place(x=widget_x + (widget.winfo_width() - label_width) // 2, y=widget_y + 250)
            widget.label = label
    elif isinstance(widget, tk.Button):
        zoomed_image = image.resize((int(image.width * 1.2), int(image.height * 1.2)), Image.LANCZOS)
        zoomed_photo = ImageTk.PhotoImage(zoomed_image)
        widget.config(image=zoomed_photo)
        widget.image = zoomed_photo

def zoom_out(event, widget, image):
    if isinstance(widget, tk.Canvas):
        widget.delete("all")
        if hasattr(widget, 'label'):
            widget.create_image(125, 125, image=circle_photo)
            widget.label.destroy()
        widget.create_image(125, 125, image=image)
        widget.image = image
    elif isinstance(widget, tk.Button):
        widget.config(image=image)
        widget.image = image

# Configuração da janela principal
root = tk.Tk()
root.title("Data Miner")
root.configure(bg='#1e1e1e')
root.iconbitmap('view/icons/datamining.ico')  # Certifique-se de que o arquivo 'app_icon.ico' esteja no mesmo diretório do script

# Centralizar a janela
window_width = 800
window_height = 450
center_window(root, window_width, window_height)

# Carregar a fonte Bree Serif (certifique-se de que o arquivo .ttf está no mesmo diretório do script)
font_path = r"src/view/fonts/BreeSerif-Regular.ttf"
bree_serif = tkfont.Font(family="Bree Serif", size=30, weight="bold")
bree_serif_small = tkfont.Font(family="Bree Serif", size=15, weight="bold")  # Fonte menor para os labels

# Título
title_label = tk.Label(root, text="Selecione a Plataforma", font=bree_serif, fg="#606060", bg='#1e1e1e')
title_label.pack(pady=30)

# Frame para os botões
frame = tk.Frame(root, bg='#1e1e1e')
frame.pack(pady=20)

# Carregar e redimensionar as imagens (substitua os caminhos pelos corretos)
jira_image_path = "view/icons/jira_icon_black.png"
github_image_path = "view/icons/gh_icon_black.png"
settings_image_path = "view/icons/settings_icon.png"

# Load and resize images with error handling
try:
    jira_image = Image.open(jira_image_path)
    jira_image = jira_image.resize((180, 180), Image.LANCZOS)
    jira_photo = ImageTk.PhotoImage(jira_image)
except Exception as e:
    print(f"Error loading Jira image: {e}")
    jira_photo = None

try:
    github_image = Image.open(github_image_path)
    github_image = github_image.resize((200, 200), Image.LANCZOS)
    github_photo = ImageTk.PhotoImage(github_image)
except Exception as e:
    print(f"Error loading GitHub image: {e}")
    github_photo = None

# Criar imagens de círculos suavizados
circle_image = create_circle_image(240, (60, 60, 60), (0, 0, 0, 0))
circle_photo = ImageTk.PhotoImage(circle_image)

# Canvas para desenhar os círculos e adicionar imagens
canvas_jira = tk.Canvas(frame, width=250, height=250, bg='#1e1e1e', highlightthickness=0)
canvas_jira.grid(row=0, column=0, padx=60)
canvas_jira.create_image(125, 125, image=circle_photo)
if jira_photo:
    canvas_jira.create_image(125, 125, image=jira_photo)
canvas_jira.bind("<Button-1>", lambda e: on_jira_click())
canvas_jira.bind("<Enter>", lambda e: zoom_in(e, canvas_jira, jira_image, "JIRA"))
canvas_jira.bind("<Leave>", lambda e: zoom_out(e, canvas_jira, jira_photo))

canvas_github = tk.Canvas(frame, width=250, height=250, bg='#1e1e1e', highlightthickness=0)
canvas_github.grid(row=0, column=1, padx=60)
canvas_github.create_image(125, 125, image=circle_photo)
if github_photo:
    canvas_github.create_image(125, 125, image=github_photo)
canvas_github.bind("<Button-1>", lambda e: on_github_click())
canvas_github.bind("<Enter>", lambda e: zoom_in(e, canvas_github, github_image, "GitHub"))
canvas_github.bind("<Leave>", lambda e: zoom_out(e, canvas_github, github_photo))

# Configuração para o ícone de configurações
try:
    settings_image = Image.open(settings_image_path)
    settings_image = settings_image.resize((30, 30), Image.LANCZOS)
    settings_photo = ImageTk.PhotoImage(settings_image)
    settings_image_zoomed = settings_image.resize((36, 36), Image.LANCZOS)
    settings_photo_zoomed = ImageTk.PhotoImage(settings_image_zoomed)
except Exception as e:
    print(f"Error loading settings image: {e}")
    settings_photo = None

if settings_photo:
    settings_button = tk.Button(root, image=settings_photo, command=on_settings_click, bg='#1e1e1e', bd=0, highlightthickness=0, activebackground='#1e1e1e')
    settings_button.place(relx=0.97, rely=0.95, anchor='center')
    settings_button.bind("<Enter>", lambda e: settings_button.config(image=settings_photo_zoomed))
    settings_button.bind("<Leave>", lambda e: settings_button.config(image=settings_photo))

root.mainloop()
