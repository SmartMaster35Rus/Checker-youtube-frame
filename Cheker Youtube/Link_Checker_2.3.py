import os
import sys
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import logging
import threading
import subprocess


class LinkCheckerThread(threading.Thread):
    def __init__(self, master, page_links, result_text, check_button, exit_button):
        threading.Thread.__init__(self)
        self.page_links = page_links
        self.result_text = result_text
        self.check_button = check_button
        self.exit_button = exit_button
        self.master = master
        self.check_button.config(state="disabled")
        self.exit_button.config(state="disabled")

    def run(self):
        # отключаем кнопки при старте потока
        self.check_button.config(state="disabled")
        self.exit_button.config(state="disabled")

        # проверяем ссылки
        for link in self.page_links:
            # выполняем проверку ссылок
            result = ''
            self.result_text.insert(tk.END, result)
            self.result_text.see(tk.END)  # прокручиваем текстовое поле вниз
            self.master.update()  # обновляем интерфейс

            # обновляем интерфейс после каждой 1 проверки
            if self.page_links.index(link) % 1 == 0:
                self.result_text.update_idletasks()
                self.master.update()  # обновляем интерфейс

        # включаем кнопки после завершения потока
        self.check_button.config(state="normal")
        self.exit_button.config(state="normal")
        self.result_text.update_idletasks()

class CheckerWindow:

    def __init__(self, master):
        self.master = master
        master.title("Link Checker 2.3")
        self.master.geometry("900x700")

        self.instruction_text = """
Инструкция по работе с программой Link Checker:

Запустите приложение, нажав на его значок.
В верхнем меню выберите "Файл" и в выпадающем списке выберите "Открыть".
Выберите файл с расширением .txt, который содержит список ссылок на страницы сайта, где размещены видео.
Нажмите кнопку "Проверить ссылки".
После завершения проверки результаты будут отображены в окне программы и записаны в файл лога.
Для закрытия программы выберите "Файл" в верхнем меню и в выпадающем списке выберите "Выход".          
        
"""

        self.about_text = """
"Link Checker 2.3" 

- это программа, которая позволяет автоматически проверять ссылки на страницах веб-сайтов. 
Программа поддерживает следующие видеохостинги: YouTube и Vimeo.

Программа имеет простой и понятный пользовательский интерфейс. 
После выбора файла с ссылками для проверки, программа запускает процесс проверки ссылок. 
Результаты проверки отображаются в окне вывода информации.

Программа также позволяет просмотреть инструкцию по использованию, а также выйти из приложения.

Надеемся, что "Link Checker 2.3" будет полезен вам при проверке ссылок на вашем веб-сайте!"

Автор: BombasterMedia Kr0nix
Дата создания: 24 марта 2023 г.
"""

        self.changelog_text = """Link Checker 2.3

История изменений:

-- 31.03.2023

Добавлена функция открытия лог файла из меню "файл" -> "открыть лог".
Отредатировано сообщение при пустом клике проверки с уточнением.
Добавлена блокировка кнопок на время проверки.
Внедрение всей информации без подгрузки с доп файлов.

-- 30.03.2023

Добавление бар меню и прогресс бара.
Добавил фукцию очистку результата для повторой проверки.
Блокировка кнопок во время проверки в основном потоке.

-- 29.03.2023

Добавление кнопок и обновление визуализации приложения.

-- 26.03.2023

Адаптация скрипта и добавление визуализации.

-- 24.03.2023

Создание и разработка скрипта."""

        # создаем меню
        self.menu_bar = tk.Menu(master)
        master.config(menu=self.menu_bar)

        # добавляем опцию "Файл"
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)

        # добавляем опцию "Открыть"
        self.file_menu.add_command(label="Открыть", command=self.select_file)
        self.file_menu.add_command(label="Открыть лог", command=self.open_log_file)       

        # добавляем разделитель
        self.file_menu.add_separator()

        # добавляем опцию "Инструкция"
        self.file_menu.add_command(label="Инструкция", command=self.show_instructions)

        # добавляем опцию "Выход"
        self.file_menu.add_command(label="Выход", command=self.master.destroy)

        self.result_text = tk.Text(master, height=30)
        self.result_text.pack(fill=tk.BOTH, padx=10, pady=10)
        self.result_text.configure(bg='black', fg='white')

        # добавляем кнопку "Очистить результаты"
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Копировать", command=self.copy_results)
        self.edit_menu.add_command(label="Очистить результаты", command=self.clear_results)
        self.menu_bar.add_cascade(label="Правка", menu=self.edit_menu)   

        # добавляем опцию "О программе"
        self.about_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="О программе", menu=self.about_menu)
        self.about_menu.add_command(label="Информация о программе", command=self.show_about)
        self.about_menu.add_command(label="История изменений", command=self.show_changes_history)  
        
        # Создание стиля кнопок
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 12), padding=10, foreground='black', background='white')

        # Создание фрейма для прогресс-бара
        self.progressbar_frame = tk.Frame(master)
        self.progressbar_frame.pack(fill=tk.X, padx=10, pady=10)

        # Создание прогресс-бара
        self.progress_bar = ttk.Progressbar(self.progressbar_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill=tk.X)

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

    def open_log_file(self):
        subprocess.run(['notepad.exe', 'log.txt'])

    def copy_results(self):
        """Копирует текст из текстового поля в буфер обмена"""
        self.master.clipboard_clear()
        self.master.clipboard_append(self.result_text.get("1.0", tk.END))

    def open_log_file(self):
        """Открывает файл лога в текстовом редакторе"""
        log_path = "log.txt"
        if os.path.isfile(log_path):
            os.startfile(log_path)
        else:
            self.result_text.insert(tk.END, f"Файл лога {log_path} не найден\n")

    def clear_results(self):
        """Очищает текстовое поле с результатами"""
        self.result_text.delete('1.0', tk.END)

    def show_instructions(self):
        with open('E:/WORK/project/Python/test/instruction.txt', 'r', encoding='utf-8') as f:
            instructions_text = f.read()
        instructions_window = tk.Toplevel(self.master)
        instructions_window.title("Инструкция")
        instructions_label = tk.Label(instructions_window, text=instructions_text, padx=10, pady=10, justify="left")
        instructions_label.pack()

    def show_instructions(self):
        about_window = tk.Toplevel(self.master)
        about_window.title("Инструкция приложения")
        about_label = tk.Label(about_window, text=self.instruction_text, padx=10, pady=10, justify="left")
        about_label.pack()

    def show_changes_history(self):
        about_window = tk.Toplevel(self.master)
        about_window.title("История изменений")
        about_label = tk.Label(about_window, text=self.changelog_text, padx=10, pady=10, justify="left")
        about_label.pack()

    def show_about(self):
        about_window = tk.Toplevel(self.master)
        about_window.title("О программе")
        about_label = tk.Label(about_window, text=self.about_text, padx=10, pady=10, justify="left")
        about_label.pack()

    def select_file(self):
        filetypes = [('Text files', '*.txt'), ('All files', '*')]
        filename = tk.filedialog.askopenfilename(title="\n Выберите файл", filetypes=filetypes)
        if filename:
            self.file_path = filename
            self.result_text.insert(tk.END, f"\n Файл {filename} выбран\n")
        else:
            self.result_text.insert(tk.END, "\n Файл не выбран\n")

    def check_links(self):
        if not hasattr(self, 'file_path'):
            self.result_text.insert(tk.END, "\n Сначала выберите файл с ссылками для проверки\n 'файл' -> открыть ")
            return 
    
        # Получаем ссылки из файла
        with open(self.file_path, 'r') as f:
            page_links = f.read().splitlines()

        # Создаем экземпляр LinkCheckerThread и запускаем его
        checker_thread = LinkCheckerThread(self.master, page_links, self.result_text, self.check_button, self.exit_button)
        checker_thread.start()

        # Определяем максимальное значение для прогресс-бара
        max_value = len(page_links)
        self.progress_bar['maximum'] = max_value

        # Запускаем проверку ссылок
        for i, link in enumerate(page_links):
            # Обновляем значение прогресс-бара
            self.progress_bar['value'] = i + 1
            self.master.update_idletasks()
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
                    self.result_text.see(tk.END)  # прокручиваем текстовое поле вниз
                    self.master.update()  # обновляем интерфейс
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
                    self.result_text.see(tk.END)  # прокручиваем текстовое поле вниз
                    self.master.update()  # обновляем интерфейс
                    print(result)

                else:
                    result = f'Video on page {link} has unknown source'
                    self.result_text.insert(tk.END, result + '\n')
                    print(result)

                # Запись результатов в лог
                self.log_file.write(result + '\n')
                self.master.update_idletasks()  # обновляем интерфейс после каждой проверки
                
        # выводим информацию о завершении проверки
        self.result_text.insert(tk.END, "Проверка завершена\n")
        self.log_file.close()

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
