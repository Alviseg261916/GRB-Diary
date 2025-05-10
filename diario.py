# --------------------------DECLARE DEPENDECIES--------------------------

import os
import sys
from typing import Union, Callable
import customtkinter, tkinter
from tkinter import *
from PIL import Image
import pywinstyles
import openpyxl
import time
import random
import pandas
import sqlite3
import pygame
import threading
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import json
import copy

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # quando sei in eseguibile .exe
    except AttributeError:
        base_path = os.path.abspath(".")  # quando esegui .py normalmente
    return os.path.join(base_path, relative_path)

# imposta i percorsi Tcl/Tk SOLO se sei in eseguibile
if hasattr(sys, '_MEIPASS'):
    os.environ['TCL_LIBRARY'] = resource_path("tcl8.6")
    os.environ['TK_LIBRARY'] = resource_path("tk8.6")


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")
app = customtkinter.CTk()
app.title("Diario personale")
app.geometry("1920x1080")
app.iconbitmap(resource_path("Images/App_Icon.ico"))
#app.attributes("-fullscreen", True)

# --- --- --- --- --- --- Declaring variables --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- -

# --- --- --- Item mangaer variables
active_animations= {}
animations_status= {}
fade_out_progress= {}
active_fade_outs= {}

current_fade_in_widget= None
current_fade_in_color= None

current_fade_out_widget= None
current_fade_out_color= None

Common_LIM= []

# --- --- --- Data variables
Database_phrase_path= resource_path("Data/Database.db")
random_phrase_path= resource_path("Data/Phrases.xlsx")

# --- --- --- Time & Date variables
timevar= customtkinter.StringVar()
datevar= customtkinter.StringVar()

# --- --- --- Login verification
LROperationCode= 0
User_Name= customtkinter.StringVar()
User_Password= customtkinter.StringVar()
User_Name_String= customtkinter.StringVar()
User_ID= NONE
User_Status_String= StringVar()

# --- --- --- Save button
Save_Button_LIM_1=[]

# --- --- ---  Dates management
Date_Offset_1_Internal= None
Date_Offset_2_Internal= None
Date_Offset_1=0
Date_Offset_2=0

tablenameprev= None
tablename= None
tablenamenext= None

Current_Year= None
Current_Month= None

# --- --- --- Notebook
NoteTimeStamp= 0
NoteTimeStamp_C= 0
NotePresence_Year= 0
NotePresence_Month= 0
NotePresence_Day= 0

# --- --- --- NoteList
NoteListHeight= 0
SelectedNoteDay= None
SelectedNoteId= None
Notebook_List_LIM_2=[]
# --- --- --- --- --- --- Logic --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

# --- --- --- Item manager

# Funzione globale per eseguire il FadeIn su un widget
def fade_in(widget, delay, steps, color="red"):
    global current_fade_in_widget, current_fade_in_color, active_animations, animations_status

    # Se il widget è già aperto (fade_in completato), non esegue l'animazione
    if animations_status.get(widget, 0) == 1:
        return

    # Se esiste già un'animazione fade_in in corso su un altro widget, completala subito.
    if current_fade_in_widget is not None and current_fade_in_widget != widget:
        pywinstyles.set_opacity(current_fade_in_widget.winfo_id(), value=1.0, color=current_fade_in_color)
        if current_fade_in_widget in active_animations:
            del active_animations[current_fade_in_widget]
        animations_status[current_fade_in_widget] = 1
        current_fade_in_widget = None
        current_fade_in_color = None

    # Se lo stesso widget ha già un'animazione in corso, la termina.
    if widget in active_animations:
        pywinstyles.set_opacity(widget.winfo_id(), value=1.0, color=color)
        del active_animations[widget]
        animations_status[widget] = 1

    token = object()
    active_animations[widget] = token
    current_fade_in_widget = widget
    current_fade_in_color = color

    def animate(step):
        global current_fade_in_widget, current_fade_in_color, animations_status
        if active_animations.get(widget) != token:
            return  # L'animazione è stata annullata
        opacity = step / steps
        opacity = min(opacity, 1)
        pywinstyles.set_opacity(widget.winfo_id(), value=opacity, color=color)
        if step < steps:
            widget.after(delay, lambda: animate(step + 1))
        else:
            if active_animations.get(widget) == token:
                del active_animations[widget]
            if current_fade_in_widget == widget:
                current_fade_in_widget = None
                current_fade_in_color = None
            # Al termine, il widget è considerato "aperto"
            animations_status[widget] = 1

    animate(0)

# Funzione globale per eseguire il FadeOut su un widget
def fade_out(widget, delay, steps, color="red"):
    global active_animations, animations_status, fade_out_progress, active_fade_outs
    global current_fade_out_widget, current_fade_out_color

    # Se il widget è già chiuso, non esegue l'animazione
    if animations_status.get(widget, 1) == 0:
        return

    # Se esiste già un'animazione fade_out in corso su un widget diverso,
    # chiudila immediatamente.
    if current_fade_out_widget is not None and current_fade_out_widget != widget:
        pywinstyles.set_opacity(current_fade_out_widget.winfo_id(), value=0, color=current_fade_out_color)
        animations_status[current_fade_out_widget] = 0
        current_fade_out_widget.place_forget()
        if current_fade_out_widget in active_animations:
            del active_animations[current_fade_out_widget]
        if current_fade_out_widget in fade_out_progress:
            del fade_out_progress[current_fade_out_widget]
        if current_fade_out_widget in active_fade_outs:
            app.after_cancel(active_fade_outs[current_fade_out_widget])
            del active_fade_outs[current_fade_out_widget]
        current_fade_out_widget = None
        current_fade_out_color = None

    # Se il widget ha già un'animazione fade_out in corso, annullala e completa immediatamente.
    if widget in active_animations:
        if widget in active_fade_outs:
            app.after_cancel(active_fade_outs[widget])
            del active_fade_outs[widget]
        pywinstyles.set_opacity(widget.winfo_id(), value=0, color=color)
        animations_status[widget] = 0
        widget.place_forget()
        del active_animations[widget]
        if widget in fade_out_progress:
            del fade_out_progress[widget]
        return

    # Imposta il widget corrente come quello in fade_out
    current_fade_out_widget = widget
    current_fade_out_color = color

    token = object()
    active_animations[widget] = token
    fade_out_progress[widget] = 0

    def animate(step):
        global fade_out_progress, active_animations, animations_status, active_fade_outs
        fade_out_progress[widget] = step
        if active_animations.get(widget) != token:
            return  # L'animazione è stata annullata
        current_opacity = 1 - (step / steps)
        current_opacity = max(current_opacity, 0)
        pywinstyles.set_opacity(widget.winfo_id(), value=current_opacity, color=color)
        if step < steps:
            after_id = widget.after(delay, lambda: animate(step + 1))
            active_fade_outs[widget] = after_id
        else:
            if active_animations.get(widget) == token:
                del active_animations[widget]
            animations_status[widget] = 0  # Il widget è ora "chiuso"
            widget.place_forget()
            if widget in fade_out_progress:
                del fade_out_progress[widget]
            if widget in active_fade_outs:
                del active_fade_outs[widget]
            # Reset globale per il fade_out
            global current_fade_out_widget, current_fade_out_color
            current_fade_out_widget = None
            current_fade_out_color = None

    animate(0)

class ChangePage:
    def __init__(self, *pages):
        self.pages = pages

    def show_page(self, page):
        for p in self.pages:
            p.place_forget()
        page.place(relx=0.5, rely=0.5, anchor="center")

def ItemManager(listname, operationcode):
    # operationcode == 0: Rimuove items senza fade
    if operationcode == 0:
        for item in listname:
            if len(item) >= 3:
                #print("0 - List accepted")
                item[0].place_forget()
                animations_status[item[0]] = 0
            else:
                missing_items = 3 - len(item)
                print(f"{missing_items} variable{' is' if missing_items==1 else 's are'} missing in the list: {item}")

    # operationcode == 1: Mostra items senza fade
    elif operationcode == 1:
        for item in listname:
            if len(item) >= 3:
                #print("1 - List accepted")
                item[0].place(x=item[1], y=item[2])
                animations_status[item[0]] = 1
            else:
                missing_items = 3 - len(item)
                print(f"{missing_items} variable{' is' if missing_items==1 else 's are'} missing in the list: {item}")

    # operationcode == 2: Rimuove items con FadeOut
    elif operationcode == 2:
        for item in listname:
            if len(item) >= 5:
                print("2 - List accepted | FadeOut time:", item[3], "ms | Color:", item[4])
                if item[3] < 1000:
                    steps = 10
                    delay = item[3] / 10
                elif item[3] < 10000:
                    steps = 50
                    delay = item[3] / 50
                elif item[3] < 100000:
                    steps = 500
                    delay = item[3] / 500
                else:
                    print("FadeOut time too big")
                    continue
                steps = int(steps)
                delay = int(delay)
                color = item[4].strip("'")
                print("steps:", steps, "delay:", delay)
                fade_out(item[0], delay, steps, color=color)
            else:
                missing_items = 5 - len(item)
                print(f"{missing_items} variable{' is' if missing_items==1 else 's are'} missing in the list: {item}")

    # operationcode == 3: Visualizza items con FadeIn
    elif operationcode == 3:
        for item in listname:
            if len(item) >= 5:
                print("3 - List accepted | FadeIn time:", item[3], "ms | Color:", item[4])
                if item[3] < 1000:
                    steps = 10
                    delay = item[3] / 10
                elif item[3] < 10000:
                    steps = 50
                    delay = item[3] / 50
                elif item[3] < 100000:
                    steps = 500
                    delay = item[3] / 500
                else:
                    print("FadeIn time too big")
                    continue
                steps = int(steps)
                delay = int(delay)
                color = item[4].strip("'")
                if animations_status.get(item[0], 0) == 1:
                    continue
                item[0].place(x=item[1], y=item[2])
                fade_in(item[0], delay, steps, color=color)
            else:
                missing_items = 5 - len(item)
                print(f"{missing_items} variable{' is' if missing_items==1 else 's are'} missing in the list: {item}")
    
    # ERROR
    elif operationcode == 2 or operationcode == 3:
        print('You MUST wait for the other action to be completed!')

# --- --- --- Random phrase selector
random_phrase_data = pandas.read_excel(random_phrase_path)
random_phrase_row = random_phrase_data.sample(n=1).iloc[0]
random_phrase = random_phrase_row['phrase']
random_author = random_phrase_row['author']

# --- --- --- Time & Date reader

def update_time_var(timevar):
    """Aggiorna la variabile con l'ora attuale."""
    current_time = time.strftime("%H:%M:%S")  # Formatta l'ora come HH:MM:SS
    timevar.set(current_time)  # Aggiorna la variabile
    app.after(1000, update_time_var, timevar) 

def update_date_var(datevar):
    """Aggiorna la variabile con la data attuale."""
    current_date = time.strftime("%d-%m-%Y")  # Formatta la data come YYYY-MM-DD
    datevar.set(current_date)  # Aggiorna la variabile
    app.after(1000, update_date_var, datevar)

# --- --- --- Boot sequence

def boot_loading_progress(value=0):
    startup_progress_bar.set(value)
    if value >= 1:
        boot_loading_completed(0)
        value = 1
        return
    elif value < 0.2:
        startup.after(105, boot_loading_progress, value + 0.01)
    elif value >= 0.2 and value < 0.7:
        startup.after(150, boot_loading_progress, value + 0.05)
    elif value >= 0.7:
        startup.after(300, boot_loading_progress, value + 0.10)

def boot_loading_completed(value,counter=0):
    if value==0 and counter<4 :
        startup_progress_completed.place(relx=0.5, rely=0.75, anchor="center")
        startup.after(500, boot_loading_completed, 1, counter+1)
    elif value==1 and counter<4 :
        startup_progress_completed.place_forget()
        startup.after(500, boot_loading_completed, 0, counter+1)
    elif  counter==4:
        ItemManager(Login_LIM_1, 1)
        ItemManager(Login_LIM_2, 3)
        startup.after(2000, ItemManager,Boot_LIM_1, 0)
      
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.init()

def bootsound():
    pygame.mixer.init()
    pygame.mixer.music.load(resource_path("Sounds/BootUp.wav"))
    pygame.mixer.music.play()

def start_bootsound():
    # qui crei e fai partire la thread
    t = threading.Thread(target=bootsound, daemon=True)
    t.start()

def App_Initialization():

    print("############################# Sequenza inizializzazione data")
    
    current_time= datetime.now()

    month= Months_Names_List[current_time.month]

    MonthDownlist.set(month)
    YearDownlist.set(str(current_time.year))

    TableNameGenerator(current_time.year, current_time.month)

    print("############################# Impostati Anno & Mese: ", current_time.year, current_time.month)
    
    if not os.path.exists(Database_phrase_path):  #Verify if database is present. If not it creates it
        conn = sqlite3.connect(Database_phrase_path)
        conn.close()



# --- --- --- Login_Register

def LoginRegister(LROperationCode):

    global User_ID, User_Name, User_Password

    User_Name = login_user_id.get()

    User_Password = login_password_id.get()

    if LROperationCode == 1: #Register

        print ("\nTrying to register an user")

        cursor.execute("SELECT * FROM Users WHERE User_Name = ?", (User_Name,))
        register_result = cursor.fetchone()

        if register_result:
            User_Status_String.set(str("Username already in use"))
            print("\nUsername already in use")
        else:
            while True:
                User_ID = random.randint(1, 999999)
                cursor.execute("SELECT * FROM Users WHERE User_ID = ?", (User_ID,))
                id_result = cursor.fetchone()
                if not id_result:
                    break
            sql_insert = "INSERT INTO Users (User_Name, User_Password, User_ID) VALUES (?, ?, ?)"
            cursor.execute(sql_insert, (User_Name, User_Password, User_ID))
            conn.commit()
            User_Status_String.set(str("User registered"))
            print("\nUser: ", User_Name," reguistered with ID: ", User_ID)

    if LROperationCode == 2: #Login
        print ("\nTrying to login an user")

        cursor.execute("SELECT * FROM Users WHERE User_Name = ? AND User_Password = ?",(User_Name, User_Password))
        login_result = cursor.fetchone()
        if login_result:
            User_Name_String.set(login_user_id.get())
            cursor.execute("SELECT User_ID FROM Users WHERE User_Name = ?", (User_Name,))
            result  = cursor.fetchone()
            User_ID = result[0]
            User_Status_String.set(str("Access granted"))
            print("\nAccess granted to user:", User_Name, " User_ID: ", User_ID,)
            ItemManager(Main_Page_LIM_1, 1)
            ItemManager(Main_Page_LIM_2, 3)
            ItemManager(Calendar_LIM_1, 1)
            TableNameGenerator(None, None)
            
            startup.after(2000, ItemManager,Login_LIM_1, 0)
            startup.after(2000, ItemManager,Login_LIM_2, 0)
        else:
            User_Status_String.set(str("Access denied"))
            print("\nAccess denied to user:", User_Name)

# --- --- --- Table_Manager

def NotePresenceDaysListManager(tablenameactual):
    sql_select= f'''SELECT Note from "{tablenameactual}" where type = 1'''
    cursor.execute(sql_select)
    result = cursor.fetchone()

    if not result:
        print("Note presence list in the table: ", tablenameactual, " does not exists. Creating...")
        NotePresenceList=[]
        NotePresenceListJson = json.dumps(NotePresenceList)
        User_ID=191023 #admin
        Day= 0
        Type = 1
        sql_insert = f'''INSERT INTO "{tablenameactual}" (User_ID, Day, Type, Note) VALUES (?, ?, ?, ?)'''
        cursor.execute(sql_insert, (User_ID, Day, Type, NotePresenceListJson,))
        conn.commit()
        print("Note presence list created for the table: ", tablenameactual, ".")

# --- --- --- Table_Name_Generator
Months_Names_List = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"]
Months_Names_Dict = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}

Years_Names_List = ["2025", "2024", "2023", "2022", "2021", "2020","2019", "2018", "2017", "2016", "2015", "2014"]
Years_Names_Dict = {"2025": 2025, "2024": 2024, "2023": 2023, "2022": 2022, "2021": 2021, "2020": 2020, "2019": 2019, "2018": 2018, "2017": 2017, "2016": 2016, "2015":2015, "2014": 2014}

def TableNameGenerator(Date_Offset_1, Date_Offset_2):

    global Date_Offset_1_Internal, Date_Offset_2_Internal, SelectedNoteId

    SelectedNoteId=None

    print(Date_Offset_1, Date_Offset_2)

    if Date_Offset_1 != None and Date_Offset_1 !=Date_Offset_1_Internal:

        Date_Offset_1_Internal = Date_Offset_1

        print("Updated internal memory 1", Date_Offset_1_Internal)


    if Date_Offset_2 != None:

        Date_Offset_2_Internal = Date_Offset_2

        print("Updated internal memory 2", Date_Offset_2_Internal)
 
    offset11= Date_Offset_1_Internal
    offset12= Date_Offset_1_Internal
    offset13= Date_Offset_1_Internal  

    offset21= Date_Offset_2_Internal-1
    offset22= Date_Offset_2_Internal
    offset23= Date_Offset_2_Internal+1

    offset21= offset22-1

    if offset21 <= 0:
        offset21= 12+offset21
        offset11= offset11-1
    
    offset23 = offset22+1

    if offset23 > 12:

        offset21= offset23-12
        offset13= offset13+1

    Previous_Year= offset11
    Previous_Month= offset21
    tablenameprev= str(Previous_Year)+str(Previous_Month)

    Current_Year= offset12
    Current_Month= offset22
    tablenameactual= str(Current_Year)+str(Current_Month)

    Next_Year= offset13
    Next_Month= offset23
    tablenamenext= str(Next_Year)+str(Next_Month)

    name1= Months_Names_List[(Current_Month-1)]
    MonthDownlist.set(name1)

    print(Current_Year, Current_Month)

    VerifyTablesExistence(tablenameprev, tablenameactual, tablenamenext)
    Generate_Calendar(tablenameprev, tablenameactual, tablenamenext, Previous_Year, Previous_Month, Current_Year, Current_Month, Next_Year, Next_Month)

def MonthDownlistCommand(choice):

    temp=Months_Names_Dict[choice]

    MonthDownlist.set(choice)

    TableNameGenerator(None, temp)

def YearDownlistCommand(choice):

    temp=Years_Names_Dict[choice]

    YearDownlist.set(choice)

    TableNameGenerator(temp, None)

# --- --- --- Note verify presence 

def Generate_Calendar(tablenameprev, tablenameactual, tablenamenext, Previous_Year, Previous_Month, Current_Year, Current_Month, Next_Year, Next_Month):
    global Calendar_LIM_1
    ItemManager(Calendar_LIM_1, 0)
    Calendar_LIM_1.clear()
    Calendar_LIM_1.extend([[Calendar_Page_Background, 305, 110],
                           [YearDownlist, 320, 125],
                           [MonthDownlist, 565, 125],
                           [Calendar_Monday_Label, 320, 213],
                           [Calendar_Tuesday_Label, 548, 213],
                           [Calendar_Wednesday_Label, 776, 213],
                           [Calendar_Thursday_Label, 1004, 213],
                           [Calendar_Friday_Label, 1232, 213],
                           [Calendar_Saturday_Label, 1460, 213],
                           [Calendar_Sunday_Label, 1688, 213]])

    width=213
    height=121

    Days_Range_In_Prev_Month=monthrange(Previous_Year,  Previous_Month)
    Days_Range_In_Actual_Month=monthrange(Current_Year,  Current_Month)


    cursor.execute(f'''SELECT Note from "{tablenameactual}" where type = 1''')
    result = cursor.fetchone()
    if result:
        NotePresenceDaysList=json.loads(result[0])

    for i in range(1, 43):

        if i <= 7:

            if i <= Days_Range_In_Actual_Month[0]:
                Day=(Days_Range_In_Prev_Month[1]-(Days_Range_In_Actual_Month[0]-i))
            elif i >= Days_Range_In_Actual_Month[0] and i <= (Days_Range_In_Actual_Month[0]+Days_Range_In_Actual_Month[1]):
                Day=((i-Days_Range_In_Actual_Month[0]))
            else:
                Day=(i - (Days_Range_In_Actual_Month[0] + Days_Range_In_Actual_Month[1]))                      

            Xcoordinates=int((i-1)*width + i*15)
            Ycoordinates=int(15 + 1*(height+15))

        elif i > 7 and i <= 14:

            if i <= Days_Range_In_Actual_Month[0]:
                Day=(Days_Range_In_Prev_Month[1]-(Days_Range_In_Actual_Month[0]-i))
            elif i >= Days_Range_In_Actual_Month[0] and i <= (Days_Range_In_Actual_Month[0]+Days_Range_In_Actual_Month[1]):
                Day=((i-Days_Range_In_Actual_Month[0]))
            else:
                Day=(i - (Days_Range_In_Actual_Month[0] + Days_Range_In_Actual_Month[1]))                            

            Xcoordinates=int((i-8)*width + (i-7)*15)
            Ycoordinates=int(15 + 2*(height+15))

        elif i > 14 and i <= 21:

            if i <= Days_Range_In_Actual_Month[0]:
                Day=(Days_Range_In_Prev_Month[1]-(Days_Range_In_Actual_Month[0]-i))
            elif i >= Days_Range_In_Actual_Month[0] and i <= (Days_Range_In_Actual_Month[0]+Days_Range_In_Actual_Month[1]):
                Day=((i-Days_Range_In_Actual_Month[0]))
            else:
                Day=(i - (Days_Range_In_Actual_Month[0] + Days_Range_In_Actual_Month[1]))                

            Xcoordinates=int((i-15)*width + (i-14)*15)
            Ycoordinates=int(15 + 3*(height+15))

        elif i > 21 and i <= 28:

            if i <= Days_Range_In_Actual_Month[0]:
                Day=(Days_Range_In_Prev_Month[1]-(Days_Range_In_Actual_Month[0]-i))
            elif i >= Days_Range_In_Actual_Month[0] and i <= (Days_Range_In_Actual_Month[0]+Days_Range_In_Actual_Month[1]):
                Day=((i-Days_Range_In_Actual_Month[0]))
            else:
                Day=(i - (Days_Range_In_Actual_Month[0] + Days_Range_In_Actual_Month[1]))                 

            Xcoordinates=int((i-22)*width + (i-21)*15)
            Ycoordinates=int(15 + 4*(height+15))

        elif i > 28 and i <= 35:

            if i <= Days_Range_In_Actual_Month[0]:
                Day=(Days_Range_In_Prev_Month[1]-(Days_Range_In_Actual_Month[0]-i))
            elif i >= Days_Range_In_Actual_Month[0] and i <= (Days_Range_In_Actual_Month[0]+Days_Range_In_Actual_Month[1]):
                Day=((i-Days_Range_In_Actual_Month[0]))
            else:
                Day=(i - (Days_Range_In_Actual_Month[0] + Days_Range_In_Actual_Month[1]))                 

            Xcoordinates=int((i-29)*width + (i-28)*15)
            Ycoordinates=int(15 + 5*(height+15))

        elif i > 35 and i <= 42:

            if i <= Days_Range_In_Actual_Month[0]:
                Day=(Days_Range_In_Prev_Month[1]-(Days_Range_In_Actual_Month[0]-i))
            elif i >= Days_Range_In_Actual_Month[0] and i <= (Days_Range_In_Actual_Month[0]+Days_Range_In_Actual_Month[1]):
                Day=((i-Days_Range_In_Actual_Month[0]))
            else:
                Day=(i - (Days_Range_In_Actual_Month[0] + Days_Range_In_Actual_Month[1]))                

            Xcoordinates=int((i-36)*width + (i-35)*15)
            Ycoordinates=int(15 + 6*(height+15))

        elif i > 42:

            if i <= Days_Range_In_Actual_Month[0]:
                Day=(Days_Range_In_Prev_Month[1]-(Days_Range_In_Actual_Month[0]-i))
            elif i >= Days_Range_In_Actual_Month[0] and i <= (Days_Range_In_Actual_Month[0]+Days_Range_In_Actual_Month[1]):
                Day=((i-Days_Range_In_Actual_Month[0]))
            else:
                Day=(i - (Days_Range_In_Actual_Month[0] + Days_Range_In_Actual_Month[1]))                    

            Xcoordinates=int((i-43)*width + (i-42)*15)
            Ycoordinates=int(15 + 7*(height+15))

        Xcoordinates=Xcoordinates + 305
        Ycoordinates=Ycoordinates + 110
        if (i-Days_Range_In_Actual_Month[0]) in NotePresenceDaysList: #i is inside the list of the days with a note attatched. Querys the note of that day

            cursor.execute(f'''SELECT Note from "{tablenameactual}" where User_ID = ? and type = 2 and day = ?''', (User_ID, (i-Days_Range_In_Actual_Month[0]),))
            result = cursor.fetchone()
            if result:
                print(result)
                NotePresence_Text=(result[0][:26])
                if NotePresence_Text == "":
                    Color1= '#D3A8A1'
                    Note_Var_String= Day 
                    Note_Data_Type=1
                Color1= '#fc51ae'
                Note_Var_String= NotePresence_Text + "..."
                Note_Data_Type=2
                print("Note:", NotePresence_Text," |--> sent to display.")
            else:
                Color1= '#D3A8A1'
                Note_Var_String= Day 
                Note_Data_Type=1
        elif i <= Days_Range_In_Actual_Month[0] or i > (Days_Range_In_Actual_Month[0]+Days_Range_In_Actual_Month[1]):  #days out of the month range
            Color1= '#c9c9c9'
            Note_Var_String= Day
            Note_Data_Type=1
        else:  #days inside of the month range without note
            Color1= '#D3A8A1'
            Note_Var_String= Day 
            Note_Data_Type=1
            
        CalendarCellButton( Xcoordinates, Ycoordinates, Note_Var_String, Note_Data_Type, Color1, Day, tablenameactual, NotePresenceDaysList )

    ItemManager(Calendar_LIM_1, 1)

class CalendarCellButton(customtkinter.CTkButton):
    def __init__(self, x, y, Note_Var_String, Note_Data_Type, Color, Day, tablenameactual, NotePresenceDaysList):
        global Calendar_LIM_1

        self.Day = Day
        self.tablenameactual = tablenameactual
        self.NotePresenceDaysList = NotePresenceDaysList

        if Note_Data_Type == 1:
            super().__init__(master=main_frame,
                             width=213,
                             height=121,
                             corner_radius=20,
                             text= Note_Var_String,
                             font=("arial", 50),
                             text_color="#14162c",
                             bg_color="#f3e0ed",
                             fg_color=Color,
                             hover_color="#ca418b",
                             command= lambda: (Open_NoteBook_Entry_Page(self.Day, tablenameactual)))
        elif Note_Data_Type == 2:
            super().__init__(master=main_frame,
                             width=213,
                             height=121,
                             corner_radius=20,
                             text= Note_Var_String,
                             font=("arial", 25),
                             text_color="#14162c",
                             bg_color="#f3e0ed",
                             fg_color=Color,
                             hover_color="#ca418b",
                             command= lambda: (List_Notes(self.Day, self.tablenameactual, self.NotePresenceDaysList)))
            self._text_label.configure(wraplength=183, justify="center") 

        pywinstyles.set_opacity(self, color="#f3e0ed")
        Calendar_LIM_1.append([self, x, y])

# --- --- --- Open day

def Open_NoteBook_Entry_Page(Day, tablenameactual):
    global Notebook_List_LIM_2
    if Day != 0:

        NoteBook_Entry_Page.delete(0.0, 'end')
        ItemManager(Notebook_List_LIM_2, 0)
        Notebook_List_LIM_2.clear()
        Notebook_List_LIM_2= Note_Right_Bar_LIM_1.copy()
        SaveNewNote(Day, tablenameactual)
        ItemManager(Notebook_List_LIM_2, 1)
        ItemManager(Note_Entry_LIM_1, 1)
        ItemManager(Calendar_LIM_1, 0)
    
    else:
        print("!!! Error: NO DAY WAS LINKED TO THIS DAY")

def List_Notes(Day, tablenameactual, NotePresenceDaysList):
    global Notebook_List_LIM_1, Notebook_List_LIM_2, Calendar_LIM_1

    NoteBook_Entry_Page.delete(0.0, 'end')

    if Day != 0:

        Notebook_List_LIM_1.clear()
        Notebook_List_LIM_1.extend([[NoteBook_List, 305, 110],
                                    [Right_Bar_Background, 1605, 110],
                                    [Right_Bar, 1605, 110]])
        if Day in NotePresenceDaysList:
            cursor.execute(f'''SELECT Note, Note_Id from "{tablenameactual}" where type = 2 and day = ?''', (Day,))
            result=cursor.fetchall()
            counter=0
            for i in result:
                
                if str(i[0]) =="":
                    continue

                counter= counter + 1

                if counter == 1:
                    height= 30
                elif counter > 1:
                    height= height + Notebook_List_LIM_1[-1][0].winfo_height() + 30

                print("counter:", counter, " | ", Notebook_List_LIM_1[-1][0].winfo_height(), " + ", 30*(counter), " = ", height)

                DayNoteListButton( 30, height, str(i[0]), i[1], tablenameactual, Day)
    
        ItemManager(Notebook_List_LIM_2, 0)
        Notebook_List_LIM_2.clear()
        AddAnotherNote(Day, tablenameactual)
        ItemManager(Notebook_List_LIM_2, 1)
        ItemManager(Notebook_List_LIM_1, 1)
        ItemManager(Calendar_LIM_1, 0)

    else:
            print("!!! Error: NO DAY WAS LINKED TO THIS DAY")

def Set_PreExsisting_Text(SelectedNoteId, tablenameactual):
    global Notebook_List_LIM_2

    NoteBook_Entry_Page.delete(0.0, 'end')

    cursor.execute(f'''SELECT Note from "{tablenameactual}" where type = 2 and Note_Id = ?''', (SelectedNoteId,))
    result=cursor.fetchall()
    NoteText=result[0][0]
    NoteBook_Entry_Page.insert("1.0", NoteText)
    ItemManager(Notebook_List_LIM_2, 0)
    Notebook_List_LIM_2.clear
    Notebook_List_LIM_2= Note_Right_Bar_LIM_1.copy()
    SaveNoteEdits(SelectedNoteId, tablenameactual)
    ItemManager(Notebook_List_LIM_2, 1)
    ItemManager(Note_Entry_LIM_1, 1)
    ItemManager(Calendar_LIM_1, 0)

class DayNoteListButton(customtkinter.CTkButton):
    def __init__(self, x, y, Note_Var_String, NoteId, tablenameactual, Day):
        global Notebook_List_LIM_1
        print(y)
        super().__init__(master=NoteBook_List,
                         width=10,
                         height=10,
                         bg_color="#F3E0EC",
                         fg_color="#b993cf",
                         hover_color="#ca418b",
                         text=Note_Var_String,
                         font=("arial", 25),
                         text_color="#14162c",
                         command= lambda: (Show_Selection(x, y, self.winfo_width(), self.winfo_height(), NoteId, tablenameactual, Day)))
        self.update()
        self._text_label.configure(wraplength=1225, justify="left")
        self.place(x=x, y=y)
        pywinstyles.set_opacity(self, value= 0.8, color="#F3E0EC")
        templist=[]
        templist.append(self)
        templist.append(x)
        templist.append(y)
        Notebook_List_LIM_1.append(templist)
        self.update()

def Show_Selection(x, y, width, height, NoteId, tablenameactual, Day):
    global Notebook_List_LIM_2, SelectedNoteId
    print(Notebook_List_LIM_2)
    if SelectedNoteId == NoteId:
        ItemManager(Notebook_List_LIM_2, 0)
        Notebook_List_LIM_2.clear()
        AddAnotherNote(Day, tablenameactual)
        ItemManager(Notebook_List_LIM_2, 1)
        SelectedNoteId= None
    else:
        SelectedNoteId = NoteId
        ItemManager(Notebook_List_LIM_2, 0)
        Notebook_List_LIM_2.clear()
        DayNoteListSelected(x, y, width, height)
        NoteEditButton(SelectedNoteId, tablenameactual)
        NoteDeleteButton(SelectedNoteId, tablenameactual)
        ItemManager(Notebook_List_LIM_2, 1)

class DayNoteListSelected(customtkinter.CTkFrame):
    def __init__(self, x, y, width, heihgt):
        global Notebook_List_LIM_2
        width=width+20
        heihgt=heihgt+20
        x=x-10
        y=y-10
        super().__init__(master=NoteBook_List, width=width, height=heihgt, corner_radius = 10, border_width= 2, bg_color='#F3E0EC', fg_color='#F3E0EC', border_color='#ffb5c3')
        self.place(x=x, y=y)
        pywinstyles.set_opacity(self, color="#F3E0EC")
        templist=[]
        templist.append(self)
        templist.append(x)
        templist.append(y)
        Notebook_List_LIM_2.append(templist)

# --- --- --- Note Save - Delete Button

class SaveNewNote(customtkinter.CTkButton):
    def __init__(self, Day, tablenameactual):
        global Notebook_List_LIM_2      
        super().__init__(master=Right_Bar_Background,
                         text="",
                         bg_color="#f3e0ed",
                         fg_color="#f3e0ed",
                         hover_color="#f3e0ed",
                         image=customtkinter.CTkImage(Image.open('Images/Save.PNG'),size=(150,150)),
                         command= lambda: (Save_Note(Day, tablenameactual)))                                                                                                                                      
        x=82.5
        y=15
        self.place(x=x, y=y)
        templist=[]
        templist.append(self)
        templist.append(x)
        templist.append(y)
        Notebook_List_LIM_2.append(templist)

class AddAnotherNote(customtkinter.CTkButton):
    def __init__(self, Day, tablenameactual):
        global Notebook_List_LIM_2      
        super().__init__(master=Right_Bar_Background,
                         text="",
                         bg_color="#f3e0ed",
                         fg_color="#f3e0ed",
                         hover_color="#f3e0ed",
                         image=customtkinter.CTkImage(Image.open('Images/Add_Note.PNG'),size=(150,150)),
                         command= lambda: (Open_NoteBook_Entry_Page(Day, tablenameactual)))                                                                                                                                      
        x=82.5
        y=15
        self.place(x=x, y=y)
        pywinstyles.set_opacity(self, value= 1, color="#f3e0ed")
        templist=[]
        templist.append(self)
        templist.append(x)
        templist.append(y)
        Notebook_List_LIM_2.append(templist)

class SaveNoteEdits(customtkinter.CTkButton):
    def __init__(self, SelectedNoteId, tablenameactual):
        global Notebook_List_LIM_2     
        super().__init__(master=Right_Bar_Background,
                         text="",
                         bg_color="#f3e0ed",
                         fg_color="#f3e0ed",
                         hover_color="#f3e0ed",
                         image=customtkinter.CTkImage(Image.open('Images/Save.PNG'),size=(150,150)),
                         command= lambda: (Update_Note(SelectedNoteId, tablenameactual)))                                                                                                                                      
        x=82.5
        y=15
        self.place(x=x, y=y)
        pywinstyles.set_opacity(self, value= 1, color="#f3e0ed")
        templist=[]
        templist.append(self)
        templist.append(x)
        templist.append(y)
        Notebook_List_LIM_2.append(templist)

class NoteEditButton(customtkinter.CTkButton):
    def __init__(self, SelectedNoteId, tablenameactual):
        global Notebook_List_LIM_2      
        super().__init__(master=Right_Bar_Background,
                         text="",
                         bg_color="#f3e0ed",
                         fg_color="#f3e0ed",
                         hover_color="#f3e0ed",
                         image=customtkinter.CTkImage(Image.open('Images/Edit.PNG'),size=(150,150)),
                         command= lambda: (Set_PreExsisting_Text(SelectedNoteId, tablenameactual)))                                                                                                                                      
        x=82.5
        y=15
        self.place(x=x, y=y)
        pywinstyles.set_opacity(self, value= 1, color="#f3e0ed")
        templist=[]
        templist.append(self)
        templist.append(x)
        templist.append(y)
        Notebook_List_LIM_2.append(templist)

class NoteDeleteButton(customtkinter.CTkButton):
    def __init__(self, SelectedNoteId, tablenameactual):
        global Notebook_List_LIM_2
        super().__init__(master=Right_Bar_Background,
                         text="",
                         bg_color="#f3e0ed",
                         fg_color="#f3e0ed",
                         hover_color="#f3e0ed",
                         image=customtkinter.CTkImage(Image.open('Images/Delete.PNG'),size=(150,150)),
                         command= lambda: (Delete_Note(SelectedNoteId, tablenameactual)))                                                                                                                                      
        x=82.5
        y=180
        self.place(x=x, y=y)
        pywinstyles.set_opacity(self, value= 1, color="#f3e0ed")
        templist=[]  
        templist.append(self)
        templist.append(x)
        templist.append(y)
        Notebook_List_LIM_2.append(templist)

# --- --- --- NoteManager

def Save_Note(Day, tablenameactual):
    global User_ID, NoteBook_Entry_Page

    sql_select= f'''SELECT Note from "{tablenameactual}" where type = 1'''
    cursor.execute(sql_select,)
    result = cursor.fetchone()
    NotePresenceDaysList=json.loads(result[0])

    NotePresenceDaysList.append(Day)
    NotePresenceDaysListJson = json.dumps(NotePresenceDaysList)
    sql_update= f'''UPDATE "{tablenameactual}" Set Note = ? WHERE Type = 1'''
    cursor.execute(sql_update, (NotePresenceDaysListJson,))

    print("Adding a note for the user: ",User_ID, ".")
    User_ID=int(User_ID)
    Notetext = NoteBook_Entry_Page.get("1.0", "end-1c")
    sql_insert = f'''INSERT INTO "{tablenameactual}" (User_ID, Day, Type, Note) VALUES (?, ?, ?, ?)'''
    cursor.execute(sql_insert, (User_ID, Day, 2, Notetext,))
    conn.commit()

    print("Added a note connected to the user: ",User_ID, ".")

def Update_Note(SelectedNoteId, tablenameactual):
    global User_ID, NoteBook_Entry_Page
    Notetext = NoteBook_Entry_Page.get("1.0", "end-1c")
    sql_update= f'''UPDATE "{tablenameactual}" SET Note = ? WHERE Note_Id = ?'''
    cursor.execute(sql_update, (Notetext, SelectedNoteId))
    conn.commit()
    print("Updated note N.: ", SelectedNoteId, " connected to the user: ", User_ID, ".")

def Delete_Note(SelectedNoteId, tablenameactual):
    global User_ID, NoteBook_Entry_Page
    sql_delete= f'''DELETE FROM "{tablenameactual}" where Note_Id = ?'''
    cursor.execute(sql_delete, (SelectedNoteId,))    
    conn.commit()
    ItemManager(Notebook_List_LIM_1, 0)   
    ItemManager(Notebook_List_LIM_2, 0)
    List_Notes(0)
    Generate_Calendar()
    ItemManager(Calendar_LIM_1, 1)
    print("Removed note N.: ", SelectedNoteId, " connected to the user: ", User_ID, ".")

# --- --- --- --- --- --- Database management --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- -

# --- --- --- Connect to database
conn = sqlite3.connect(resource_path('Data/Database.db'))
cursor= conn.cursor()

# --- --- --- Verify if all the tables needed exists. If not it creates them

def VerifyTablesExistence(tablenameprev, tablenameactual, tablenamenext):

    #--- --- Users
    sql_create= '''
    CREATE TABLE IF NOT EXISTS Users(
    User_Name VARCHAR(30) NOT NULL,
    User_Password CHAR(20) NOT NULL,
    User_ID INT
    )
    '''
    cursor.execute(sql_create)

    #--- --- Notes

    sql_create= f'''CREATE TABLE IF NOT EXISTS "{tablenameprev}"(
                    User_ID INT NOT NULL,
                    Day NOT NULL,
                    Note_Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Type INT NOT NULL,
                    Note TEXT NOT NULL)
                '''
    cursor.execute(sql_create)

    sql_create= f'''CREATE TABLE IF NOT EXISTS "{tablenameactual}"(
                    User_ID INT NOT NULL,
                    Day NOT NULL,
                    Note_Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Type INT NOT NULL,
                    Note TEXT NOT NULL)
                '''
    cursor.execute(sql_create)

    sql_create= f'''CREATE TABLE IF NOT EXISTS "{tablenamenext}"(
                    User_ID INT NOT NULL,
                    Day NOT NULL,
                    Note_Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Type INT NOT NULL,
                    Note TEXT NOT NULL)
                '''
    cursor.execute(sql_create)

    NotePresenceDaysListManager(tablenameactual)  #Creates the row with the presence of notes for that specific table

    #--- --- Save changes
    conn.commit()

# --- --- --- --- --- --- GUI --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- -

# --- --- --- Boot page
startup = customtkinter.CTkFrame(master=app, #background for the Bootup page
                                   width=1920, 
                                   height=1080,
                                   bg_color="black",
                                   fg_color="black")
startup.place(relx=0.5, rely=0.5, anchor="center")

startup_logo = customtkinter.CTkLabel(master=startup,
                                      text="", #logo for the Bootup page
                                      image=customtkinter.CTkImage(Image.open(resource_path('Images/Logo_GRB_2.PNG')),size=(640,167)))
startup_logo.place(relx=0.5, rely=0.5, anchor="center")

startup_progress_bar = customtkinter.CTkProgressBar(master=startup, 
                                                    width=740,
                                                    progress_color="white")
startup_progress_bar.place(relx=0.5, rely=0.7, anchor="center")

startup_progress_completed = customtkinter.CTkLabel(master=startup,
                                    text="LOADING COMPLETED",
                                    font=("Arial", 30),
                                    bg_color="#000000",
                                    fg_color="#000000",
                                    text_color="#ffffff",)

Boot_LIM_1=[[startup, 960, 540], [startup_logo, 960, 540], [startup_progress_bar, 960, 756], [startup_progress_completed, 960, 810]]

# --- --- --- Login page
Login_Background = customtkinter.CTkLabel(master=app,
                                text="",
                                image=customtkinter.CTkImage(Image.open(resource_path('Images/Login_Wallpaper.PNG')),size=(1920,1080)))

Login_Time_Label = customtkinter.CTkLabel(master=Login_Background,
                                    textvariable=timevar,
                                    font=("Bauhaus 93", 100),
                                    bg_color="#e2c9f1",
                                    fg_color="#e2c9f1",
                                    text_color="#14162c")
pywinstyles.set_opacity(Login_Time_Label, color="#e2c9f1")

phraseframe = customtkinter.CTkFrame(master=Login_Background, # creo il frame per la sfondo di login
                                   width=850, 
                                   height=300,
                                   corner_radius = 30,
                                   bg_color="#f3e0ed",
                                   fg_color="#F3E0EC") 
pywinstyles.set_opacity(phraseframe, value= 0.8, color="#f3e0ed")

phrase_label = customtkinter.CTkLabel(master=Login_Background,
                                      text=random_phrase,
                                      font=("Book Antiqua",50),
                                      wraplength=830,
                                      justify="left",
                                      bg_color="#f3e0ed",
                                      fg_color="#f3e0ed",
                                      text_color="#14162c",)
pywinstyles.set_opacity(phrase_label, color="#f3e0ed")

author_label = customtkinter.CTkLabel(master=Login_Background,
                                      text=random_author,
                                      font=("Book Antiqua", 35),
                                      wraplength=830,
                                      justify="left",
                                      bg_color="#f3e0ed",
                                      fg_color="#f3e0ed",
                                      text_color="#14162c")
pywinstyles.set_opacity(author_label, color="#f3e0ed")

LoginFrame_background = customtkinter.CTkFrame(master=Login_Background, # creo il frame per il box di login
                                   width=800, 
                                   height=900,
                                   corner_radius = 30,
                                   bg_color="#f3e0ed",
                                   fg_color="#F3E0EC")
pywinstyles.set_opacity(LoginFrame_background, value= 0.8, color="#f3e0ed")

Login_Title = customtkinter.CTkLabel(master=Login_Background,
                                    text="Welcome to your personal diary",
                                    font=("Montserrat", 50),
                                    bg_color="#F3E0EC",
                                    fg_color="#F3E0EC",
                                    text_color="#14162c")
pywinstyles.set_opacity(Login_Title, color="#F3E0EC")

Login_Icon = customtkinter.CTkLabel(master=Login_Background,
                                text="",
                                image=customtkinter.CTkImage(Image.open(resource_path('Images/Login_Icon.PNG')),size=(50,50)),
                                bg_color="#F3E0EC",
                                fg_color="#F3E0EC")
pywinstyles.set_opacity(Login_Icon, color="#F3E0EC")

Login_Text = customtkinter.CTkLabel(master=Login_Background,
                                text="Login",
                                font=("Montserrat", 60),
                                bg_color="#F3E0EC",
                                fg_color="#F3E0EC",
                                text_color="#14162c")
pywinstyles.set_opacity(Login_Text, color="#F3E0EC")

login_user_id =  customtkinter.CTkEntry(master=Login_Background,
                                        width=300, 
                                        height=50,
                                        corner_radius=5,
                                        border_width=2,
                                        placeholder_text='Nome utente', 
                                        font=("Montserrat", 20),
                                        bg_color="#F3E0EC",
                                        fg_color="#f3e0eb",
                                        text_color="#14162c",
                                        placeholder_text_color="#14162c")
pywinstyles.set_opacity(login_user_id,color="#F3E0EC")

login_password_id =  customtkinter.CTkEntry(master=Login_Background,
                                        width=300, 
                                        height=50,
                                        corner_radius=5,
                                        border_width=2,
                                        placeholder_text='Password', 
                                        font=("Montserrat", 20),
                                        show="*",
                                        bg_color="#F3E0EC",
                                        fg_color="#f3e0eb",
                                        placeholder_text_color="#14162c",
                                        text_color="#14162c")
pywinstyles.set_opacity(login_password_id,color="#F3E0EC")

Login_button = customtkinter.CTkButton(master=Login_Background,
                                       width=300,
                                       height=50,
                                       corner_radius= 5,
                                       text='Confirm',
                                       font=("Arial", 30),
                                       bg_color="#F3E0EC",
                                       fg_color="#55286F",
                                       command= lambda: LoginRegister(2))
pywinstyles.set_opacity(Login_button,color="#F3E0EC")

Login_Or = customtkinter.CTkLabel(master=Login_Background,
                                text="or",
                                font=("Montserrat", 20),
                                bg_color="#F3E0EC",
                                fg_color="#F3E0EC",
                                text_color="#14162c")
pywinstyles.set_opacity(Login_Or, color="#F3E0EC")

Register_button = customtkinter.CTkButton(master= Login_Background,
                                       width= 300,
                                       height= 50,
                                       corner_radius= 25,
                                       text='Register',
                                       font=("Arial", 30),
                                       bg_color="#F3E0EC",
                                       fg_color="#2b1438",
                                       command= lambda: LoginRegister(1))
pywinstyles.set_opacity(Register_button,color="#F3E0EC")

login_status_label= customtkinter.CTkLabel(master=Login_Background,
                                           width=300, 
                                           height=50,
                                           corner_radius=19,
                                           textvariable= User_Status_String, 
                                           bg_color="#F3E0EC",
                                           fg_color="#F3E0EC",
                                           text_color="#14162c")
pywinstyles.set_opacity(login_status_label,color="#F3E0EC")

Login_LIM_1 = [[Login_Time_Label, 288, 324], [phraseframe, 45, 459], [phrase_label, 60, 464], [author_label, 60, 717], [LoginFrame_background, 1030, 90],[Login_Title, 1074.5, 161.5], [Login_Icon, 1295, 348],
               [Login_Text, 1357.5, 339.5], [login_user_id, 1280, 448], [login_password_id, 1280, 525], [Login_button, 1280, 602], [Login_Or, 1421, 653], [Register_button, 1280, 682],
               [login_status_label, 1280, 722]]
Login_LIM_2 = [[Login_Background, 0, 0, 1000, "'#000000'"]]

# --- --- --- Main page

main_frame = customtkinter.CTkFrame(master=app,
                                    width=1920,
                                    height=1080,
                                    bg_color="#fff58a")

Main_Background = customtkinter.CTkLabel(master=main_frame,
                                         text="",
                                         image=customtkinter.CTkImage(Image.open(resource_path('Images/Login_Wallpaper.PNG')),size=(1920,1080)))

Left_Bar_Frame_Background = customtkinter.CTkFrame(master=main_frame,
                                  width=300,
                                  height=1070,
                                  corner_radius=20,
                                  bg_color="#f3e0ed",
                                  fg_color="#F3E0EC",
                                  background_corner_colors=["#F3E0EC","#f3e0ed","#f3e0ed","#F3E0EC"])
pywinstyles.set_opacity(Left_Bar_Frame_Background, color="#f3e0ed")

User_Icon = customtkinter.CTkFrame(master=main_frame,
                                  width=100,
                                  height=100,
                                  corner_radius=50,
                                  bg_color="#f3e0ed",
                                  fg_color="#ffffff")
pywinstyles.set_opacity(User_Icon, value= 0.8, color="#f3e0ed")

User_Name = customtkinter.CTkLabel(master=main_frame,
                                  width=200,
                                  height=30,
                                  corner_radius=50,
                                  textvariable=User_Name_String,
                                  font=("Montserrat", 20),
                                  bg_color="#f3e0ed",
                                  fg_color="#ffffff",
                                  text_color="#14162c")
pywinstyles.set_opacity(User_Name, color="#f3e0ed")
 
Left_Bar_Menu_1 = customtkinter.CTkButton(master=main_frame,
                                       width=290,
                                       height=50,
                                       corner_radius=25,
                                       text='Calendar',
                                       font=("Arial", 30),
                                       bg_color="#F3E0EC",
                                       fg_color="#55286F",
                                       hover_color="#55286F",
                                       background_corner_colors=["#55286F","#F3E0EC","#F3E0EC","#55286F"],
                                       command= lambda: (ItemManager(Notebook_List_LIM_1, 0), ItemManager(Note_Entry_LIM_1, 0), ItemManager(Notebook_List_LIM_2, 0) , TableNameGenerator(None, None)))
pywinstyles.set_opacity(Left_Bar_Menu_1,color="#F3E0EC")

Top_Bar_Background = customtkinter.CTkFrame(master=main_frame,
                                  width=1610,
                                  height=100,
                                  corner_radius=20,
                                  bg_color="#f3e0ed",
                                  fg_color="#F3E0EC")
pywinstyles.set_opacity(Top_Bar_Background, color="#f3e0ed")

Top_Bar = customtkinter.CTkFrame(master=main_frame,
                                  width=1610,
                                  height=100,
                                  corner_radius=20,
                                  bg_color="#f3e0ed",
                                  fg_color="#f3e0ed")
pywinstyles.set_opacity(Top_Bar, color="#f3e0ed")

Top_Bar_Label = customtkinter.CTkLabel(master=Top_Bar,
                                    height=60,
                                    text="Your personal daily diary",
                                    font=("Bauhaus 93", 60),
                                    bg_color="#e2c9f1",
                                    fg_color="#e2c9f1",
                                    text_color="#14162c"
                                   )
pywinstyles.set_opacity(Top_Bar_Label, color="#e2c9f1")

time_label = customtkinter.CTkLabel(master=Top_Bar,
                                    width=300,
                                    height=60,
                                    textvariable=timevar,
                                    font=("Bauhaus 93", 45),
                                    bg_color="#e2c9f1",
                                    fg_color="#e2c9f1",
                                    text_color="#14162c"
                                   )
pywinstyles.set_opacity(time_label, color="#e2c9f1")

Date_label = customtkinter.CTkLabel(master=Top_Bar,
                                    width=300,
                                    height=40,
                                    textvariable=datevar,
                                    font=("Bauhaus 93", 25),
                                    bg_color="#e2c9f1",
                                    fg_color="#e2c9f1",
                                    text_color="#14162c"
                                   )
pywinstyles.set_opacity(Date_label, color="#e2c9f1")

Main_Page_LIM_1= [[Main_Background, 0, 0], [Left_Bar_Frame_Background, 0, 5],  [User_Icon, 100, 15], [User_Name, 50, 140], [Left_Bar_Menu_1, 0, 185],
                  [Top_Bar_Background, 305,5], [Top_Bar, 305, 5], [Top_Bar_Label, 20, 20], [time_label, 1300,30], [Date_label, 1334,10]]
Main_Page_LIM_2 = [[main_frame, 0, 0, 1000, "'#000000'"]]

# --- --- --- Calendar

Calendar_Page_Background= customtkinter.CTkFrame(master=main_frame,
                                  width=1610,
                                  height=965,
                                  corner_radius=20,
                                  bg_color="#f3e0ed",
                                  fg_color="#F3E0EC")
pywinstyles.set_opacity(Calendar_Page_Background, color="#f3e0ed")

YearDownlist = customtkinter.CTkOptionMenu(master= main_frame, values=Years_Names_List, command= YearDownlistCommand)

MonthDownlist = customtkinter.CTkOptionMenu(master= main_frame, values=Months_Names_List, command= MonthDownlistCommand)

Calendar_Monday_Label= customtkinter.CTkLabel(master= main_frame,
                                    width=213,
                                    height=35,
                                    corner_radius=20,
                                    text="Mon",
                                    font=("Bauhaus 93", 25),
                                    bg_color="#F3E0EC",
                                    fg_color="#b993cf",
                                    text_color="#14162c"
                                   )
pywinstyles.set_opacity(Calendar_Monday_Label, color="#F3E0EC")

Calendar_Tuesday_Label= customtkinter.CTkLabel(master= main_frame,
                                    width=213,
                                    height=35,
                                    corner_radius=20,
                                    text="Tue",
                                    font=("Bauhaus 93", 25),
                                    bg_color="#F3E0EC",
                                    fg_color="#b993cf",
                                    text_color="#14162c"
                                   )
pywinstyles.set_opacity(Calendar_Tuesday_Label, color="#F3E0EC")

Calendar_Wednesday_Label = customtkinter.CTkLabel(master=main_frame,
                                                  width=213,
                                                  height=35,
                                                  corner_radius=20,
                                                  text="Wed",
                                                  font=("Bauhaus 93", 25),
                                                  bg_color="#F3E0EC",
                                                  fg_color="#b993cf",
                                                  text_color="#14162c")
pywinstyles.set_opacity(Calendar_Wednesday_Label, color="#F3E0EC")

Calendar_Thursday_Label = customtkinter.CTkLabel(master=main_frame,
                                                  width=213,
                                                  height=35,
                                                  corner_radius=20,
                                                  text="Thu",
                                                  font=("Bauhaus 93", 25),
                                                  bg_color="#F3E0EC",
                                                  fg_color="#b993cf",
                                                  text_color="#14162c")
pywinstyles.set_opacity(Calendar_Thursday_Label, color="#F3E0EC")

Calendar_Friday_Label = customtkinter.CTkLabel(master=main_frame,
                                                  width=213,
                                                  height=35,
                                                  corner_radius=20,
                                                  text="Fri",
                                                  font=("Bauhaus 93", 25),
                                                  bg_color="#F3E0EC",
                                                  fg_color="#b993cf",
                                                  text_color="#14162c")
pywinstyles.set_opacity(Calendar_Friday_Label, color="#F3E0EC")

Calendar_Saturday_Label = customtkinter.CTkLabel(master=main_frame,
                                                  width=213,
                                                  height=35,
                                                  corner_radius=20,
                                                  text="Sat",
                                                  font=("Bauhaus 93", 25),
                                                  bg_color="#F3E0EC",
                                                  fg_color="#b993cf",
                                                  text_color="#14162c")
pywinstyles.set_opacity(Calendar_Saturday_Label, color="#F3E0EC")

Calendar_Sunday_Label = customtkinter.CTkLabel(master=main_frame,
                                                  width=213,
                                                  height=35,
                                                  corner_radius=20,
                                                  text="Sun",
                                                  font=("Bauhaus 93", 25),
                                                  bg_color="#F3E0EC",
                                                  fg_color="#b993cf",
                                                  text_color="#14162c")
pywinstyles.set_opacity(Calendar_Sunday_Label, color="#F3E0EC")

Calendar_LIM_1=[[Calendar_Page_Background, 305, 110], [YearDownlist, 320, 125], [MonthDownlist, 565, 125],
                [Calendar_Monday_Label, 320, 213], [Calendar_Tuesday_Label, 548, 213], [Calendar_Wednesday_Label, 776, 213], [Calendar_Thursday_Label, 1004, 213],
                [Calendar_Friday_Label, 1232, 213], [Calendar_Saturday_Label, 1460, 213], [Calendar_Sunday_Label, 1688, 213]]

# --- --- --- Notebook

# --- Notebook Right bat

Right_Bar_Background = customtkinter.CTkFrame(master=main_frame,
                                  width=315,
                                  height=965,
                                  corner_radius=20,
                                  bg_color="#f3e0ed",
                                  fg_color="#F3E0EC")
pywinstyles.set_opacity(Right_Bar_Background, color="#f3e0ed")

Right_Bar = customtkinter.CTkFrame(master=main_frame,
                                  width=315,
                                  height=965,
                                  corner_radius=20,
                                  bg_color="#f3e0ed",
                                  fg_color="#f3e0ed")
pywinstyles.set_opacity(Right_Bar, color="#f3e0ed")

Note_Right_Bar_LIM_1=[[Right_Bar_Background, 1605, 110], [Right_Bar, 1605, 110]]

# --- Note list
NoteBook_List= customtkinter.CTkFrame(master=main_frame,
                                        width=1295,
                                        height=965,
                                        corner_radius=20,
                                        border_width=0,
                                        bg_color="#F3E0EC",
                                        fg_color="#f3e0eb")
pywinstyles.set_opacity(NoteBook_List, color="#F3E0EC")
Notebook_List_LIM_1=[[NoteBook_List, 305, 110], [Right_Bar_Background, 1605, 110], [Right_Bar, 1605, 110]]

# --- Notebook entry text
NoteBook_Entry_Page=  customtkinter.CTkTextbox(master=main_frame, 
                                        width=1295,
                                        height=965,
                                        corner_radius=20,
                                        border_width=0, 
                                        font=("Montserrat", 20),
                                        wrap="word",
                                        bg_color="#F3E0EC",
                                        fg_color="#f3e0eb",
                                        text_color="#14162c")
pywinstyles.set_opacity(NoteBook_Entry_Page,color="#F3E0EC")

Note_Entry_LIM_1=[[NoteBook_Entry_Page, 305, 110]]

App_Initialization()
update_time_var(timevar)
update_date_var(datevar)
app.after(500, start_bootsound)
boot_loading_progress()
app.mainloop()