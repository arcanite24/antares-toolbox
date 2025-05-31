import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


class DatasetFilterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Dataset Filter")
        self.master.geometry("1024x768")  # Default size
        self.center_window()

        self.base_path = os.getcwd()
        self.images = []
        self.current_index = 0

        self.selected_folder = "selected"
        self.discarded_folder = "discarded"

        self.setup_ui()
        self.load_images()
        self.update_display()
        self.update_counts()

    def center_window(self):
        # Center the window on the screen
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        # Path selection
        self.path_frame = tk.Frame(self.master)
        self.path_frame.pack(pady=10)

        self.path_label = tk.Label(self.path_frame, text="Base Path:")
        self.path_label.pack(side=tk.LEFT)

        self.path_entry = tk.Entry(self.path_frame, width=50)
        self.path_entry.insert(0, self.base_path)
        self.path_entry.pack(side=tk.LEFT)

        self.path_button = tk.Button(
            self.path_frame, text="Browse", command=self.browse_path
        )
        self.path_button.pack(side=tk.LEFT)

        # Image display
        self.image_frame = tk.Frame(self.master)
        self.image_frame.pack(expand=True, fill=tk.BOTH)

        self.prev_label = tk.Label(self.image_frame)
        self.prev_label.pack(side=tk.LEFT, padx=10, expand=True)

        self.current_label = tk.Label(self.image_frame)
        self.current_label.pack(side=tk.LEFT, expand=True)

        self.next_label = tk.Label(self.image_frame)
        self.next_label.pack(side=tk.RIGHT, padx=10, expand=True)

        # Folder configuration
        self.folder_frame = tk.Frame(self.master)
        self.folder_frame.pack(pady=10)

        tk.Label(self.folder_frame, text="Selected Folder:").grid(row=0, column=0)
        self.selected_entry = tk.Entry(self.folder_frame, width=20)
        self.selected_entry.insert(0, self.selected_folder)
        self.selected_entry.grid(row=0, column=1)

        tk.Label(self.folder_frame, text="Discarded Folder:").grid(row=1, column=0)
        self.discarded_entry = tk.Entry(self.folder_frame, width=20)
        self.discarded_entry.insert(0, self.discarded_folder)
        self.discarded_entry.grid(row=1, column=1)

        # Add count labels
        self.count_frame = tk.Frame(self.master)
        self.count_frame.pack(pady=5)

        self.remaining_label = tk.Label(self.count_frame, text="Remaining: 0")
        self.remaining_label.pack(side=tk.LEFT, padx=10)

        self.selected_count_label = tk.Label(self.count_frame, text="Selected: 0")
        self.selected_count_label.pack(side=tk.LEFT, padx=10)

        self.discarded_count_label = tk.Label(self.count_frame, text="Discarded: 0")
        self.discarded_count_label.pack(side=tk.LEFT, padx=10)

        # Add notification label
        self.notification_label = tk.Label(self.master, text="", fg="green")
        self.notification_label.pack(pady=5)

        # Help labels
        self.help_frame = tk.Frame(self.master)
        self.help_frame.pack(side=tk.BOTTOM, pady=10)

        tk.Label(self.help_frame, text="Up Arrow: Move to Selected").pack(side=tk.LEFT, padx=10)
        tk.Label(self.help_frame, text="Down Arrow: Move to Discarded").pack(side=tk.LEFT, padx=10)

        # Key bindings
        self.master.bind("<Up>", self.move_to_selected)
        self.master.bind("<Down>", self.move_to_discarded)

    def browse_path(self):
        new_path = filedialog.askdirectory()
        if new_path:
            self.base_path = new_path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self.base_path)
            self.load_images()
            self.update_display()

    def load_images(self):
        self.images = [
            f
            for f in os.listdir(self.base_path)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
        ]
        self.current_index = 0

    def update_display(self):
        if not self.images:
            return

        # Update current image
        current_img = Image.open(
            os.path.join(self.base_path, self.images[self.current_index])
        )
        current_img = current_img.resize((600, 600), Image.NEAREST)
        current_photo = ImageTk.PhotoImage(current_img)
        self.current_label.config(image=current_photo)
        self.current_label.image = current_photo

        # Update previous image
        if len(self.images) > 1:
            prev_index = (self.current_index - 1) % len(self.images)
            prev_img = Image.open(os.path.join(self.base_path, self.images[prev_index]))
            prev_img = prev_img.resize((200, 200), Image.NEAREST)
            prev_photo = ImageTk.PhotoImage(prev_img)
            self.prev_label.config(image=prev_photo)
            self.prev_label.image = prev_photo
        else:
            self.prev_label.config(image="")

        # Update next image
        if len(self.images) > 1:
            next_index = (self.current_index + 1) % len(self.images)
            next_img = Image.open(os.path.join(self.base_path, self.images[next_index]))
            next_img = next_img.resize((200, 200), Image.NEAREST)
            next_photo = ImageTk.PhotoImage(next_img)
            self.next_label.config(image=next_photo)
            self.next_label.image = next_photo
        else:
            self.next_label.config(image="")

    def update_counts(self):
        remaining = len(self.images)
        
        selected_path = os.path.join(self.base_path, self.selected_folder)
        discarded_path = os.path.join(self.base_path, self.discarded_folder)
        
        selected = len(os.listdir(selected_path)) if os.path.exists(selected_path) else 0
        discarded = len(os.listdir(discarded_path)) if os.path.exists(discarded_path) else 0

        self.remaining_label.config(text=f"Remaining: {remaining}")
        self.selected_count_label.config(text=f"Selected: {selected}")
        self.discarded_count_label.config(text=f"Discarded: {discarded}")

    def move_to_selected(self, event):
        self.move_image("selected")

    def move_to_discarded(self, event):
        self.move_image("discarded")

    def move_image(self, folder):
        if not self.images:
            return

        source = os.path.join(self.base_path, self.images[self.current_index])
        dest_folder = os.path.join(self.base_path, getattr(self, f"{folder}_folder"))
        os.makedirs(dest_folder, exist_ok=True)
        dest = os.path.join(dest_folder, self.images[self.current_index])

        os.rename(source, dest)
        self.images.pop(self.current_index)

        # Show non-intrusive notification
        self.show_notification(f"Image moved to {folder} folder")

        if self.images:
            self.current_index %= len(self.images)
            self.update_display()
            self.update_counts()
        else:
            self.current_label.config(image="")
            self.prev_label.config(image="")
            self.next_label.config(image="")
            self.update_counts()

    def show_notification(self, message):
        self.notification_label.config(text=message)
        self.master.after(2000, lambda: self.notification_label.config(text=""))

if __name__ == "__main__":
    root = tk.Tk()
    app = DatasetFilterApp(root)
    root.mainloop()
