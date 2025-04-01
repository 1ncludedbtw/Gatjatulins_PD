from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
import bcrypt 

BG_COLOR = "#1E1E1E"
FG_COLOR = "#CCCCCC"
BD_COLOR = "#444444"
BT_BG_COLOR = "#FF8000"
BT_TEXT_COLOR = "#000000"
RB_COLOR = "#CCCCCC"
MAIN_BG_COLOR = "#2E2E2E"

callbackHome = None

def connect_db():
    return sqlite3.connect("kino.db")


def clearWin(root):
    for widget in root.winfo_children():
        widget.pack_forget()


def checkAdmin(username, password, status_label, root):
    conn = connect_db()
    cur = conn.cursor()
    entered_username = username.get()
    cur.execute(
        """SELECT Password FROM Admins WHERE Username = ?""",
        (
            entered_username,
        ),
    )
    temp = cur.fetchone()
    
    entered_password = password.get()
    userBytes = entered_password.encode('utf-8')

    stored_hash = temp[0].encode('utf-8')
    entered_password_bytes = entered_password.encode('utf-8')

    if bcrypt.checkpw(entered_password_bytes, stored_hash):
        print("GOOD")
        winAdminPanel(root)
    else:
        status_label.configure(text="Nav pareizs lietotājvards vai parole", bg="#CCCCCC")


def winAdminPanel(root):
    clearWin(root)
    Label(root, text="Administratoru panelis", font=("Arial", 18)).pack(pady=20)

    frame = Frame(root, bg=MAIN_BG_COLOR)
    frame.pack()

    Button(frame, text="Administratori", command=lambda: manage_admins(root), width=20).grid(
        row=0, column=0, padx=5, pady=5
    )
    Button(frame, text="Pilsetas", command=lambda: manage_cities(root), width=20).grid(
        row=0, column=1, padx=5, pady=5
    )
    Button(
        frame, text="Kinoteātri", command=lambda: manage_theaters(root), width=20
    ).grid(row=1, column=0, padx=5, pady=5)
    Button(frame, text="Filmas", command=lambda: manage_movies(root), width=20).grid(
        row=1, column=1, padx=5, pady=5
    )
    Button(frame, text="Seansi", command=lambda: manage_sessions(root), width=20).grid(
        row=2, column=0, padx=5, pady=5
    )
    Button(root, text="Atpakaļ", command=callbackHome).pack(pady=20)


def manage_items(root, table_name, name_col, title, add_callback):
    clearWin(root)
    Label(root, text=title, font=("Arial", 16)).pack(pady=10)

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT {name_col} FROM {table_name}")
    items = cur.fetchall()
    conn.close()

    listbox = Listbox(root, font=("Arial", 12), width=40, height=10)
    listbox.pack()

    for item in items:
        listbox.insert(END, item[0])

    def delete_item():
        try:
            selected = listbox.get(listbox.curselection())

            conn = connect_db()
            cur = conn.cursor()
            cur.execute(f"DELETE FROM {table_name} WHERE {name_col} = ?", (selected,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Labi", f"{title[:-1]} izdzēsts!")
            manage_items(root, table_name, name_col, title, add_callback)
        except:
            messagebox.showerror("Kļūda", "Sarakstā atlasiet vienumu!")

    Button(root, text="Nodzēst", command=delete_item).pack(pady=5)
    Button(root, text="Pievienot", command=lambda: add_callback(root)).pack(pady=5)
    Button(root, text="Atpakaļ", command=lambda: winAdminPanel(root)).pack(pady=10)


def manage_Seanses(root, table_name, name_col, title, add_callback):
    clearWin(root)
    Label(root, text=title, font=("Arial", 16)).pack(pady=10)

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        """SELECT 
            Pilsetas.Pilsetas_nosaukums,
            Filmas.Filmu_nosaukums, 
            Kinoteatri.Kinoteatru_nosaukums,
            Filmu_seanses.datums, 
            Filmu_seanses.laiks
        FROM Filmu_seanses
        INNER JOIN Filmas ON Filmu_seanses.filmu_ID = Filmas.filmu_ID 
        INNER JOIN Kinoteatri ON Filmu_seanses.kinoteatru_ID = Kinoteatri.kinoteatru_ID 
        INNER JOIN Pilsetas ON Kinoteatri.pilsetas_ID = Pilsetas.pilsetas_ID """
    )
    items = cur.fetchall()
    conn.close()

    listbox = Listbox(root, font=("Arial", 10), width=80, height=10)
    listbox.pack()

    for item in items:
        listbox.insert(
            END, f"{item[0]} | {item[1]} | {item[2]} | {item[3]} | {item[4]}"
        )

    def delete_item():
        try:
            selected = listbox.get(listbox.curselection())

            conn = connect_db()
            cur = conn.cursor()
            cur.execute(f"DELETE FROM Filmu_Seanses WHERE {name_col} = ?", (selected,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Labi", f"{title[:-1]} izdzēsts!")
            manage_items(root, table_name, name_col, title, add_callback)
        except:
            messagebox.showerror("Kļūda", "Sarakstā atlasiet vienumu!")

    Button(root, text="Nodzēst", command=delete_item).pack(pady=5)
    Button(root, text="Pievienot", command=lambda: add_callback(root)).pack(pady=5)
    Button(root, text="Atpakaļ", command=lambda: winAdminPanel(root)).pack(pady=10)


def manage_admins(root):
    manage_items(root, "Admins", "username", "Administratoru saraksts", add_admin)


def add_admin(root):
    clearWin(root)
    Label(root, text=f"Pievienot Administratoru", font=("Arial", 16)).pack(pady=10)

    entries = []
    for label in ["Lietotājvārds", "Parole"]:
        Label(root, text=label).pack()
        entry = Entry(root)
        entry.pack()
        entries.append(entry)

    def save_item():
        values = [e.get() for e in entries]
        if all(values):
            conn = connect_db()
            cur = conn.cursor()
            placeholders = ", ".join(["?" for _ in values])

            cur.execute("SELECT Username FROM Admins WHERE Username = ?", (values[0],))

            usernames = cur.fetchall()
            if len(usernames) == 0:
                username = values[0]
                password = values[1]
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cur.execute(
                    f"INSERT INTO Admins (Username, Password) VALUES ({placeholders})", (username,hashed_password.decode('utf-8'))
                )
                conn.commit()
                conn.close()
                messagebox.showinfo("Veiksmīgs","Admins pielāgots!")
            else:
                messagebox.showerror("Kļūda", "Administrātors ar šo lietotājvārdu jau ir")
        else:
              messagebox.showerror("Kļūda", "Aizpildiet visus laukus!")

    Button(root, text="Uzglābt", command=save_item).pack(pady=10)
    Button(root, text="Atpakaļ", command=lambda: winAdminPanel(root)).pack(pady=5)



def manage_cities(root):
    manage_items(root, "Pilsetas", "Pilsetas_Nosaukums", "Pilsētu saraksts", add_city)


def add_city(root):
    add_item(
        root,
        "Pilsetas",
        "Pilsetas_Nosaukums",
        ("Pilsetas Nosaukums",),
        "Pilsetas",
        manage_cities,
    )


def manage_theaters(root):
    manage_items(
        root, "Kinoteatri", "Kinoteatru_nosaukums", "Kinoteatru saraksts", add_theater
    )


def add_theater(root):
    add_item(
        root,
        "Kinoteatri",
        "Kinoteatru_nosaukums, Pilsetas_ID",
        ("Kinoteatru Nosaukums", "ID Pilsetas"),
        "Kinoteatri",
        manage_theaters,
    )


def manage_movies(root):
    manage_items(root, "Filmas", "Filmu_nosaukums", "Список Фильмов", add_movie)


def add_movie(root):
    add_item(
        root,
        "Filmas",
        "Filmu_nosaukums, zanru_ID",
        ("Filmas nosaukums", "Zanru ID"),
        "Films",
        manage_movies,
    )


def manage_sessions(root):
    manage_Seanses(root, "Filmu_seanses", "filmu_ID", "Seansu saraksts", add_session)


def add_session(root):
    add_item(
        root,
        "Filmu_seanses",
        "filmu_ID, kinoteatru_ID, datums, laiks",
        ("ID Filma", "ID Kinoteātra", "Datums (YYYY-MM-DD)", "Laiks (HH:MM)"),
        "Seanse",
        manage_sessions,
    )


def add_item(root, table, columns, labels, title, back_callback):
    clearWin(root)
    Label(root, text=f"Pievienot {title}", font=("Arial", 16)).pack(pady=10)

    entries = []
    for label in labels:
        Label(root, text=label).pack()
        entry = Entry(root)
        entry.pack()
        entries.append(entry)

    def save_item():
        values = [e.get() for e in entries]
        if all(values):
            conn = connect_db()
            cur = conn.cursor()
            placeholders = ", ".join(["?" for _ in values])
            cur.execute(
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Veiksmīgs", f"{title} pielāgots!")
            back_callback(root)
        else:
            messagebox.showerror("Kļūda", "Aizpildiet visus laukus!")

    Button(root, text="Uzglābt", command=save_item).pack(pady=10)
    Button(root, text="Atpakaļ", command=lambda: back_callback(root)).pack(pady=5)
