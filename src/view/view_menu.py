import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageDraw
from view.view_jira import JiraDataMinerApp
from view.view_gh import GitHubRepoInfoApp 

class DataMinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Miner")
        self.root.configure(bg='#1e1e1e')
        self.root.iconbitmap('view/icons/datamining.ico')

        self.window_width = 800
        self.window_height = 450
        self.center_window()

        self.bree_serif = tkfont.Font(family="Bree Serif", size=30, weight="bold")
        self.bree_serif_small = tkfont.Font(family="Bree Serif", size=15, weight="bold")

        self.image_refs = {}

        self.create_widgets()

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f'{self.window_width}x{self.window_height}+{x}+{y}')

    def create_widgets(self):
        title_label = tk.Label(self.root, text="Selecione a Plataforma", font=self.bree_serif, fg="#606060", bg='#1e1e1e')
        title_label.pack(pady=30)

        frame = tk.Frame(self.root, bg='#1e1e1e')
        frame.pack(pady=20)

        self.create_platform_button(frame, "view/icons/jira_icon_black.png", "JIRA", 0, 0, self.on_jira_click)
        self.create_platform_button(frame, "view/icons/gh_icon_black.png", "GitHub", 0, 1, self.on_github_click)

        self.create_settings_button()
        self.create_close_button()

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
            close_button = tk.Button(self.root, image=close_photo, command=self.root.quit, bg='#1e1e1e', bd=0, highlightthickness=0, activebackground='#1e1e1e')
            close_button.place(relx=0.98, rely=0.02, anchor='ne')
            close_button.bind("<Enter>", lambda e: close_button.config(image=close_photo_zoomed))
            close_button.bind("<Leave>", lambda e: close_button.config(image=close_photo))
            self.image_refs['close'] = close_photo
            self.image_refs['close_zoomed'] = close_photo_zoomed

    def on_jira_click(self): 
        self.root.withdraw()  
        jira_app = JiraDataMinerApp(self.root)
        jira_app.run()

    def on_github_click(self): 
        self.root.withdraw()  
        gh_app = GitHubRepoInfoApp(self.root)
        gh_app.run()  

    def on_settings_click(self):
        from view.view_settings import SettingsApp
        settings_app = SettingsApp()
        settings_app.mainloop()

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

if __name__ == "__main__":
    root = tk.Tk()
    app = DataMinerApp(root)
    root.mainloop()
