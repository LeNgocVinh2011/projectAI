import tkinter
import customtkinter
from tkinter import filedialog
from tkinter import messagebox
import mimetypes
import os
from PIL import Image, ImageTk

from person_detec import predict_folder

PATH = os.path.dirname(os.path.realpath(__file__))

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    WIDTH = 780
    HEIGHT = 520

    def __init__(self):
        super().__init__()

        self.title("Video Detection Application")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        # self.overrideredirect(True);
        self.resizable(0, 0)
        self.iconbitmap('images/video-marketing.ico')
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        self.frame_left.grid_rowconfigure(0, minsize=10)
        self.frame_left.grid_rowconfigure(5, weight=1)
        self.frame_left.grid_rowconfigure(8, minsize=20)
        self.frame_left.grid_rowconfigure(11, minsize=10)

        self.frame_info = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_info.grid(row=2, column=0, columnspan=3, rowspan=8, pady=20, padx=20, sticky="nsew")

        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
                                                   text="Display image",
                                                   height=100,
                                                   fg_color=("white", "gray38"),
                                                   justify=tkinter.LEFT)

        self.label_info_1.grid(column=0, row=0, sticky="nwe", padx=15, pady=15)

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Video Detection",
                                              text_font=("Roboto Medium", -16))
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        img_size = 20

        add_path = ImageTk.PhotoImage(Image.open(PATH + "/images/add.png").resize((img_size, img_size)))
        exit_icon = ImageTk.PhotoImage(Image.open(PATH + "/images/power-off.png").resize((img_size, img_size)))
        detec_icon = ImageTk.PhotoImage(Image.open(PATH + "/images/magnifying-glass.png").resize((img_size, img_size)))

        self.btnChoose = customtkinter.CTkButton(master=self.frame_left,
                                                 text="Choose file",
                                                 fg_color=("gray75", "gray30"),
                                                 command=self.choosefile,
                                                 image=add_path)
        self.btnChoose.grid(row=2, column=0, pady=10, padx=20)

        self.btnExit = customtkinter.CTkButton(master=self.frame_left,
                                               text="Exit",
                                               fg_color=("gray75", "gray30"),
                                               command=self.on_closing,
                                               image=exit_icon)
        self.btnExit.grid(row=3, column=0, pady=10, padx=20)

        self.switch_themes = customtkinter.CTkSwitch(master=self.frame_left,
                                                     text="Dark Mode",
                                                     command=self.change_mode)
        self.switch_themes.grid(row=10, column=0, pady=10, padx=20, sticky="w")

        self.frame_right.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_right.rowconfigure(7, weight=10)
        self.frame_right.columnconfigure((0, 1), weight=1)
        self.frame_right.columnconfigure(2, weight=0)

        self.entryPath = customtkinter.CTkEntry(master=self.frame_right,
                                                width=120,
                                                placeholder_text="Video path...")
        self.entryPath.grid(row=0, column=0, columnspan=2, padx=20, sticky="we")

        self.btnDetec = customtkinter.CTkButton(master=self.frame_right,
                                                text="Detection",
                                                command=self.detection,
                                                image=detec_icon)
        self.btnDetec.grid(row=0, column=2, columnspan=1, padx=20, sticky="we")

        self.checkboxAllow = customtkinter.CTkCheckBox(master=self.frame_right,
                                                       text="Filter by seconds",
                                                       command=self.enable_seconds)
        self.checkboxAllow.grid(row=1, column=0, columnspan=1, padx=20, sticky="w")
        self.entrySeconds = customtkinter.CTkEntry(master=self.frame_right,
                                                   width=120,
                                                   placeholder_text="Seconds...")
        self.entrySeconds.grid(row=1, column=1, columnspan=1, padx=20, sticky="w")

        self.switch_themes.select()
        self.entrySeconds.configure(state=tkinter.DISABLED)
        self.checkboxAllow.configure(text="Filter video by seconds")

    def detection(self):
        second = self.entrySeconds.get()
        try:
            if second != None and second.isdigit():
                predict_folder(self.entryPath.get(), second)
            else:
                predict_folder(self.entryPath.get(), None)
        except:
            messagebox.showerror("Error", "Detection error!")

    def choosefile(self):
        try:
            self.filename = filedialog.askopenfilename(title="Select video file")
            if mimetypes.guess_type(self.filename)[0].startswith('video'):
                self.entryPath.insert('end', self.filename)
            else:
                messagebox.showerror("Error", "File video is invalid!");
        except:
            print("You must choose the file path!")

    def enable_seconds(self):
        if self.checkboxAllow.get() == True:
            self.entrySeconds.configure(state=tkinter.NORMAL)
        else:
            self.entrySeconds.configure(state=tkinter.DISABLED)

    def change_mode(self):
        if self.switch_themes.get() == True:
            customtkinter.set_appearance_mode("dark")
        else:
            customtkinter.set_appearance_mode("light")

    def on_closing(self, event=0):
        # res = messagebox.askquestion('Confirm', 'Are you sure?')
        # if res == 'yes':
        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()
