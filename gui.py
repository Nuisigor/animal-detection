import customtkinter as ctk
from tkinter import filedialog, Label, Frame, Canvas, Scrollbar, NW, messagebox
from PIL import Image, ImageTk
import os
import imageio
import time
from shutil import copyfile
from process import Processor

yolo_versions = ["YOLOv5-32", "YOLOv9-16", "YOLOv9-8", "YOLOv5-16", "YOLOv5-8", "YOLOv3-64", "YOLOv3-32", "YOLOv3-16", "YOLOv3-8"]

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.__processor = None
        self.title("Animal Finder")
        self.geometry("600x800")
        self.processing = False
        self.folder_path = ""
        self.destination_path = ""
        self.thumbnails = []
        self.file_checkboxes = []
        
        self.create_widgets()

    def create_widgets(self):
        # Frame para seleção de modelo
        self.model_frame = ctk.CTkFrame(self)
        self.model_frame.pack(pady=(20, 10), padx=20, fill="x")
        self.create_model_selection(self.model_frame)
        
        # Frame para seleção de pasta de origem
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.pack(pady=(10, 10), padx=20, fill="x")
        self.folder_label = ctk.CTkLabel(self.folder_frame, text="Pasta Selecionada")
        self.folder_label.pack(pady=5)
        self.select_folder_button = ctk.CTkButton(self.folder_frame, text="Selecionar Pasta", command=self.select_folder)
        self.select_folder_button.pack(pady=5)
        
        # Frame para seleção de pasta de destino
        self.destination_frame = ctk.CTkFrame(self)
        self.destination_frame.pack(pady=(10, 10), padx=20, fill="x")
        self.destination_label = ctk.CTkLabel(self.destination_frame, text="Pasta de Destino")
        self.destination_label.pack(pady=5)
        self.select_destination_button = ctk.CTkButton(self.destination_frame, text="Selecionar Pasta de Destino", command=self.select_destination)
        self.select_destination_button.pack(pady=5)
        
        # Frame para seleção de arquivos
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=(10, 10), padx=20, fill="both", expand=True)
        self.create_file_selection(self.file_frame)
        
        # Frame para barra de progresso
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.pack(pady=(10, 10), padx=20, fill="x")
        self.create_progress_bar(self.progress_frame)
        
        # Frame para botões
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=(10, 20), padx=20, fill="x")
        self.create_buttons(self.button_frame)

    def create_model_selection(self, frame):
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=0)
        frame.grid_columnconfigure(3, weight=1)

        self.model_label = ctk.CTkLabel(frame, text="Selecione o modelo")
        self.model_label.grid(row=0, column=1, pady=5, sticky="e", padx=(0, 10))

        self.model_options = yolo_versions
        self.model_var = ctk.StringVar(value=self.model_options[0])
        self.model_select = ctk.CTkOptionMenu(frame, variable=self.model_var, values=self.model_options)
        self.model_select.grid(row=0, column=2, pady=5, sticky="w")

    def create_file_selection(self, frame):
        self.select_all_var = ctk.BooleanVar()
        self.select_all_checkbox = ctk.CTkCheckBox(frame, text="Selecionar todos os arquivos", variable=self.select_all_var, command=self.toggle_select_all)
        self.select_all_checkbox.pack(anchor='w', pady=5)  # Alinhar à esquerda

        self.canvas = Canvas(frame, bd=0, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = Scrollbar(frame, command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner_frame = Frame(self.canvas, bg=self.cget('bg'))
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor=NW)

        self.inner_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # For Linux systems
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # For Linux systems

    def create_progress_bar(self, frame):
        self.progress_bar = ctk.CTkProgressBar(frame, width=300)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)  # Inicializar barra de progresso em 0

        self.status_label = ctk.CTkLabel(frame, text="Processando...")
        self.status_label.pack(pady=5)
        self.status_label.pack_forget()  # Ocultar a label inicialmente

    def create_buttons(self, frame):
        self.stop_button = ctk.CTkButton(frame, text="Parar", fg_color="red", hover_color="red", command=self.stop_process)
        self.stop_button.pack(side="left", padx=(50, 10))

        self.start_button = ctk.CTkButton(frame, text="Iniciar", command=self.start_process)
        self.start_button.pack(side="right", padx=(10, 50))

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.folder_label.configure(text=f"Pasta Selecionada: {self.folder_path}")
            self.display_files()

    def select_destination(self):
        self.destination_path = filedialog.askdirectory()
        if self.destination_path:
            self.destination_label.configure(text=f"Pasta de Destino: {self.destination_path}")

    def display_files(self):
        if not self.folder_path:
            return

        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        self.thumbnails.clear()
        self.file_checkboxes.clear()

        files = os.listdir(self.folder_path)
        for file in files:
            if file.lower().endswith(('.mp4', '.avi', '.mkv')):
                file_path = os.path.join(self.folder_path, file)
                thumbnail = self.create_thumbnail(file_path)
                self.thumbnails.append(thumbnail)

                file_frame = ctk.CTkFrame(self.inner_frame)
                file_frame.pack(pady=5, padx=10, fill="x")

                thumbnail_label = Label(file_frame, image=thumbnail, bg=self.inner_frame.cget('bg'))
                thumbnail_label.pack(side="left", padx=5)

                file_checkbox_var = ctk.BooleanVar()
                file_checkbox = ctk.CTkCheckBox(file_frame, text=file, variable=file_checkbox_var)
                file_checkbox.pack(side="left", padx=5)
                self.file_checkboxes.append(file_checkbox)
                file_checkbox.var = file_checkbox_var

                thumbnail_label.bind("<MouseWheel>", self._on_mousewheel)
                thumbnail_label.bind("<Button-4>", self._on_mousewheel)  # Para sistemas linux
                thumbnail_label.bind("<Button-5>", self._on_mousewheel)  # Para sistemas linux

    def create_thumbnail(self, file_path):
        video = imageio.get_reader(file_path)
        frame = video.get_next_data()
        frame_image = Image.fromarray(frame)
        frame_image.thumbnail((100, 100))
        return ImageTk.PhotoImage(frame_image)

    def toggle_select_all(self):
        select_all = self.select_all_var.get()
        for checkbox in self.file_checkboxes:
            checkbox.var.set(select_all)

    def start_process(self):
        if self.processing:
            return

        # Verifica se a pasta de entrada e saída foram selecionadas
        if not self.folder_path or not self.destination_path:
            messagebox.showerror("Erro", "Selecione uma pasta de entrada e uma pasta de saída antes de iniciar o processamento.")
            return
        self.__processor = Processor(self.model_var.get())
        self.processing = True
        self.status_label.pack()  # Mostrar a label de status

        selected_files = [checkbox.cget("text") for checkbox in self.file_checkboxes if checkbox.var.get()]
        print("Arquivos selecionados:", selected_files)

        total_files = len(selected_files)
        if total_files == 0:
            self.processing = False
            return

        for index, file in enumerate(selected_files):
            if not self.processing:  # Verifica se o processamento foi interrompido
                break

            has_animal = self.__processor.process_video(os.path.join(self.folder_path, file))
            if has_animal:
                copyfile(os.path.join(self.folder_path, file), os.path.join(self.destination_path, file))
            time.sleep(1)
            progress = (index + 1) / total_files
            self.progress_bar.set(progress)
            self.status_label.configure(text=f"Processando {file} ({index + 1}/{total_files})")
            self.update_idletasks()  # Atualiza a interface gráfica

        self.processing = False
        self.status_label.pack_forget()

    def stop_process(self):
        self.processing = False
        self.progress_bar.set(0)  # Reseta barra de progresso para 0
        self.status_label.pack_forget()  # Oculta a label de status
        self.status_label.configure(text="Processando...")

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
