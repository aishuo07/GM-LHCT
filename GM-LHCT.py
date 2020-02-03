from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import hashlib
import json
from datetime import datetime
import pandas as pd
import sqlite3
import re
import gmplot
import webbrowser
import os

conn = sqlite3.connect('database.db')
c = conn.cursor()


class FileButton:
    def __init__(self, window, path):
        self.window = window
        self.path = path
        self.frame = Frame(window.get_files_frame(), bg='#282828', bd=1)
        self.path_label = Label(self.frame, text=path, bg='#282828', fg='#FFFFFF', padx=10, pady=10)
        self.remove_button = Button(self.frame, text='Remove', command=self.remove, bg='#EE0000', fg='#FFFFFF',
                                    relief=FLAT, padx=10, pady=10)
        self.path_label.pack(side=LEFT)
        self.remove_button.pack(side=RIGHT)

    def get_frame(self):
        return self.frame

    def remove(self):
        self.window.remove_file(self.path)


class BrowseFiles:
    def __init__(self, window):
        self.window = window
        self.nex = None
        self.files = list()
        self.file_buttons = list()
        self.frame = Frame(window, bg='#1F1F1F')
        self.files_frame = Frame(self.frame, bg='#2F2F2F')
        Label(self.frame, text='Files', bg='#1F1F1F', fg='#FFFFFF').pack(side=TOP)
        button_frame = Frame(self.frame)
        add_button = Button(button_frame, command=self.add_file, text="Browse", relief=FLAT, bg='#2F2F2F', fg='#FFFFFF',
                            pady=10, padx=10)
        next_button = Button(button_frame, command=self.get_info, text="Next", relief=FLAT, bg='#0088DD', fg='#FFFFFF',
                             pady=10, padx=10)
        add_button.pack(side=LEFT, fill=X, expand=True)
        next_button.pack(side=RIGHT, fill=X, expand=True)
        button_frame.pack(side=BOTTOM, fill=X, anchor=S)
        self.files_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def get_info(self):
        if len(self.files) < 2:
            popup_msg("Minimum 2 files should be selected")
            return

        self.frame.pack_forget()

        if self.nex is not None:
            if self.nex.get_files() == self.files:
                pack(self.nex)
                return

        loading = start_loading('Loading...')
        self.window.update()
        view_details = ViewDetails(self.window, self, list.copy(self.files))
        self.nex = view_details
        pack(view_details)
        stop_loading(loading)

    def add_file(self):
        if len(self.files) == 6:
            popup_msg("Maximum six files allowed!")
        filename = filedialog.askopenfilename()
        if filename != "":
            if filename[::-1][:5] != 'nosj.':
                popup_msg("Select a valid JSON file")
                return
            if filename in self.files:
                popup_msg("File already added")
                return
            self.files.append(filename)
            self.refresh_files()

    def remove_file(self, path):
        self.files.remove(path)
        self.refresh_files()

    def refresh_files(self):
        for x in self.file_buttons:
            x.get_frame().pack_forget()
        self.file_buttons = list()
        for x in self.files:
            self.file_buttons.append(FileButton(self, x))
            self.file_buttons[-1].get_frame().pack(anchor=N, fill=X)

    def get_files_frame(self):
        return self.files_frame

    def get_frame(self):
        return self.frame


class Artifact:
    def __init__(self, file_name, window):
        self.window = window
        self.file_name = file_name
        self.latitude = list()
        self.longitude = list()
        self.time = list()
        self.date = list()
        self._read_file()
        self._parse_file()
        self._data_into_db()

    def _read_file(self):
        json_data = open(self.file_name, "rb").read()
        self.hash = hashlib.md5(json_data).hexdigest()
        self.json_obj = json.loads(json_data)

    def _parse_file(self):
        e = 10 ** 7
        data = ['---', '---', '---', '---']
        for values in self.json_obj.values():
            for j in range(len(values)):
                for key in values[j].keys():
                    if key == 'latitudeE7':
                        data[0] = values[j][key] / e
                        self.latitude.append(data[0])
                    if key == 'longitudeE7':
                        data[1] = values[j][key] / e
                        self.longitude.append(data[1])
                    if key == 'timestampMs':
                        date_time = str(datetime.fromtimestamp(int(values[j][key][0:-3])))
                        data[2] = date_time[11:16]
                        data[3] = date_time[0:10]
                        self.time.append(data[2])
                        self.date.append(data[3])

    def update_artifact(self, new_table):
        self.latitude = list()
        self.longitude = list()
        self.date = list()
        self.time = list()
        for group in new_table:
            for row in group:
                self.latitude.append(row[0])
                self.longitude.append(row[1])
                self.date.append(row[2])
                self.time.append(row[3])
            self.latitude.append(' ')
            self.longitude.append(' ')
            self.date.append(' ')
            self.time.append(' ')
        self.scrollbary.pack_forget()
        self.tree.pack_forget()
        self.create_frame()


    def data_to_csv(self, path):
        data = {
            'Latitude': self.latitude,
            'Longitude': self.longitude,
            'Date': self.date,
            'Time': self.time
        }
        data_frame = pd.DataFrame(data)
        data_frame.to_csv(f"{path}.csv", index=True)

    def _data_into_db(self):
        data = {
            'Latitude': self.latitude,
            'Longitude': self.longitude,
            'Date': self.date,
            'Time': self.time
        }
        data_frame = pd.DataFrame(data)
        data_frame.to_sql('t' + self.hash, conn, if_exists='replace', index=False)

    def create_frame(self):
        self.scrollbary = Scrollbar(self.window, orient=VERTICAL, )
        self.tree = ttk.Treeview(self.window, columns=("Latitude", "Longitude", "Date", "Time"), selectmode="extended",
                            height=14, yscrollcommand=self.scrollbary.set)
        self.scrollbary.config(command=self.tree.yview)
        self.scrollbary.pack(side=RIGHT, fill=Y)
        self.tree.heading('Latitude', text="Latitude", anchor=W)
        self.tree.heading('Longitude', text="Longitude", anchor=W)
        self.tree.heading('Date', text="Date", anchor=W)
        self.tree.heading('Time', text="Time", anchor=W)
        self.tree.column('#0', stretch=NO, minwidth=0, width=25)
        self.tree.column('#1', stretch=NO, minwidth=0, width=100)
        self.tree.column('#2', stretch=NO, minwidth=0, width=100)
        self.tree.column('#3', stretch=NO, minwidth=0, width=100)
        self.tree.column('#4', stretch=NO, minwidth=0, width=100)
        self.tree.pack()
        for i in range(len(self.latitude)):
            self.tree.insert("", 0, values=(self.latitude[i], self.longitude[i], self.date[i], self.time[i]))


class Table:
    def __init__(self, window, file_name, usernum):
        self.frame = LabelFrame(window, text=f'User : {usernum} - {file_name}')
        self.frame.pack(side=LEFT, padx=5, pady=5)
        self.file_name = file_name
        self.artifact = Artifact(self.file_name, self.frame)
        _hash = f'File Hash : {self.artifact.hash}'
        filehash = Entry(self.frame, relief='flat')
        filehash.insert(0, _hash)
        filehash.config(state='readonly')
        filehash.pack(expand=True, fill=X)
        self.create_artifact()

    def create_artifact(self):
        print('Creating.. ', self.file_name)
        self.artifact.create_frame()
        print('Done creating artifacts. ')

    def get_hash(self):
        return self.artifact.hash

    def connect(self, path):
        self.artifact.data_to_csv(path)
        

class TableView:
    def __init__(self, window, file_names):
        self.window = window
        self.file_names = file_names
        container = Frame(self.window)
        canvas = Canvas(container, bg='#2F2F2F', height=352, width=850)
        scrollbar = Scrollbar(container, orient="horizontal", command=canvas.xview)
        self.frame = Frame(canvas, )
        self.frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=self.frame, anchor='nw')
        canvas.configure(xscrollcommand=scrollbar.set)
        container.pack(padx=25, pady=10)
        canvas.pack(side=TOP, expand=True, fill=BOTH)
        scrollbar.pack(side=BOTTOM, fill=X)
        print('Creating Tables')
        self.tables = list()
        self.hashes = list()
        for i in range(len(self.file_names)):
            temp = Table(self.frame, self.file_names[i], i + 1)
            self.tables.append(temp)
            self.hashes.append(temp.get_hash())

    def update_tables(self, new_tables):
        if not len(new_tables) == len(self.tables):
            popup_msg('Something went wrong')
            return
        for i in range(len(new_tables)):
            self.tables[i].artifact.update_artifact(new_tables[i])

    def connect2(self, path, index):
        self.tables[index].connect(path)

    def get_hash2(self):
        return self.hashes


class ViewDetails:
    def __init__(self, window, prev, file_names):
        self.check = False
        self.option_list = list()
        self.window = window
        self.prev = prev
        self.file_names = file_names
        self.frame = Frame(self.window, bg='#1F1F1F')
        self.table_frame = Frame(self.frame, bg='#1F1F1F')
        self.query_args_frame = Frame(self.frame, bg='#1F1F1F')
        self.buttons_frame = Frame(self.frame, bg="#2F2F2F")
        self.textvar = StringVar()

        self.query_args_frame.grid_columnconfigure(0, weight=1, uniform='grouped')
        self.query_args_frame.grid_columnconfigure(1, weight=1, uniform='grouped')
        self.query_args_frame.grid_columnconfigure(2, weight=1, uniform='grouped')
        self.query_args_frame.grid_columnconfigure(3, weight=1, uniform='grouped')
        self.query_args_frame.grid_rowconfigure(0, weight=1)
        self.l1frame = Frame(self.query_args_frame, bg='#1F1F1F', padx=5)
        self.l2frame = Frame(self.query_args_frame, bg='#1F1F1F', padx=5)
        self.l3frame = Frame(self.query_args_frame, bg='#1F1F1F', padx=5)
        self.l4frame = Frame(self.query_args_frame, bg='#1F1F1F', padx=5)
        self.strvar = StringVar()
        choices = sorted({
            'ALL',
            'Date',
            'Latitude',
            'Longitude',
            'Latitude Range',
            'Longitude Range',
            'Particular Date',
            'Particular Latitude',
            'Particular Longitude',
            'Date Range'
        })
        self.strvar.set('Select Compare Option')
        self.l1 = Label(self.l1frame, text='Select feature to compare:', bg='#1F1F1F', fg='#FFFFFF')
        self.l1.pack(side=TOP, pady=2)
        self.dropdown = OptionMenu(self.l1frame, self.strvar, *choices, command=self.set_this)
        self.dropdown.config(bg="#2F2F2F", fg="#FFFFFF", relief=FLAT, activebackground="#2F2F2F",
                             activeforeground="#FFFFFF")
        self.dropdown["highlightthickness"] = 0
        self.dropdown["menu"].config(bg="#2F2F2F", fg="#FFFFFF", relief=FLAT)
        self.dropdown.pack(side=BOTTOM, expand=True, fill=X)

        self.l2 = Label(self.l2frame, text=' ', bg='#1F1F1F', fg='#FFFFFF')

        # self.l2.pack(side=TOP, pady=2,)
        self.start = Entry(self.l2frame)
        # self.start.pack(side=BOTTOM, expand=True, fill=X, ipady=5, ipadx=5)
        self.l3 = Label(self.l3frame, text=' ', bg='#1F1F1F', fg='#FFFFFF')
        # self.l3.pack(side=TOP, pady=2)
        self.end = Entry(self.l3frame)
        # self.end.pack(side=BOTTOM, expand=True, fill=X, ipady=5, ipadx=5)
        self.l4 = Label(self.l4frame, text=' ', bg='#1F1F1F', fg='#FFFFFF')
        self.l4.pack(side=TOP, pady=2)
        compare_button = Button(
            self.l4frame,
            command=self.compare,
            text="Compare",
            relief=FLAT, bg='#0088DD',
            fg='#FFFFFF',
            pady=3,
            padx=5
        )
        compare_button.pack(side=BOTTOM, expand=True, fill=X)
        self.l1frame.grid(row=0, column=0, sticky=NSEW)
        self.l2frame.grid(row=0, column=1, sticky=NSEW)
        self.l3frame.grid(row=0, column=2, sticky=NSEW)
        self.l4frame.grid(row=0, column=3, sticky=NSEW)
        map_button = Button(self.buttons_frame, command=self.map_button, text="Map", relief=FLAT, bg='#0088DD',
                            fg='#FFFFFF', pady=10, padx=10)
        back_button = Button(self.buttons_frame, command=self.back_button, text="Back", relief=FLAT, bg='#2F2F2F',
                             fg='#FFFFFF', pady=10, padx=10)

        self.tableobj = TableView(self.table_frame, file_names)
        self.hashlist = self.tableobj.get_hash2()

        self.users = list()
        for i in range(1, len(self.hashlist) + 1):
            self.users.append("Person " + str(i))
        self.textvar.set("Export")

        export_button = OptionMenu(self.buttons_frame, self.textvar, *self.users, command=self.save_this_file)
        export_button.config(bg="#2F2F2F", fg="#FFFFFF", relief=FLAT, activebackground="#2F2F2F",
                             activeforeground="#FFFFFF", pady=10, padx=10)
        export_button["highlightthickness"] = 0
        export_button["menu"].config(bg="#2F2F2F", fg="#FFFFFF", relief=FLAT)

        back_button.grid(column=0, row=0, sticky=NSEW)
        map_button.grid(column=1, row=0, sticky=NSEW)
        export_button.grid(column=2, row=0, sticky=NSEW)
        self.buttons_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        self.buttons_frame.grid_columnconfigure(1, weight=1, uniform="group1")
        self.buttons_frame.grid_columnconfigure(2, weight=1, uniform="group1")
        self.buttons_frame.grid_rowconfigure(0, weight=1)
        self.buttons_frame.pack(side=BOTTOM, fill=X, expand=True, anchor=S)
        self.table_frame.pack(side=TOP, expand=True, fill=BOTH)
        self.query_args_frame.pack(expand=True, fill=BOTH)

    def _check_fields(self):
        if self.strvar.get() == 'Select Compare Option':
            popup_msg('No compare option selected')
            return False
        if self.strvar.get() == 'ALL' or self.strvar.get() == 'Date' or self.strvar.get() == 'Latitude' or \
                self.strvar.get() == 'Longitude':
            return True
        if self.strvar.get() == 'Particular Date':
            date = self.start.get()
            is_valid_date = True
            try:
                year, month, day = date.split('-')
                datetime(int(year), int(month), int(day))
            except ValueError:
                is_valid_date = False
            if not is_valid_date:
                popup_msg('Invalid Date')
            return is_valid_date
        if self.strvar.get() == 'Particular Latitude' or self.strvar.get() == 'Particular Longitude':
            start = self.start.get()
            is_valid_float = True
            try:
                float(start)
            except ValueError:
                is_valid_float = False
            if not is_valid_float:
                popup_msg('Invalid Value')
            return is_valid_float
        if self.strvar.get() == 'Date Range':
            date1 = self.start.get()
            date2 = self.end.get()
            is_valid_date = True
            try:
                year1, month1, day1 = date1.split('-')
                year2, month2, day2 = date2.split('-')
                datetime(int(year1), int(month1), int(day1))
                datetime(int(year2), int(month2), int(day2))
            except ValueError:
                is_valid_date = False
            if not is_valid_date:
                popup_msg('Invalid Date(s)')
            return is_valid_date
        if self.strvar.get() == 'Latitude Range' or self.strvar.get() == 'Longitude Range':
            start = self.start.get()
            end = self.end.get()
            is_valid_float = True
            try:
                float(start)
                float(end)
            except ValueError:
                is_valid_float = False
            if not is_valid_float:
                popup_msg('Invalid value(s)')
            return is_valid_float
        print('Unexpected error')
        return False

    def set_this(self, value):
        self.start.delete(0, "end")
        self.end.delete(0, "end")
        if value == 'ALL' or value == 'Date' or value == 'Latitude' or value == 'Longitude':
            self.l2frame.grid_forget()
            self.l3frame.grid_forget()
        elif value == 'Particular Date' or value == 'Particular Latitude' or value == 'Particular Longitude':
            self.l3frame.grid_forget()
            self.l2frame.grid(row=0, column=1, columnspan=2, sticky=NSEW)
            self.l2.config(text='Enter : ')
            self.l2.pack(side=TOP, pady=2)
            self.start.pack(side=BOTTOM, expand=True, fill=X, ipadx=5, ipady=5)
        else:
            self.l2frame.grid_forget()
            self.start.config(width=None)
            self.l2.config(text='Start : ')
            self.l2.pack(side=TOP, pady=2)
            self.start.pack(side=BOTTOM, expand=True, fill=X, ipadx=5, ipady=5)
            self.l3.config(text='End : ')
            self.l3.pack(side=TOP, pady=2)
            self.end.pack(side=BOTTOM, expand=True, fill=X, ipadx=5, ipady=5)
            self.l2frame.grid(row=0, column=1, sticky=NSEW)
            self.l3frame.grid(row=0, column=2, sticky=NSEW)
        self.option_list = list()
        print(value)

        if value == "ALL":
            self.option_list.append("Latitude")
            self.option_list.append("Longitude")
            self.option_list.append("Date")
            self.option_list.append("Time")
        elif value == "Latitude":
            self.option_list.append("Latitude")
        elif value == "Longitude":
            self.option_list.append("Longitude")
        elif value == "Date":
            self.option_list.append("Date")
        elif value == "Longitude Range":
            self.check = True
            self.option_list.append("Longitude")
        elif value == "Latitude Range":
            self.check = True
            self.option_list.append("Latitude")
        elif value == 'Date Range':
            self.check = True
            self.option_list.append("Date")
        elif value == "Particular Date":
            self.check = True
            self.option_list.append("Date")
        elif value == "Particular Latitude":
            self.check = True
            self.option_list.append("Latitude")
        elif value == "Particular Longitude":
            self.check = True
            self.option_list.append("Longitude")

    def compare(self):
        if not self._check_fields():
            return
        self.frame.pack_forget()
        loading = start_loading('Searching...')
        self.window.update()
        self._query()
        self.frame.pack(expand=True, fill=BOTH)
        stop_loading(loading)

    def _query(self):
        columns = self.option_list
        query = ""
        tables = list()
        if "Particular" in self.strvar.get():
            for i in range(len(self.hashlist)):
                query = "select *"
                query += " from {} where {} = '{}' group by Time".format('t' + self.hashlist[i], columns[0],
                                                                         self.start.get())
                print(query)
                c.execute(query)
                tables.append([c.fetchall()])
            print(tables)
        else:
            for i in range(len(self.hashlist)):
                query += "select "
                for j in range(len(columns)):
                    query += columns[j]
                    if j != len(columns) - 1:
                        query += ", "
                query += " from {}".format('t' + self.hashlist[i])
                if i != len(self.hashlist) - 1:
                    query += " intersect "
            if self.start.get() != "" and self.end.get() != "" and self.check:
                query += " where {} >= '{}' and {} <= '{}'".format(columns[0], self.start.get(), columns[0], self.end.get())
            query += " group by Time"
            print(query)
            c.execute(query)
            values = c.fetchall()
            for i in range(len(self.hashlist)):
                temp = list()
                for x in values:
                    query = "select *"
                    query += " from {} where {} = '{}' group by Time".format('t' + self.hashlist[i], columns[0], x[0])
                    print(query)
                    c.execute(query)
                    temp.append(c.fetchall())
                tables.append(temp)
            print(tables)
        self.tableobj.update_tables(tables)

    def save_this_file(self, value):
        for p in range(len(self.users)):
            if value == self.users[p]:
                self.export_file(p)

    def get_frame(self):
        return self.frame

    def get_files(self):
        return self.file_names

    def map_button(self):
        # TODO: Maps
        # (self.tableobj) is a TableView object which has a class variable called tables which is
        # a list containing objects of class Artifact wich contains class variables called
        # latitude, longitude, date and time, all of which are lists
        # for a loop variable i you can access attributes of user i+1 by variables:
        #   self.tableobj.tables[i].artifact.latitudes
        #   self.tableobj.tables[i].artifact.longitudes
        #   self.tableobj.tables[i].artifact.date
        #   self.tableobj.tables[i].artifact.time
        color=['#0000FF','#8A2BE2','#A52A2A','#5F9EA0','#7FFF00','#00FFFF']
        color1=['Blue','BlueViolet','Brown','CadetBlue','Chartreuse','Cyan']
        f = open("map1.html", "w+")
        gmap = gmplot.GoogleMapPlotter(24.7, 77.41, 5)
        for i in range(0,len(self.tableobj.tables)):
            latitude = [element for element in set(self.tableobj.tables[i].artifact.latitude) if isinstance(element, (int, float))]
            longitude = [element for element in set(self.tableobj.tables[i].artifact.longitude) if isinstance(element, (int, float))]
            gmap.scatter(latitude,longitude,color[i],size=10,marker=False)
            gmap.plot(latitude,longitude,color[i],edge_width=6-i)
        gmap.draw("map1.html")
        webbrowser.open("map1.html",new=2)

    def back_button(self):
        self.frame.pack_forget()
        pack(self.prev)

    def export_file(self, index):
        files = [("csv Files", "*csv")]
        path = filedialog.asksaveasfilename(filetypes=files)
        self.tableobj.connect2(path, index)
        self.textvar.set('Export')


def start_loading(text):
    frame = Frame(root, bg='#1F1F1F')
    Label(frame, text=text, bg='#1F1F1F', fg='#FFFFFF').pack(fill=BOTH, expand=True)
    frame.pack(fill=BOTH, expand=True)
    return frame


def stop_loading(frame):
    frame.pack_forget()


def pack(obj):
    obj.get_frame().pack(expand=True, fill=BOTH)


def unpack(obj):
    obj.get_frame().pack_forget()


def popup_msg(msg):
    messagebox.showerror('Error', msg)


def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


root = Tk()
root.title('Tool')
root.minsize(900, 512)
root.title("GM-LHCT")
center(root)
ff = BrowseFiles(root)
pack(ff)
root.mainloop()
