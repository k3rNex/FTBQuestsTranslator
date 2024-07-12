import os
import re
import json
from tkinter import Tk, Button, Label, filedialog, StringVar, ttk, messagebox
from googletrans import Translator
import threading


class QuestTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quest Translator")

        self.label = Label(root, text="Выберите директорию с квестами")
        self.label.pack(pady=10)

        self.dir_var = StringVar()
        self.dir_label = Label(root, textvariable=self.dir_var)
        self.dir_label.pack(pady=5)

        self.select_button = Button(root, text="Выбрать директорию", command=self.select_directory)
        self.select_button.pack(pady=5)

        self.translate_button = Button(root, text="Начать перевод", command=self.start_translation)
        self.translate_button.pack(pady=20)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)

    def start_translation(self):
        self.progress["value"] = 0
        if not self.dir_var.get():
            messagebox.showwarning("Внимание", "Пожалуйста, выберите директорию с квестами.")
            return

        threading.Thread(target=self.translate_quests).start()

    def translate_quests(self):
        quests_dir = self.dir_var.get()
        lang_file_path = os.path.join(quests_dir, 'lang', 'ru_ru.lang')
        quest_data = []

        # Создаем папку lang, если она не существует
        if not os.path.exists(os.path.join(quests_dir, 'lang')):
            os.makedirs(os.path.join(quests_dir, 'lang'))

        snbt_files = [f for f in os.listdir(quests_dir) if f.endswith('.snbt')]
        total_files = len(snbt_files)

        for i, filename in enumerate(snbt_files):
            with open(os.path.join(quests_dir, filename), 'r', encoding='utf-8') as file:
                snbt_content = file.read()
                quest_data.extend(self.parse_snbt(snbt_content))
            self.progress["value"] = ((i + 1) / total_files) * 100
            self.root.update_idletasks()

        translated_quests = self.translate_texts(quest_data)
        self.save_to_lang_file(translated_quests, lang_file_path)

        messagebox.showinfo("Завершено", f"Перевод завершен и сохранен в {lang_file_path}")

    def parse_snbt(self, snbt_content):
        quests = re.findall(r'\{.*?\}', snbt_content, re.DOTALL)
        quest_data = []

        for quest in quests:
            title = re.search(r'"title":\s*"(.*?)"', quest).group(1)
            subtitle = re.search(r'"subtitle":\s*"(.*?)"', quest).group(1)
            description = re.search(r'"description":\s*"(.*?)"', quest).group(1)
            quest_id = re.search(r'"id":\s*"(.*?)"', quest).group(1)
            quest_data.append({
                'id': quest_id,
                'title': title,
                'subtitle': subtitle,
                'description': description
            })

        return quest_data

    def translate_texts(self, quest_data, target_lang='ru'):
        translator = Translator()
        for quest in quest_data:
            quest['title'] = translator.translate(quest['title'], dest=target_lang).text
            quest['subtitle'] = translator.translate(quest['subtitle'], dest=target_lang).text
            quest['description'] = translator.translate(quest['description'], dest=target_lang).text
        return quest_data

    def save_to_lang_file(self, quest_data, lang_file_path):
        with open(lang_file_path, 'w', encoding='utf-8') as lang_file:
            for quest in quest_data:
                lang_file.write(f'quest.{quest["id"]}.title={quest["title"]}\n')
                lang_file.write(f'quest.{quest["id"]}.subtitle={quest["subtitle"]}\n')
                lang_file.write(f'quest.{quest["id"]}.description={quest["description"]}\n')


if __name__ == "__main__":
    root = Tk()
    app = QuestTranslatorApp(root)
    root.mainloop()
