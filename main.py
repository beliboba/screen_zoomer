import os
import re
import mss
import threading
import tkinter as tk
from screeninfo import get_monitors
from PIL import Image, ImageTk
import keyboard

root = tk.Tk()


class App:
    label_image: tk.PhotoImage | str = None
    monitor: int = None
    size = None
    FPS: int = None
    box_width: int = None
    box_height: int = None
    x: int = None
    y: int = None
    zoom_factor: float = 1.0
    zoom_gauge: tk.Label | None = None
    zoom_gauge_opacity: float = 0.0

    def __init__(self):
        self.label = tk.Label(root)
        self.label.pack()
        root.geometry("512x512")
        root.withdraw()
        self.setup()
        self.capture_thread = threading.Thread(target=self.capture)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        self.output()
        root.deiconify()

    def center_box(self):
        monitor = get_monitors()[self.monitor - 1]
        self.box_width = root.winfo_width()
        self.box_height = root.winfo_height()
        self.x = monitor.width // 2 - self.box_width // 2
        self.y = monitor.height // 2 - self.box_height // 2

    def capture(self):
        with mss.mss() as sct:
            while True:
                # Calculate the capture area based on the zoom factor
                zoomed_width = int(self.box_width * self.zoom_factor)
                zoomed_height = int(self.box_height * self.zoom_factor)
                zoomed_x = self.x - int((zoomed_width - self.box_width) / 2)
                zoomed_y = self.y - int((zoomed_height - self.box_height) / 2)

                sct_img = sct.grab(
                    {
                        "top": zoomed_y,
                        "left": zoomed_x,
                        "width": zoomed_width,
                        "height": zoomed_height,
                        "mon": self.monitor - 1
                    }
                )
                img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
                img = img.resize((self.box_width, self.box_height), Image.Resampling.LANCZOS)  # Resize the image
                self.label_image = ImageTk.PhotoImage(img)

                # Update zoom gauge visibility
                if self.zoom_gauge:
                    if self.zoom_gauge_opacity > 0:
                        self.zoom_gauge.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
                    else:
                        self.zoom_gauge.place_forget()

    def output(self):
        if self.label_image:
            self.label.configure(image=self.label_image)
            self.label.image = self.label_image
        root.after(1000 // self.FPS, self.output)

    @staticmethod
    def prompt(text: str):
        os.system("cls || clear")
        print(text)

    def setup(self):
        monitors = get_monitors()
        self.prompt("Select monitor")
        for i, monitor in enumerate(monitors):
            print(f"{i + 1}: {monitor.width}x{monitor.height} {monitor.name}")
        try:
            monitor = int(input("monitor: "))
            if monitor < 1 or monitor > len(monitors):
                raise ValueError
            self.monitor = monitor
        except ValueError:
            print("Invalid input, using monitor 1")
            self.monitor = 1

        self.prompt("Enter FPS")
        try:
            fps = int(input("FPS: "))
            if fps < 1:
                raise ValueError
            self.FPS = fps
        except ValueError:
            print("Invalid input, using default 60 FPS")
            self.FPS = 60

        print(f"Monitor: {self.monitor}")
        print(f"FPS: {self.FPS}")

        self.center_box()
        keyboard.add_hotkey('=', self.zoom_in)
        keyboard.add_hotkey('-', self.zoom_out)
        keyboard.add_hotkey('end', self.close_app)

        root.bind('<Configure>', lambda event: self.center_box())

    def zoom_in(self):
        self.zoom_factor *= 1.1

    def zoom_out(self):
        self.zoom_factor *= 0.9

    @staticmethod
    def close_app():
        root.destroy()
        exit(0)


app = App()

root.mainloop()
