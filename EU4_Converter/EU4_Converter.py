import os
import shutil
import re
import threading
from tkinter import Tk, filedialog, Button, Label, Text, Scrollbar, END, RIGHT, Y, BOTTOM, Frame, LEFT, TOP, X, DISABLED, NORMAL, BOTH, VERTICAL

version = "0.9"

conversion_map = {
    'а': 'a', 'б': '‘', 'в': '±', 'г': '’', 'д': '“', 'е': 'e', 'є': '¼', 'ж': '”', 'з': '•', 'и': '©',
    'і': 'i', 'ї': 'ï', 'й': '¹', 'к': '³', 'л': '˜', 'м': '´', 'н': '·', 'о': 'o', 'п': '™', 'р': 'p', 'с': 'c',
    'т': '½', 'у': '›', 'ф': '°', 'х': 'x', 'ц': '²', 'ч': 'µ', 'ш': '¶', 'щ': '¸', 'ь': '»', 'ю': '¾', 'я': '÷',
    'А': 'A', 'Б': '€', 'В': 'B', 'Г': '‚', 'Д': 'ƒ', 'Е': 'E', 'Є': '¬', 'Ж': '„', 'З': '¯', 'К': 'K',
    'Л': 'ˆ', 'М': 'M', 'Н': 'H', 'П': '‰', 'Р': 'P', 'С': 'C', 'Т': 'T', 'У': '‹', 'Ф': ' ', 'Ц': '¢',
    'Ч': '¥', 'Ш': '¦', 'Щ': '¨', 'Ю': '®', 'Я': '×'
}

reverse_conversion_map = {v: k for k, v in conversion_map.items()}

selected_paths = []

def log_message(message):
    log.config(state=NORMAL)
    log.insert(END, message + "\n")
    log.see(END)
    log.config(state=DISABLED)

def reset_selection():
    global selected_paths
    selected_paths = []
    display_selected_files()
    label.config(text="Виберіть файл(и) .yml або теку для конвертації")
    reset_button.pack_forget()
    log_message("Вибір скинуто.")

def select_files():
    global selected_paths
    initial_dir = os.getcwd()
    paths = filedialog.askopenfilenames(initialdir=initial_dir,
                                       title="Виберіть .yml файли",
                                       filetypes=[("YAML files", "*.yml")]
                                      )
    if paths:
        selected_paths = list(paths)
        display_selected_files()
        reset_button.pack(side=LEFT, padx=5)

def select_folder():
    global selected_paths
    path = filedialog.askdirectory(title="Виберіть теку")
    if path:
        selected_paths = [path]
        display_selected_files()
        label.config(text="Обраний шлях: \n" + path)
        log_message("Обраний шлях: " + path)
        reset_button.pack(side=LEFT, padx=5)

def convert_file(file_path, to_special=True):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            content = file.read()

        def replace_within_quotes(match):
            text = match.group(1)
            current_map = conversion_map if to_special else reverse_conversion_map
            return ''.join(current_map.get(char, char) if char in current_map else char for char in text)

        converted_content = re.sub(r'\"(.*?)\"', lambda m: '"' + replace_within_quotes(m) + '"', content)

        with open(file_path, 'w', encoding='utf-8-sig') as file:
            file.write(converted_content)

        log_message(f"Файл '{os.path.basename(file_path)}' конвертовано.")
    except Exception as e:
        log_message(f"Помилка при конвертації файлу '{os.path.basename(file_path)}': {e}")

def backup_and_process(to_special=True):
    global selected_paths
    if not selected_paths:
        label.config(text="Будь ласка, спочатку виберіть файл(и) або теку.")
        log_message("Помилка: Файл(и) або тека не обрані.")
        return

    for path in selected_paths:
        if os.path.isfile(path) and path.endswith('.yml'):
            backup_and_convert_file(path, to_special)
        elif os.path.isdir(path):
            backup_and_convert_directory(path, to_special)
        else:
            label.config(text="Оберіть файл(и) .yml або теку.")
            log_message("Помилка: Оберіть файл(и) .yml або теки.")

def backup_and_convert_file(file_path, to_special):
    backup_path = file_path + ".bak"
    try:
        shutil.copyfile(file_path, backup_path)
        log_message(f"Резервна копія файлу створена: {backup_path}")
    except Exception as e:
        log_message(f"Помилка при створенні резервної копії файлу: {e}")
        return
    convert_file(file_path, to_special)

def backup_and_convert_directory(dir_path, to_special):
    backup_path = dir_path + "_backup"
    try:
        if os.path.exists(backup_path):
            for item in os.listdir(dir_path):
                s = os.path.join(dir_path, item)
                d = os.path.join(backup_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            log_message(f"Файли резервної копії оновлено: {backup_path}")
        else:
            shutil.copytree(dir_path, backup_path)
            log_message(f"Резервна копія теки створена: {backup_path}")
    except Exception as e:
        log_message(f"Помилка при роботі з резервною копією теки: {e}")
        return

    for root, _, filenames in os.walk(dir_path):
        for filename in filenames:
            if "l_english" in filename and filename.endswith(".yml"):
                file_path = os.path.join(root, filename)
                thread = threading.Thread(target=convert_file, args=(file_path, to_special))
                thread.start()

def display_selected_files():
    selected_files_text.config(state=NORMAL)
    selected_files_text.delete('1.0', END)
    if selected_paths:
        if os.path.isfile(selected_paths[0]):
            for path in selected_paths:
                selected_files_text.insert(END, os.path.basename(path) + "\n")
        else:
            selected_files_text.insert(END, selected_paths[0] + "\n")
    selected_files_text.config(state=DISABLED)
    log_message("Обрані файли: " + "\n".join(selected_paths))

root = Tk()
root.title(f"EU4 Converter by Ner_Kun v{version}")
root.geometry("500x600")
icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Ico.ico")
root.iconbitmap(icon_path)

root.configure(bg="#2d2d2d")
label = Label(root, text="Виберіть файл(и) .yml або теку для конвертації", bg="#2d2d2d", fg="white")
label.pack(pady=10)

selection_frame = Frame(root, bg="#2d2d2d")
selection_frame.pack()

select_files_button = Button(selection_frame, text="Обрати файл(и)", command=select_files, bg="#595959", fg="white")
select_files_button.pack(side=LEFT, padx=5)

select_folder_button = Button(selection_frame, text="Обрати теку", command=select_folder, bg="#595959", fg="white")
select_folder_button.pack(side=LEFT, padx=5)

reset_button = Button(selection_frame, text="Скинути", command=reset_selection, bg="#595959", fg="white")
reset_button.pack_forget()

selected_files_frame = Frame(root, bg="#2d2d2d")
selected_files_frame.pack(pady=10, fill=X)

selected_files_text = Text(selected_files_frame, wrap='word', height=10, width=50, bg="#3c3c3c", fg="white", state=DISABLED)
selected_files_text.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar_files = Scrollbar(selected_files_frame, orient=VERTICAL, command=selected_files_text.yview)
scrollbar_files.pack(side=RIGHT, fill=Y)
selected_files_text.config(yscrollcommand=scrollbar_files.set)

conversion_frame = Frame(root, bg="#2d2d2d")
conversion_frame.pack(pady=10)

convert_button = Button(conversion_frame, text="Конвертувати у «Альфавіт»", command=lambda: backup_and_process(to_special=True), bg="#595959", fg="white")
convert_button.pack(side=LEFT, padx=5)

reverse_convert_button = Button(conversion_frame, text="Конвертувати в літери", command=lambda: backup_and_process(to_special=False), bg="#595959", fg="white")
reverse_convert_button.pack(side=LEFT, padx=5)

log_frame = Frame(root, bg="#2d2d2d")
log_frame.pack(pady=10, side=BOTTOM, fill=BOTH, expand=True)

log = Text(log_frame, wrap='word', height=10, width=50, bg="#3c3c3c", fg="white", state=DISABLED)
log.pack(pady=10, side=BOTTOM, fill=BOTH, expand=True)

root.mainloop()
