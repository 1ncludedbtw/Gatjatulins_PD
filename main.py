from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3
import admin

# Izveido savienojumu ar SQLite datubāzi
conn = sqlite3.connect("kino.db")
cur = conn.cursor()

# Krāsu definīcijas
BG_COLOR = "#1E1E1E"
FG_COLOR = "#CCCCCC"
BD_COLOR = "#444444"
BT_BG_COLOR = "#FF8000"
BT_TEXT_COLOR = "#000000"
RB_COLOR = "#CCCCCC"
MAIN_BG_COLOR = "#2E2E2E"

# Funkcija loga definēšanai (galvenais vai virslogu)
def defineWindow(window_width, window_height, title, bg, ifTopLevel):
    if ifTopLevel:
        # Izveido jaunu logu, kas ir virs esošā
        temp = Toplevel()
        temp.configure(bg=bg)
        temp.resizable(False, False)  # Logs nav pārveidojams
        temp.title(title)
        temp.transient(root)
        temp.grab_set()  # Bloķē citu logu darbību, līdz šis logs tiek aizvērts
        return temp
    else:
        # Izveido galveno logu
        temp = Tk()
        temp.resizable(False, False)
        temp.configure(bg=bg)
        temp.title(title)
        if window_width != 0 and window_height != 0:
            # Nosaka loga izmērus un centrē to ekrānā
            screen_width = temp.winfo_screenwidth()
            screen_height = temp.winfo_screenheight()
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)
            temp.geometry(f"{window_width}x{window_height}+{x}+{y}")
        return temp

# Funkcija, kas iztīra loga saturu
def clearWin(root):
    for widget in root.winfo_children():
        widget.pack_forget()

# Kontaktinformācijas loga funkcija
def winContact():
    clearWin(root)

    contact_info = "Tālrunis: +371 123 4567\nEmail: kino@example.com\nAdrese: Tautas iela 59, Daugavpils"
    contact_label = Label(
        root,
        text=contact_info,
        font=("Arial", 18),
        justify=LEFT,
        bg=MAIN_BG_COLOR,
        fg=FG_COLOR,
    )
    contact_label.pack()

    # Atpakaļ poga
    back_button = Button(root, text="Atpakaļ", command=winMain)
    back_button.pack()

# Galvenais logs, kur tiek attēlots filmu saraksts
def winMain():
    global Lb

    clearWin(root)
    clearWin(fram1)

    framTitle = Frame(root)
    framTitle.pack()

    # Loga virsraksts
    text2 = Label(
        framTitle,
        text="Kur noskatīties?",
        font=("Zettameter Regular", 50),
        fg=FG_COLOR,
        bg=BG_COLOR,
        bd=2,
        relief="solid",
        padx=10,
    )
    text2.pack()

    # Galvenais filtrēšanas un filmu saraksta rādis
    fram1.pack(side=LEFT, padx=5)

    addGenres(fram1, Lb)
    cur.execute("""SELECT Filmu_Nosaukums FROM Filmas""")
    res = cur.fetchall()
    for i in res:
        Lb.insert(END, i[0])  # Ielādē visas filmas sarakstā
    Lb.pack(side="left")

    Lb.bind("<Double-Button-1>", selected_item)  # Dubultklikšķis uz filmas, lai izvēlētos

# Administrācijas loga funkcija
def winAdmin():
    global username, password, status_label

    clearWin(root)
    clearWin(fram1)

    fram1.pack(expand=True)
    Label(fram1, text="Administratoru panelis", font=("Arial", 16)).pack(pady=10)
    Label(fram1, text="Lietotājvārds:").pack()
    username = Entry(fram1, font=("Arial", 14))  # Lietotājvārda ievades lauks
    username.pack()
    Label(fram1, text="Parole:").pack()
    password = Entry(fram1, font=("Arial", 14), show="*")  # Paroles ievades lauks
    password.pack()
    Button(
        fram1,
        text="Login",
        font=("Arial", 14),
        command=lambda: admin.checkAdmin(username, password, status_label, root),  # Admina pieteikšanās funkcija
    ).pack(pady=10)
    status_label = Label(fram1, text="", font=("Arial", 12), bg=MAIN_BG_COLOR)
    status_label.pack()

# Galvenais izvēlnes pievienošanas funkcija
def addMenu(root):
    menu = Menu(root, bg=FG_COLOR)
    root.config(menu=menu)
    menu.add_cascade(label="Main", command=winMain)  # Galvenais logs
    menu.add_cascade(label="Kontakt Informācija", command=winContact)  # Kontaktinformācija
    menu.add_cascade(label="Administratori", command=winAdmin)  # Administratori

# Funkcija žanru filtrēšanai
def addGenres(frame, Lb):
    global v
    framGenres = Frame(fram1, bg=BD_COLOR, bd=5, relief="solid")
    framGenres.pack(anchor="nw")
    buttFilter = Button(
        framGenres, text="Filtrēt", command=filterGenre, font=("Arial", 9)
    )

    v = IntVar()  # Atzīmēto žanru saglabāšana

    cur.execute("SELECT zanru_ID, Zanru_Nosaukums FROM Zanri")
    res = cur.fetchall()

    # Pievieno radiopogas žanriem
    columns = 3
    for i, (zanru_ID, zanru_name) in enumerate(res):
        radbutt = Radiobutton(
            framGenres,
            text=zanru_name,
            variable=v,
            value=zanru_ID,
            fg=BT_TEXT_COLOR,
            bd=2,
            relief="solid",
            font=("Arial", 9),
        )
        radbutt.grid(row=i // columns, column=i % columns, sticky="w", padx=5, pady=3)

    buttFilter.grid(pady=5)

    cur.execute("SELECT Filmu_nosaukums FROM Filmas")
    films = cur.fetchall()

    for film in films:
        Lb.insert(END, film[0])  # Ielādē visas filmas sarakstā

# Funkcija, lai parādītu, kur var skatīties izvēlēto filmu
def showWhereToWatch():
    for i in Lb.curselection():
        temp = Lb.get(i)
    print("1)", temp)
    cur.execute(
        """SELECT 
            Filmas.Filmu_nosaukums, 
            Filmu_seanses.datums, 
            Filmu_seanses.laiks,
            Kinoteatri.Kinoteatru_nosaukums,
            Pilsetas.Pilsetas_nosaukums
        FROM Filmu_seanses
        INNER JOIN Filmas ON Filmu_seanses.filmu_ID = Filmas.filmu_ID 
        INNER JOIN Kinoteatri ON Filmu_seanses.kinoteatru_ID = Kinoteatri.kinoteatru_ID 
        INNER JOIN Pilsetas ON Kinoteatri.pilsetas_ID = Pilsetas.pilsetas_ID
        WHERE Filmas.Filmu_nosaukums = ?""",
        (temp,),
    )
    res = cur.fetchall()
    print(temp, res, len(res))

    if len(res) == 0:
        textRes = f'Filmai "{temp}" tagad nav seansu'
    else:
        textRes = f'Filmu "{res[0][0]}" var paskatīties:\n'
        for i in res:
            textRes = textRes + f"\t- {i[4]} {i[3]} {i[1]} {i[2]} \n"
    winShow = defineWindow(0, 0, "Seansi", MAIN_BG_COLOR, 1)
    textWhereToWatch = Label(
        winShow, text=textRes, justify="left", bg=MAIN_BG_COLOR, fg=FG_COLOR
    )
    textWhereToWatch.pack()
    Button(winShow, text="Aizvērt", command=winShow.destroy).pack()
    winShow.mainloop()

# Funkcija žanra filtrēšanai
def filterGenre():
    global v, Lb

    genre_id = v.get()

    Lb.delete(0, END)  # Iztīra esošo sarakstu

    cur.execute(
        """
        SELECT Filmu_nosaukums FROM Filmas WHERE zanru_ID = ?""",
        (genre_id,),
    )

    res = cur.fetchall()

    for film in res:
        Lb.insert(END, film[0])  # Ielādē tikai izvēlētā žanra filmas

# Funkcija, kas tiek izsaukta, kad tiek izvēlēta filma
def selected_item(event):
    clearWin(fram2)
    w = Label(fram2)
    text1 = Label(
        fram2, text="", wraplength=370, font=("Arial", 15), bg=BD_COLOR, fg=FG_COLOR
    )
    btnShow = Button(
        fram2,
        text="Paradīt, kur paskatīties!",
        command=showWhereToWatch,
        bg=BD_COLOR,
        bd=2,
        relief="ridge",
        fg=FG_COLOR,
    )

    for i in Lb.curselection():
        temp = Lb.get(i)
        print(temp)
    cur.execute(f"SELECT filmu_ID FROM Filmas WHERE Filmu_nosaukums = '{temp}'")
    tempid = cur.fetchall()

    id1 = f"data/{tempid[0][0]}.png"  # Attēla faila nosaukums
    image = Image.open(id1)
    image.thumbnail((300, 300))
    resized_image = image.copy()
    img = ImageTk.PhotoImage(resized_image)

    cur.execute(f"SELECT Filmu_info FROM Filmas WHERE Filmu_nosaukums = '{temp}'")
    temp1 = cur.fetchall()

    text1.configure(text=temp1[0][0])
    w.configure(image=img)
    w.image = img

    w.pack()
    text1.pack()
    btnShow.pack(pady=10)
    fram2.pack()

# Galvenais loga izveidesa
root = defineWindow(800, 700, "Kur noskatīties?", MAIN_BG_COLOR, 0)
v = IntVar()  # Atzīmētā žanra saglabāšana
framTitle = Frame(root, height=100, width=200)
fram1 = Frame(root, height=100, width=100, bg=MAIN_BG_COLOR)
fram2 = Frame(root, bd=5, relief="sunken", bg=BG_COLOR)
Lb = Listbox(
    fram1, font=("Arial", 14), bg=BD_COLOR, fg=FG_COLOR, bd=5, relief="solid", width=35
)
addMenu(root)  # Pievieno izvēlni
text2 = Label(
    framTitle, text="Kur noskatīties?", font=("Zettameter Regular", 50), fg="red"
)
winMain()  # Galvenais logs tiek atvērts
root.mainloop()
