import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, font, simpledialog
import os
from PyPDF2 import PdfReader
import pyttsx3


class StringApp:
    def __init__(self, root):

        self.root = root
        self.root.title("String")
        self.root.geometry("600x400")
        self.filename = None
        self.default_font_size = 12
        self.saved_content = ""
        self.saved = True
        self.dark_mode = False

        # Configure grid layout to ensure proper resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create text area with undo enabled
        self.text_area = tk.Text(
            self.root, undo=True, wrap="word", font=("Consolas", self.default_font_size)
        )
        self.text_area.grid(row=0, column=0, sticky="nsew")

        # Binding to make sure every change is added to the undo stack
        self.text_area.bind("<KeyPress>", self.add_to_undo)

        # Create the Menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_command(label="Export to Audio", command=self.export_to_audio)

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo_text)
        edit_menu.add_command(label="Redo", command=self.redo_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_text)
        edit_menu.add_command(label="Copy", command=self.copy_text)
        edit_menu.add_command(label="Paste", command=self.paste_text)
        edit_menu.add_command(label="Select All", command=self.select_all_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="Time/Date", command=self.insert_time_date)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

        # Smart menu
        smart_menu = tk.Menu(self.menu_bar, tearoff=0)
        smart_menu.add_command(
            label="Text Extract from PDF", command=self.text_extract_from_pdf
        )
        smart_menu.add_separator()
        smart_menu.add_command(label="Read Aloud", command=self.read_aloud)
        self.menu_bar.add_cascade(label="Smart", menu=smart_menu)

        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

        # Status bar
        self.status_bar = tk.Label(
            self.root, text="Line 1, Column 1 | 0 characters | 0 words", anchor="w"
        )
        self.status_bar.grid(row=1, column=0, sticky="ew")

        self.text_area.bind("<KeyRelease>", self.update_status_and_unsaved_check)

        self.root.bind("<Control-plus>", self.zoom_in)
        self.root.bind("<Control-equal>", self.zoom_in)
        self.root.bind("<Control-minus>", self.zoom_out)
        self.root.bind("<Control-0>", self.reset_zoom)
        self.root.bind("<Control-a>", self.select_all_text)

        self.text_area.bind("<<Cut>>", self.update_status_bar)
        self.text_area.bind("<<Paste>>", self.update_status_bar)
        self.text_area.bind("<<Undo>>", self.update_status_bar)
        self.text_area.bind("<<Redo>>", self.update_status_bar)

        self.text_area.bind("<Control-MouseWheel>", self.zoom_with_scroll)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def update_status_bar(self, event=None):
        row, col = self.text_area.index(tk.INSERT).split(".")
        char_count = len(self.text_area.get(1.0, tk.END)) - 1
        word_count = len(self.text_area.get(1.0, tk.END).split())
        self.status_bar.config(
            text=f"Line {int(row)}, Column {int(col)+1} | {char_count} characters | {word_count} words"
        )

    def update_status_and_unsaved_check(self, event=None):
        self.update_status_bar()
        self.check_unsaved_changes()

    def new_file(self):
        if self.prompt_save_changes():
            self.filename = None
            self.text_area.delete(1.0, tk.END)
            self.saved_content = ""
            self.saved = True
            self.update_title()
            self.update_status_bar()

    def open_file(self):
        if self.prompt_save_changes():
            self.filename = filedialog.askopenfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            )
            if self.filename:
                with open(self.filename, "r") as file:
                    self.saved_content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, self.saved_content)
                self.saved = True
                self.update_title()
            self.update_status_bar()

    def save_file(self):
        if self.filename:
            self.saved_content = self.text_area.get(1.0, tk.END)
            with open(self.filename, "w") as file:
                file.write(self.saved_content)
            self.saved = True
            self.update_title()
        else:
            self.save_as_file()

    def save_as_file(self):
        self.filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if self.filename:
            self.saved_content = self.text_area.get(1.0, tk.END)
            with open(self.filename, "w") as file:
                file.write(self.saved_content)
            self.saved = True
            self.update_title()

    def export_to_audio(self):
        self.filename = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("Audio files", "*.mp3"), ("All files", "*.*")],
        )
        if self.filename:
            text = self.text_area.get(1.0, tk.END)
            engine = pyttsx3.init()
            engine.save_to_file(text, self.filename)
            engine.runAndWait()

    def exit_app(self):
        if self.prompt_save_changes():
            self.root.quit()

    def undo_text(self):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass

    def redo_text(self):
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass

    def cut_text(self):
        self.text_area.event_generate("<<Cut>>")

    def copy_text(self):
        self.text_area.event_generate("<<Copy>>")

    def paste_text(self):
        self.text_area.event_generate("<<Paste>>")

    def select_all_text(self, event=None):
        self.text_area.tag_add("sel", "1.0", "end")

    def insert_time_date(self):
        now = datetime.datetime.now()
        self.text_area.insert(tk.INSERT, now.strftime("%I:%M %p %d/%m/%Y"))

    def text_extract_from_pdf(self):
        self.pdfFile = filedialog.askopenfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        with open(self.pdfFile, "rb") as file:
            reader = PdfReader(file)
            number_of_pages = len(reader.pages)
            for page_num in range(number_of_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                text = " ".join(text.split())
                self.text_area.insert(tk.INSERT, text)

    def read_aloud(self):
        engine = pyttsx3.init()
        text = self.text_area.get("1.0", tk.END)
        engine.say(text)
        engine.runAndWait()

    def toggle_dark_mode(self):
        if self.dark_mode:
            self.text_area.config(bg="white", fg="black")
            self.root.config(bg="white")
            self.dark_mode = False
        else:
            self.text_area.config(bg="black", fg="white")
            self.root.config(bg="black")
            self.dark_mode = True

    def zoom_in(self, event=None):
        self.default_font_size += 1
        self.text_area.config(font=("Consolas", self.default_font_size))

    def zoom_out(self, event=None):
        if self.default_font_size > 1:
            self.default_font_size -= 1
            self.text_area.config(font=("Consolas", self.default_font_size))

    def reset_zoom(self, event=None):
        self.default_font_size = 12
        self.text_area.config(font=("Consolas", self.default_font_size))

    def zoom_with_scroll(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def add_to_undo(self, event=None):
        self.text_area.edit_separator()

    def show_about(self):
        messagebox.showinfo(
            "About",
            "'String' a simple text editor app.\nCreated by: Raisul Kayes Raka",
        )

    def prompt_save_changes(self):
        if not self.saved:
            answer = messagebox.askyesnocancel(
                "Save Changes", "Do you want to save changes to your document?"
            )
            if answer is True:
                self.save_file()
            return answer is not None
        return True

    def check_unsaved_changes(self, event=None):
        current_content = self.text_area.get(1.0, tk.END)
        self.saved = current_content == self.saved_content
        self.update_title()

    def update_title(self):
        if self.filename:
            self.root.title(
                f"String - {os.path.basename(self.filename)}{'*' if not self.saved else ''}"
            )
        else:
            self.root.title(f"String{'*' if not self.saved else ''}")


if __name__ == "__main__":
    root = tk.Tk()
    app = StringApp(root)
    root.mainloop()
