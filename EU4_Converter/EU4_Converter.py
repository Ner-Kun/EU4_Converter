import os
import shutil
import re
from tkinter import Tk, filedialog, Button, Label, Text, Scrollbar, END, RIGHT, Y, BOTTOM, Frame, LEFT, X, DISABLED, NORMAL, BOTH, VERTICAL
import queue
from datetime import datetime

class EU4ConverterApp:
    version = "0.8.4"
    conversion_map = {
        'а': 'a', 'б': '‘', 'в': '±', 'г': '’', 'ґ': 'º', 'д': '“', 'е': 'e', 'є': '¼', 'ж': '”', 'з': '•', 'и': '©',
        'і': 'i', 'ї': 'ï', 'й': '¹', 'к': '³', 'л': '˜', 'м': '´', 'н': '·', 'о': 'o', 'п': '™', 'р': 'p', 'с': 'c',
        'т': '½', 'у': '›', 'ф': '°', 'х': 'x', 'ц': '²', 'ч': 'µ', 'ш': '¶', 'щ': '¸', 'ь': '»', 'ю': '¾', 'я': '÷',
        'А': 'A', 'Б': '€', 'В': 'B', 'Г': '‚', 'Ґ': 'ª', 'Д': 'ƒ', 'Е': 'E', 'Є': '¬', 'Ж': '„', 'З': '¯', 'І': 'I',
        'Ї': 'Ï', 'Й': '‡', 'К': 'K', 'Л': 'ˆ', 'М': 'M', 'Н': 'H', 'О': 'O', 'П': '‰', 'Р': 'P', 'С': 'C', 'Т': 'T',
        'У': '‹', 'Ф': ' ', 'Х': 'X', 'Ц': '¢','Ч': '¥', 'Ш': '¦', 'Щ': '¨', 'Ю': '®', 'Я': '×'
    }
    
    reverse_conversion_map = {
        'a': 'а', '‘': 'б', '±': 'в', '’': 'г', 'º': 'ґ', '“': 'д', 'e': 'е', '¼': 'є', '”': 'ж', '•': 'з', '©': 'и',
        'i': 'і', 'ï': 'ї', '¹': 'й', '³': 'к', '˜': 'л', '´': 'м', '·': 'н', 'o': 'о', '™': 'п', 'p': 'р', 'c': 'с',
        '½': 'т', '›': 'у', '°': 'ф', 'x': 'х', '²': 'ц', 'µ': 'ч', '¶': 'ш', '¸': 'щ', '»': 'ь', '¾': 'ю', '÷': 'я',
        'A': 'А', '€': 'Б', 'B': 'В', '‚': 'Г', 'ª': 'Ґ', 'ƒ': 'Д', 'E': 'Е', '¬': 'Є', '„': 'Ж', '¯': 'З', 'I': 'І', 'Ï': 'Ї', '‡': 'Й', 'K': 'К',
        'ˆ': 'Л', 'M': 'М', 'H': 'Н', 'O': 'О', '‰': 'П', 'P': 'Р', 'C': 'С', 'T': 'Т', '‹': 'У', ' ': 'Ф', 'X': 'Х', '¢': 'Ц',
        '¥': 'Ч', '¦': 'Ш', '¨': 'Щ', '®': 'Ю', '×': 'Я'
    }

    special_symbols = {
        '‘', '±', '’', '“', '¼', '”', '•', '©', '¹', '³', '˜', '´', '·', '™', '½', '›', '°', '²', 'µ', '¶',
        '¸', '»', '¾', '÷', '€', '‚', 'ƒ', '¬', '„', '¯', 'ˆ', '‰', '‹', ' ', '¢', '¥', '¦', '¨', '®', '×'
    }


    def __init__(self, root):
        self.root = root
        self.root.title(f"EU4 Converter by Ner_Kun v{self.version}")
        self.root.geometry("500x600")
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Ico.ico")
        self.root.iconbitmap(icon_path)

        self.root.configure(bg="#2d2d2d")
        self.label = Label(self.root, text="Виберіть файл(и) .yml або теку для конвертації", bg="#2d2d2d", fg="white")
        self.label.pack(pady=10)

        self.selection_frame = Frame(self.root, bg="#2d2d2d")
        self.selection_frame.pack()

        self.select_files_button = Button(self.selection_frame, text="Обрати файл(и)", command=self.select_files, bg="#595959", fg="white")
        self.select_files_button.pack(side=LEFT, padx=5)

        self.select_folder_button = Button(self.selection_frame, text="Обрати теку", command=self.select_folder, bg="#595959", fg="white")
        self.select_folder_button.pack(side=LEFT, padx=5)

        self.reset_button = Button(self.selection_frame, text="Скинути", command=self.reset_selection, bg="#595959", fg="white")
        self.reset_button.pack_forget()

        self.selected_files_frame = Frame(self.root, bg="#2d2d2d")
        self.selected_files_frame.pack(pady=10, fill=X)

        self.selected_files_text = Text(self.selected_files_frame, wrap='word', height=10, width=50, bg="#3c3c3c", fg="white", state=DISABLED)
        self.selected_files_text.pack(side=LEFT, fill=BOTH, expand=True)

        self.scrollbar_files = Scrollbar(self.selected_files_frame, orient=VERTICAL, command=self.selected_files_text.yview)
        self.scrollbar_files.pack(side=RIGHT, fill=Y)
        self.selected_files_text.config(yscrollcommand=self.scrollbar_files.set)

        self.conversion_frame = Frame(self.root, bg="#2d2d2d")
        self.conversion_frame.pack(pady=10)

        self.convert_button = Button(self.conversion_frame, text="Конвертувати у «Альфавіт»", command=lambda: self.backup_and_process(to_special=True), bg="#595959", fg="white")
        self.convert_button.pack(side=LEFT, padx=5)

        self.reverse_convert_button = Button(self.conversion_frame, text="Конвертувати в літери", command=lambda: self.backup_and_process(to_special=False), bg="#595959", fg="white")
        self.reverse_convert_button.pack(side=LEFT, padx=5)

        self.log_frame = Frame(self.root, bg="#2d2d2d")
        self.log_frame.pack(pady=10, side=BOTTOM, fill=BOTH, expand=True)

        self.log = Text(self.log_frame, wrap='word', height=10, width=50, bg="#3c3c3c", fg="white", state=DISABLED)
        self.log.pack(pady=10, side=BOTTOM, fill=BOTH, expand=True)

        self.log_file_path = None
        self.log_file = None
        self.log.bind("<Triple-Button-1>", self.open_save_log_folder_dialog) 

        self.selected_paths = []
        self.queue = queue.Queue()
        self.root.after(100, self.process_queue)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        full_message = f"[{timestamp}] {message}\n{'-' * 62}"
        if self.log_file:
            self.log_file.write(full_message + "\n")
        
        self.queue.put(full_message)

    
    def open_save_log_folder_dialog(self, event=None):
        folder_path = filedialog.askdirectory(
            title="Виберіть папку для логу"
        )
        if folder_path:
            self.save_log_to_file(folder_path)
            self.close_log_file()

    def save_log_to_file(self, folder_path):
            try:
                log_file_name = f"EU4_Converter_Log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
                full_path = os.path.join(folder_path, log_file_name)
                self.log_file = open(full_path, "w", encoding='utf-8')
                for line in self.log.get("1.0", END).splitlines():
                    self.log_file.write(line + "\n")
            except Exception as e:
                self.log_message(f"Помилка при збереженні логу: {e}")
            else:
                self.log_message(f"Лог збережено в {full_path}")

    def close_log_file(self):
        if self.log_file:
            self.log_file.close()
            self.log_file = None
            self.log_file_path = None

    def process_queue(self):
        while not self.queue.empty():
            message = self.queue.get()
            self.log.config(state=NORMAL)
            self.log.insert(END, message + "\n")
            self.log.see(END)
            self.log.config(state=DISABLED)
        self.root.after(100, self.process_queue)

    def reset_selection(self):
        self.selected_paths = []
        self.display_selected_files()
        self.label.config(text="Виберіть файл(и) .yml або теку для конвертації")
        self.reset_button.pack_forget()
        self.log_message("Вибір скинуто.")

    def select_files(self):
        initial_dir = os.getcwd()
        paths = filedialog.askopenfilenames(initialdir=initial_dir, title="Виберіть .yml файл(и)", filetypes=[("YAML files", "*.yml")])
        if paths:
            self.selected_paths = list(paths)
            self.display_selected_files()
            self.reset_button.pack(side=LEFT, padx=5)

    def select_folder(self):
        path = filedialog.askdirectory(title="Виберіть теку")
        if path:
            self.selected_paths = [path]
            self.display_selected_files()
            self.label.config(text="Обраний шлях: \n" + path)
            self.log_message("Обраний шлях: " + path)
            self.reset_button.pack(side=LEFT, padx=5)

    def display_selected_files(self):
        self.selected_files_text.config(state=NORMAL)
        self.selected_files_text.delete('1.0', END)
        if self.selected_paths:
            if os.path.isfile(self.selected_paths[0]):
                for path in self.selected_paths:
                    self.selected_files_text.insert(END, os.path.basename(path) + "\n")
                    self.selected_files_text.insert(END, '-' * 59 + "\n")
            else:
                for root, _, filenames in os.walk(self.selected_paths[0]):
                    for filename in filenames:
                        if "l_english" in filename and filename.endswith(".yml"):
                        #if filename.endswith(".yml"):
                            file_name_only = os.path.basename(filename)
                            self.selected_files_text.insert(END, file_name_only + "\n")
                            self.selected_files_text.insert(END, '-' * 59 + "\n")
        self.selected_files_text.config(state=DISABLED)
        self.log_message("Обрані файли: " + "\n".join([os.path.basename(path) for path in self.selected_paths]))

    def convert_file(self, file_path, to_special=True):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                content = file.read()

            replaced_symbols = 0

            def replace_within_quotes(match):
                nonlocal replaced_symbols
                text = match.group(1)
                if not to_special and not any(char in self.special_symbols for char in text):
                    return match.group(0)
                current_map = self.conversion_map if to_special else self.reverse_conversion_map
                converted_text = ''.join(current_map.get(char, char) for char in text)
                replaced_count = sum(1 for char in text if char!= current_map.get(char, char))
                replaced_symbols += replaced_count
                return match.group(0).replace(text, converted_text)

            converted_content = re.sub(r'["](.*?)["]', replace_within_quotes, content)

            with open(file_path, 'w', encoding='utf-8-sig') as file:
                file.write(converted_content)

            self.log_message(f"Файл '{os.path.basename(file_path)}' конвертовано.")
            return replaced_symbols
        except Exception as e:
            self.log_message(f"Помилка при конвертації файлу '{os.path.basename(file_path)}': {e}")
            return 0

    def backup_and_process(self, to_special=True):
        if not self.selected_paths:
            self.label.config(text="Будь ласка, спочатку виберіть файл(и) або теку.")
            self.log_message("Помилка: Файл(и) або тека не обрані.")
            return

        total_replaced_symbols = 0
        converted_files = 0

        for path in self.selected_paths:
            if os.path.isfile(path) and path.endswith('.yml'):
                replaced_symbols = self.backup_and_convert_file(path, to_special)
                total_replaced_symbols += replaced_symbols
                converted_files += 1
            elif os.path.isdir(path):
                replaced_symbols, processed_files = self.backup_and_convert_directory(path, to_special)
                total_replaced_symbols += replaced_symbols
                converted_files += processed_files
            else:
                self.label.config(text="Оберіть файл(и).yml або теку.")
                self.log_message("Помилка: Оберіть файл(и).yml або теки.")

        if converted_files > 0:
            direction = "в «Альфавіт»" if to_special else "в літери"
            message = f"Конвертування {direction} завершено."
            details = f"Замінено {total_replaced_symbols} символів в {converted_files} файлах."
            self.log_message(message)
            self.log_message(details)
            self.show_popup(message, details)

    def backup_and_convert_file(self, file_path, to_special):
        backup_path = file_path + ".bak"
        try:
            shutil.copyfile(file_path, backup_path)
            self.log_message(f"Резервна копія файлу створена: {backup_path}")
        except Exception as e:
            self.log_message(f"Помилка при створенні резервної копії файлу: {e}")
            return 0
        return self.convert_file(file_path, to_special)

    def backup_and_convert_directory(self, dir_path, to_special):
        backup_base_path = dir_path + "_backup"
        yml_folders = []

        if any(os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith(".yml")):
            yml_folders.append(dir_path)

        for root, dirs, _ in os.walk(dir_path):
            for dir in dirs:
                potential_yml_folder = os.path.join(root, dir)
                if any(os.path.join(potential_yml_folder, f) for f in os.listdir(potential_yml_folder) if f.endswith(".yml")):
                    yml_folders.append(potential_yml_folder)
                    break 

        if not yml_folders:
            self.log_message(f"У {dir_path} не знайдено файлів .yml, пропущено резервне копіювання.")
            return 0, 0

        try:
            for folder in yml_folders:
                folder_name = os.path.basename(folder)
                backup_folder_path = os.path.join(backup_base_path, folder_name)
                os.makedirs(backup_folder_path, exist_ok=True)
                for item in os.listdir(folder):
                    source_item_path = os.path.join(folder, item)
                    destination_item_path = os.path.join(backup_folder_path, item)
                    if os.path.isdir(source_item_path):
                        shutil.copytree(source_item_path, destination_item_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source_item_path, destination_item_path)
                self.log_message(f"Резервну копію теки {folder_name} створено у {backup_folder_path}")
        except Exception as e:
            self.log_message(f"Помилка під час резервного копіювання теки {folder_name}: {e}")
            return 0, 0

        total_replaced_symbols = 0
        processed_files = 0

        for folder in yml_folders:
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    if filename.endswith(".yml"):
                        file_path = os.path.join(root, filename)
                        replaced_symbols = self.convert_file(file_path, to_special)
                        total_replaced_symbols += replaced_symbols
                        processed_files += 1

        return total_replaced_symbols, processed_files
    
    def show_popup(self, message, details):
        popup = Tk()
        popup.title("Завершено!")
        popup.geometry("300x140")
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Ico.ico")
        popup.iconbitmap(icon_path)
        popup.configure(bg="#2d2d2d")
        label = Label(popup, text=message, bg="#2d2d2d", fg="white")
        label.pack(pady=5)
        label = Label(popup, text=details, bg="#2d2d2d", fg="white")
        label.pack(pady=5)
        Button(popup, text="OK", command=popup.destroy, bg="#595959", fg="white").pack(pady=5)

        advice_label = Label(popup, text="Живи, Україно, живи для краси, \nДля сили, для правди, для волі!", bg="#2d2d2d", fg="#777777")
        advice_label.pack(pady=5)

        popup.mainloop()

if __name__ == "__main__":
    root = Tk()
    app = EU4ConverterApp(root)
    root.mainloop()
