import tkinter as tk
from tkinter import messagebox
import mysql.connector
import bcrypt

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123321",
    database="notes_app"
)

cursor = db.cursor()

def create_user(username, password):
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def check_user(username, password):
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
        return True
    return False

def save_note(user_id, title, content, tags):
    try:
        cursor.execute("INSERT INTO notes (user_id, title, content, tags) VALUES (%s, %s, %s, %s)",
                       (user_id, title, content, tags))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def search_notes(user_id, search_term):
    cursor.execute(
        "SELECT id, title, content, tags FROM notes WHERE user_id = %s AND (title LIKE %s OR content LIKE %s OR tags LIKE %s)",
        (user_id, f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
    return cursor.fetchall()

def get_note_by_id(note_id):
    cursor.execute("SELECT title, content, tags FROM notes WHERE id = %s", (note_id,))
    return cursor.fetchone()

def update_note(note_id, title, content, tags):
    try:
        cursor.execute("UPDATE notes SET title = %s, content = %s, tags = %s WHERE id = %s",
                       (title, content, tags, note_id))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def delete_note(note_id):
    try:
        cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Заметки")
        self.root.geometry("600x500")
        self.root.config(bg="#f4f4f9")


        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)

        self.logged_in_user_id = None
        self.create_login_screen()

    def create_login_screen(self):
        self.clear_screen()

        self.title_label = tk.Label(self.root, text="Добро пожаловать в заметки", font=("Helvetica", 16, "bold"),
                                    bg="#f4f4f9")
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="n")

        self.username_label = tk.Label(self.root, text="Логин:", font=("Helvetica", 12), bg="#f4f4f9")
        self.username_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.username_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.username_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.password_label = tk.Label(self.root, text="Пароль:", font=("Helvetica", 12), bg="#f4f4f9")
        self.password_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        self.password_entry = tk.Entry(self.root, show="*", font=("Helvetica", 12))
        self.password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.login_button = tk.Button(self.root, text="Войти", command=self.login, bg="#4CAF50", fg="white",
                                      font=("Helvetica", 12, "bold"), relief="flat", padx=20)
        self.login_button.grid(row=3, column=0, columnspan=2, pady=20)

        self.register_button = tk.Button(self.root, text="Зарегистрироваться", command=self.show_register_screen,
                                         bg="#007BFF", fg="white", font=("Helvetica", 12, "bold"), relief="flat",
                                         padx=20)
        self.register_button.grid(row=4, column=0, columnspan=2, pady=10)

    def create_main_screen(self):
        self.clear_screen()

        self.title_label = tk.Label(self.root, text="Ваши заметки", font=("Helvetica", 16, "bold"), bg="#f4f4f9")
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="n")

        self.notes_listbox = tk.Listbox(self.root, height=10, width=50, font=("Helvetica", 12), bd=0,
                                        highlightthickness=0, selectmode=tk.SINGLE)
        self.notes_listbox.grid(row=1, column=0, columnspan=2, pady=10)
        self.notes_listbox.bind("<Double-1>", self.show_note_details)

        self.search_label = tk.Label(self.root, text="Поиск:", font=("Helvetica", 16, "bold"), bg="#f4f4f9")
        self.search_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        self.search_entry = tk.Entry(self.root, font=("Helvetica", 16))  # Увеличен шрифт
        self.search_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.search_button = tk.Button(self.root, text="Поиск", command=self.search_notes, bg="#FF9800", fg="white",
                                       font=("Helvetica", 12, "bold"), relief="flat", padx=20)
        self.search_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.create_note_button = tk.Button(self.root, text="Создать заметку", command=self.create_note_screen,
                                            bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), relief="flat",
                                            padx=20)
        self.create_note_button.grid(row=4, column=0, columnspan=2, pady=20)

        self.edit_note_button = tk.Button(self.root, text="Редактировать заметку", command=self.edit_note,
                                          bg="#FF9800", fg="white", font=("Helvetica", 12, "bold"), relief="flat",
                                          padx=20)
        self.edit_note_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.delete_note_button = tk.Button(self.root, text="Удалить заметку", command=self.delete_note,
                                            bg="#F44336", fg="white", font=("Helvetica", 12, "bold"), relief="flat",
                                            padx=20)
        self.delete_note_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.load_notes()

    def delete_note(self):
        selected_note_index = self.notes_listbox.curselection()
        if selected_note_index:
            note_id = self.notes_listbox.get(selected_note_index)[0]
            cursor.execute("SELECT title FROM notes WHERE id = %s", (note_id,))
            note = cursor.fetchone()
            if note:
                confirm = messagebox.askyesno("Подтвердите удаление", f"Вы уверены, что хотите удалить заметку '{note[0]}'?")
                if confirm:
                    delete_note(note_id)
                    self.load_notes()
                    messagebox.showinfo("Успех", "Заметка удалена.")
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите заметку для удаления.")

    def load_notes(self):
        self.notes_listbox.delete(0, tk.END)
        cursor.execute("SELECT id, title FROM notes WHERE user_id = %s", (self.logged_in_user_id,))
        notes = cursor.fetchall()
        for note in notes:
            self.notes_listbox.insert(tk.END, (note[0], note[1]))

    def search_notes(self):
        search_term = self.search_entry.get()
        if search_term:
            notes = search_notes(self.logged_in_user_id, search_term)
            self.notes_listbox.delete(0, tk.END)
            for note in notes:
                self.notes_listbox.insert(tk.END, (note[0], f"{note[1]} (Теги: {note[3]})"))

    def show_note_details(self, event):
        selected_note_index = self.notes_listbox.curselection()
        if selected_note_index:
            note_id = self.notes_listbox.get(selected_note_index)[0]
            note_details = get_note_by_id(note_id)
            if note_details:
                self.show_note_details_screen(note_details)

    def show_note_details_screen(self, note_details):
        self.clear_screen()
        self.note_title = tk.Label(self.root, text=note_details[0], font=("Helvetica", 16, "bold"), bg="#f4f4f9")
        self.note_title.grid(row=0, column=0, columnspan=2, pady=20)

        self.note_content = tk.Label(self.root, text=note_details[1], font=("Helvetica", 12), bg="#f4f4f9")
        self.note_content.grid(row=1, column=0, columnspan=2, pady=20)

        self.note_tags = tk.Label(self.root, text="Теги: " + note_details[2], font=("Helvetica", 12), bg="#f4f4f9")
        self.note_tags.grid(row=2, column=0, columnspan=2, pady=10)

        self.back_button = tk.Button(self.root, text="Назад", command=self.create_main_screen, bg="#4CAF50", fg="white",
                                     font=("Helvetica", 12, "bold"), relief="flat", padx=20)
        self.back_button.grid(row=3, column=0, columnspan=2, pady=20)

    def create_note_screen(self):
        self.clear_screen()

        self.note_title_label = tk.Label(self.root, text="Заголовок:", font=("Helvetica", 12), bg="#f4f4f9")
        self.note_title_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.note_title_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.note_title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.note_content_label = tk.Label(self.root, text="Содержимое:", font=("Helvetica", 12), bg="#f4f4f9")
        self.note_content_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.note_content_text = tk.Text(self.root, font=("Helvetica", 12), height=10, width=40)
        self.note_content_text.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.note_tags_label = tk.Label(self.root, text="Теги:", font=("Helvetica", 12), bg="#f4f4f9")
        self.note_tags_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        self.note_tags_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.note_tags_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Кнопка для сохранения заметки
        self.save_button = tk.Button(self.root, text="Сохранить", command=self.save_note, bg="#4CAF50", fg="white",
                                     font=("Helvetica", 12, "bold"), relief="flat", padx=20)
        self.save_button.grid(row=3, column=0, columnspan=2, pady=20)

        # Кнопка для отмены создания заметки
        self.cancel_button = tk.Button(self.root, text="Отмена", command=self.create_main_screen, bg="#F44336",
                                       fg="white",
                                       font=("Helvetica", 12, "bold"), relief="flat", padx=20)
        self.cancel_button.grid(row=4, column=0, columnspan=2, pady=10)

    def save_note(self):
        title = self.note_title_entry.get()
        content = self.note_content_text.get("1.0", tk.END).strip()
        tags = self.note_tags_entry.get()
        save_note(self.logged_in_user_id, title, content, tags)
        self.create_main_screen()

    def edit_note(self):
        selected_note_index = self.notes_listbox.curselection()
        if selected_note_index:
            note_id = self.notes_listbox.get(selected_note_index)[0]
            note_details = get_note_by_id(note_id)
            self.create_edit_note_screen(note_id, note_details)
        else:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите заметку для редактирования.")

    def create_edit_note_screen(self, note_id, note_details):
        self.clear_screen()

        self.note_title_label = tk.Label(self.root, text="Заголовок:", font=("Helvetica", 12), bg="#f4f4f9")
        self.note_title_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.note_title_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.note_title_entry.insert(0, note_details[0])
        self.note_title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.note_content_label = tk.Label(self.root, text="Содержимое:", font=("Helvetica", 12), bg="#f4f4f9")
        self.note_content_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.note_content_text = tk.Text(self.root, font=("Helvetica", 12), height=10, width=40)
        self.note_content_text.insert(tk.END, note_details[1])
        self.note_content_text.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.note_tags_label = tk.Label(self.root, text="Теги:", font=("Helvetica", 12), bg="#f4f4f9")
        self.note_tags_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        self.note_tags_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.note_tags_entry.insert(0, note_details[2])
        self.note_tags_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.save_button = tk.Button(self.root, text="Сохранить изменения", command=lambda: self.update_note(note_id), bg="#4CAF50", fg="white",
                                     font=("Helvetica", 12, "bold"), relief="flat", padx=20)
        self.save_button.grid(row=3, column=0, columnspan=2, pady=20)

    def update_note(self, note_id):
        title = self.note_title_entry.get()
        content = self.note_content_text.get("1.0", tk.END).strip()
        tags = self.note_tags_entry.get()
        update_note(note_id, title, content, tags)
        self.create_main_screen()

    def show_register_screen(self):
        self.clear_screen()

        self.username_label = tk.Label(self.root, text="Логин:", font=("Helvetica", 12), bg="#f4f4f9")
        self.username_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.username_entry = tk.Entry(self.root, font=("Helvetica", 12))
        self.username_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.password_label = tk.Label(self.root, text="Пароль:", font=("Helvetica", 12), bg="#f4f4f9")
        self.password_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        self.password_entry = tk.Entry(self.root, show="*", font=("Helvetica", 12))
        self.password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.register_button = tk.Button(self.root, text="Зарегистрироваться", command=self.register_user,
                                         bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), relief="flat",
                                         padx=20)
        self.register_button.grid(row=3, column=0, columnspan=2, pady=20)

        self.login_button = tk.Button(self.root, text="Уже есть аккаунт? Войти", command=self.create_login_screen,
                                      bg="#007BFF", fg="white", font=("Helvetica", 12, "bold"), relief="flat",
                                      padx=20)
        self.login_button.grid(row=4, column=0, columnspan=2, pady=10)

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        create_user(username, password)
        messagebox.showinfo("Успех", "Регистрация прошла успешно. Вы можете войти в свой аккаунт.")
        self.create_login_screen()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and check_user(username, password):
            self.logged_in_user_id = user[0]
            self.create_main_screen()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.grid_forget()

root = tk.Tk()
app = NotesApp(root)
root.mainloop()