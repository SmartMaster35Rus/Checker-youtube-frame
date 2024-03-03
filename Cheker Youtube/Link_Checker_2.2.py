import os
import sys
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import logging


class CheckerWindow:
    def __init__(self, master):
        self.master = master
        master.title("Link Checker 2.2")
        self.master.geometry("900x700")

        # создаем меню
        self.menu_bar = tk.Menu(master)
        master.config(menu=self.menu_bar)

        # добавляем опцию "Файл"
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)

        # добавляем опцию "Открыть"
        self.file_menu.add_command(label="Открыть", command=self.select_file)

        # добавляем разделитель
        self.file_menu.add_separator()

        # добавляем опцию "Инструкция"
        self.file_menu.add_command(label="Инструкция", command=self.show_instructions)

        # добавляем опцию "Выход"
        self.file_menu.add_command(label="Выход", command=self.master.destroy)

        self.result_text = tk.Text(master, height=30)
        self.result_text.pack(fill=tk.BOTH, padx=10, pady=10)
        self.result_text.configure(bg='black', fg='white')

        # добавляем опцию "О программе"
        self.about_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="О программе", menu=self.about_menu)
        self.about_menu.add_command(label="Информация о программе", command=self.show_about)

        # Создание стиля кнопок
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 12), padding=10, foreground='black', background='white')

        # Кнопка проверки ссылок
        self.check_button = ttk.Button(master, text="Проверить ссылки", command=self.check_links, style='TButton')
        self.check_button.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.X)

        # Кнопка закрытия программы
        self.exit_button = ttk.Button(master, text="Закрыть программу", command=self.master.destroy, style='TButton')
        self.exit_button.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.X)

        # Инициализация логгера
        self.logger = logging.getLogger('LinkChecker')
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('link_checker.log')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Открытие файла лога
        self.log_file = open('log.txt', 'w', encoding='utf-8')

    def show_instructions(self):
        with open('E:/WORK/project/Python/test/instruction.txt', 'r', encoding='utf-8') as f:
            instructions_text = f.read()
        instructions_window = tk.Toplevel(self.master)
        instructions_window.title("Инструкция")
        instructions_label = tk.Label(instructions_window, text=instructions_text, padx=10, pady=10, justify="left")
        instructions_label.pack()


    def show_about(self):
        with open('E:/WORK/project/Python/test/about.txt', 'r', encoding='utf-8') as f:
            about_text = f.read()
        about_window = tk.Toplevel(self.master)
        about_window.title("О программе")
        about_label = tk.Label(about_window, text=about_text,padx=10, pady=10, justify="left")
        about_label.pack()
        self.about_menu = tk.Menu(self.menu_bar, tearoff=0)

    def select_file(self):
        filetypes = [('Text files', '*.txt'), ('All files', '*')]
        filename = tk.filedialog.askopenfilename(title="Выберите файл", filetypes=filetypes)
        if filename:
            self.file_path = filename
            self.result_text.insert(tk.END, f"Файл {filename} выбран\n")
        else:
            self.result_text.insert(tk.END, "Файл не выбран\n")

    def check_links(self):
        if not hasattr(self, 'file_path'):
            self.result_text.insert(tk.END, "Сначала выберите файл с ссылками для проверки\n")
            return 
    
        # Получаем ссылки из файла
        with open(self.file_path, 'r') as f:
            page_links = f.read().splitlines()

        # Запускаем проверку ссылок
        for link in page_links:
            response = requests.get(link)
            soup = BeautifulSoup(response.content, 'html.parser')
            videos = soup.find_all('iframe')
            for video in videos:
                src = video.get('src')
                if 'youtube' in src:
                    video_id = src.split('/')[-1]
                    check_url = f'https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={video_id}&format=json'
                    response = requests.get(check_url)
                    if response.status_code == 200:
                        result = f'Видео {video_id} на странице {link} Работает!'
                    else:
                        result = f'Видео {video_id} на странице {link} !!!НУЖНО ЗАМЕНИТЬ!!!'
                    self.result_text.insert(tk.END, result + '\n')
                    print(result)

                elif 'vimeo' in src:
                    video_id = src.split('/')[-1]
                    check_url = f'https://vimeo.com/api/oembed.json?url=https://vimeo.com/{video_id}'
                    response = requests.get(check_url)
                    if response.status_code == 200:
                        result = f'Видео {video_id} на странице {link} Работает!'
                    else:
                        result = f'Видео {video_id} на странице {link} !!!НУЖНО ЗАМЕНИТЬ!!!'
                    self.result_text.insert(tk.END, result + '\n')
                    print(result)

                else:
                    result = f'Video on page {link} has unknown source'
                    self.result_text.insert(tk.END, result + '\n')
                    print(result)

                # Запись результатов в лог
                self.log_file.write(result + '\n')
                self.master.update_idletasks()  # обновляем интерфейс после каждой проверки

    def __del__(self):
        # Закрытие файла лога
        self.log_file.close()


# Создаем экземпляр класса окна
root = tk.Tk()
checker_window = CheckerWindow(root)

# Задаем путь к файлу с иконкой
icon_path = 'E:/WORK/project/Python/test/icon.ico'

# Устанавливаем иконку окна
root.iconbitmap(default=icon_path)
root.mainloop()
