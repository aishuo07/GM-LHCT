import json, os, pymysql, time
import pandas as pd
from datetime import datetime
from texttable import Texttable
from tkinter import filedialog
from tkinter import *
import sqlite3
import csv
import tkinter as tk
from tkinter import ttk
import hashlib
e =10**7


root = tk.Tk()							 #name of the window
root.title("GM-LHCT")
root.state("zoomed")						#Full screen
root.resizable(0,0)						#screen size is not changeable
frame = Frame(root)
frame.place(relx=0,rely=0,relwidth =1, relheight = 1)           #defining frame


Label(frame, text = "SELECT FILE 1" ).place(relx = 0.04,rely=0.03)  #label for file selection
Label(frame, text = "SELECT FILE 2" ).place(relx = 0.04,rely=0.09)  #label for file selection


num1 = Entry(root)					#entry box for displaying first file name
num2 = Entry(root)  				#entry box for displaying first file name
num1.place(relx = 0.6,rely=0.03, relwidth = 0.5,anchor = NE) #placing entry boxes
num2.place(relx = 0.6,rely=0.09, relwidth = 0.5,anchor = NE) #placing entry boxes

hash1 = Entry(root)					#entry box for displaying first file name
hash2 = Entry(root)  				#entry box for displaying first file name
hash1.place(relx = 0.36,rely=0.91,anchor = NE,relwidth=0.28) #placing entry boxes
hash2.place(relx = 0.9,rely=0.91,anchor = NE,relwidth=0.28)

h1=Label(root, text="Hash Value")
h1.config(font = ("Courier bold",9))
h1.place(relx=.03, rely=.91)

h2=Label(root, text="Hash Value")
h2.config(font = ("Courier bold",9))
h2.place(relx=.57, rely=.91)

conn=sqlite3.connect("test1.db")
conn=sqlite3.connect("test.db")

def create_table(store):                                                            #Creating first database table
    conn=sqlite3.connect("test1.db")  				   #connecting to database
    cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS "+ store + " (Longitude STRING,Latitude STRING,Time STRING,Date STRING)")			#executing cursor to create table
    conn.commit()
    conn.close()



def insert(Longitude,Latitude,Time,Date,store):		#inserting heading to table
    conn=sqlite3.connect("test1.db")				#Connecting to database
    cur=conn.cursor()
    cur.execute("INSERT INTO "+ store + " VALUES (?,?,?,?)",(Longitude,Latitude,Time,Date))			#inserting values into table
    conn.commit()
    conn.close()

def view(store):						#function to display whole data
    conn=sqlite3.connect("test1.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM "+store)
    rows=cur.fetchall()
    conn.close()
    return rows
def common():							#function to get intersection
    conn=sqlite3.connect("test1.db")
    cur=conn.cursor()
    print(cur.execute('SELECT * FROM t INTERSECT SELECT * FROM t1'))
    rows=cur.fetchall()
    conn.close()
    return rows


#function to insert values into CSV table from selected file then to database file
def browsefunc():
    lat = []
    lon = []
    t = []
    d=[]
    hash1.delete(0,END)
    num1.delete(0, END)
    filename = filedialog.askopenfilename()
    pathlabel.config(text=filename)
    num1.insert(0, filename)
    #Reading and extracting data from JSON file
    json_data=open(filename,"rb").read()
    hasher1=hashlib.md5(json_data).hexdigest()

    hash1.insert(0,hasher1)
    json_obj = json.loads(json_data)

    data = ['---','---','---','---']
    store = "t"  			#Table in database
    create_table(store)
    table1 = Texttable()		#Texttable in python is used to create table

   #Running code for parsing the JSON file
    for i in json_obj.values():
        for j in range(len(i)):
            for k in i[j].keys():
                if(k == 'latitudeE7'):
                    data[0]= i[j][k]/e
                    lat.append(data[0])
                if(k == 'longitudeE7'):
                    data[1]= i[j][k]/e
                    lon.append(data[1])
                if(k == 'timestampMs'):
                    date_time= str(datetime.fromtimestamp(int(i[j][k][0:-3])))
                    data[3]= date_time[0:10]
                    data[2]= date_time[11:16]
                    t.append(data[2])
                    d.append(data[3])

    #Creating data from from list then converting to CSV
    datafr = {'Latitude':lat,"Longitude":lon,"Date":d,"Time":t}
    df = pd.DataFrame(datafr)
    df.to_csv("data_1.csv",index= True)

    TableMargin = Frame(root)
    TableMargin.place(relx = 0.36,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    #Scrollbar for table
    scrollbarx = Scrollbar(TableMargin, orient=HORIZONTAL)
    scrollbary = Scrollbar(TableMargin, orient=VERTICAL)
    tree = ttk.Treeview(TableMargin, columns=("Latitude", "Longitude", "Date", "Time"), height=50, selectmode="extended", yscrollcommand=scrollbary.set)
    scrollbary.config(command=tree.yview)
    scrollbary.pack(side=RIGHT, fill=Y)

    tree.heading('Latitude', text="Latitude", anchor=W)
    tree.heading('Longitude', text="Longitude", anchor=W)
    tree.heading('Date', text="Date", anchor=W)
    tree.heading('Time', text="Time", anchor=W)
    tree.column('#0', stretch=NO, minwidth=0, width=25)
    tree.column('#1', stretch=NO, minwidth=0, width=100)
    tree.column('#2', stretch=NO, minwidth=0, width=100)
    tree.column('#3', stretch=NO, minwidth=0, width=100)
    tree.pack()

    #Reading CSV file to import data to database
    with open('data_1.csv') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            Latitude = row['Latitude']
            Longitude = row['Longitude']
            Date = row['Date']
            Time = row['Time']
            tree.insert("", 0, values=(Latitude,Longitude,Date,Time))

    con = sqlite3.connect('test1.db')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS t (Longitude STRING,Latitude STRING,Date STRING,Time STRING)")
    with open('data_1.csv',newline='') as fin:
        dr = csv.DictReader(fin)
        to_db = [(i['Latitude'],i['Longitude'],i['Date'],i['Time'] ) for i in dr  ]

    cur.executemany("INSERT INTO t (Latitude,Longitude,Date,Time) VALUES (?,?,?,?); ", to_db )
    con.commit()
    con.close()


#Another browse function for 2nd file input
def browsefunc1():
    lat1 = []
    lon1 = []
    t1 = []
    d1=[]
    hash2.delete(0,END)
    num2.delete(0, END)
    filename = filedialog.askopenfilename()
    pathlabel.config(text=filename)
    num2.insert(0, filename)
    json_data=open(filename,'rb').read()
    hasher2=hashlib.md5(json_data).hexdigest()
    hash2.insert(0,hasher2)
    json_obj = json.loads(json_data)

    data = ['---','---','---','---']
    table2 = Texttable()
    create_table("t1")
    for i in json_obj.values():
        for j in range(len(i)):
            for k in i[j].keys():
                if(k == 'latitudeE7'):
                    lat1.append(i[j][k]/e)
                    data[0]= i[j][k]/e
                if(k == 'longitudeE7'):
                    lon1.append(i[j][k]/e)
                    data[1]= i[j][k]/e
                if(k == 'timestampMs'):
                    date_time= str(datetime.fromtimestamp(int(i[j][k][0:-3])))
                    data[3]= date_time[0:10]
                    data[2]= date_time[11:16]
                    t1.append(data[2])
                    d1.append(data[3])


    datafr = {'Latitude':lat1,"Longitude":lon1,"Date":d1,"Time":t1}
    df = pd.DataFrame(datafr)
    df.to_csv("data_2.csv",index= False)



    TableMargin = Frame(root)
    TableMargin.place(relx = 0.9,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    scrollbarx = Scrollbar(TableMargin, orient=HORIZONTAL)
    scrollbary = Scrollbar(TableMargin, orient=VERTICAL)
    tree = ttk.Treeview(TableMargin, columns=("Latitude", "Longitude", "Date", "Time"), height=50, selectmode="extended", yscrollcommand=scrollbary.set)
    scrollbary.config(command=tree.yview)
    scrollbary.pack(side=RIGHT, fill=Y)

    tree.heading('Latitude', text="Latitude", anchor=W)
    tree.heading('Longitude', text="Longitude", anchor=W)
    tree.heading('Date', text="Date", anchor=W)
    tree.heading('Time', text="Time", anchor=W)
    tree.column('#0', stretch=NO, minwidth=0, width=5)
    tree.column('#1', stretch=NO, minwidth=0, width=100)
    tree.column('#2', stretch=NO, minwidth=0, width=100)
    tree.column('#3', stretch=NO, minwidth=0, width=100)
    tree.pack()


    with open('data_2.csv') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            Latitude = row['Latitude']
            Longitude = row['Longitude']
            Date = row['Date']
            Time = row['Time']
            tree.insert("", 0, values=(Latitude,Longitude,Date,Time))





    con = sqlite3.connect('test1.db')
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS t1 (Longitude STRING,Latitude STRING,Date STRING,Time STRING)")
    with open('data_2.csv',newline='') as fin:
        dr = csv.DictReader(fin)
        to_db = [(i['Latitude'],i['Longitude'],i['Date'],i['Time'] ) for i in dr  ]

    cur.executemany("INSERT INTO t1 (Latitude,Longitude,Date,Time) VALUES (?,?,?,?); ", to_db )
    con.commit()
    con.close()
def common_Longitude():			#display where longitude data is common
    conn=sqlite3.connect("test1.db")
    cur=conn.cursor()

    cur.execute('SELECT * FROM t WHERE t.Longitude= (SELECT t1.Longitude from t1 where t.Longitude=t1.Longitude)')
    rows1=cur.fetchall()
    print(rows1)
    cur.execute('SELECT * FROM t1 WHERE t1.Longitude= (SELECT t.Longitude from t where t1.Longitude=t.Longitude)')
    rows2=cur.fetchall()

    conn.close()
    TableMargin = Frame(root)
    TableMargin.place(relx = 0.36,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex=ttk.Treeview(TableMargin,heigh=10,columns=("#0","#1","#2","#3"))
    tablex.column("#0",width = 50)
    tablex.column("#1",width = 100)
    tablex.column("#2",width = 100)
    tablex.column("#3",width = 100)
    tablex.column("#4",width = 70)
    tablex.heading('#0',text='Id')
    tablex.heading('#1',text='LATITUDE')
    tablex.heading('#2',text='LONGITUDE')
    tablex.heading('#3',text='Date')
    tablex.heading('#4',text='Time')



    for i in range(len(rows1)):
         tablex.insert("",i,text=i,values=(rows1[i][0],rows1[i][1],rows1[i][2],rows1[i][3]))


    scrollbarx = Scrollbar(TableMargin, orient=HORIZONTAL)
    scrollbary = Scrollbar(TableMargin, orient=VERTICAL)

    tablex.place(relx = 0.45,rely=0.15,anchor = NE,relwidth=0.4,relheight=0.8)
    tablex.lift()
    TableMargin = Frame(root)
    TableMargin.place(relx = 0.36,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex1=ttk.Treeview(TableMargin,heigh=10,columns=("#0","#1","#2","#3"))
    tablex1.column("#0",width = 50)
    tablex1.column("#1",width = 100)
    tablex1.column("#2",width = 100)
    tablex1.column("#3",width = 100)
    tablex1.column("#4",width = 70)
    tablex1.heading('#0',text='Id')
    tablex1.heading('#1',text='LATITUDE')
    tablex1.heading('#2',text='LONGITUDE')
    tablex1.heading('#3',text='Date')
    tablex1.heading('#4',text='Time')



    for i in range(len(rows2)):
         tablex1.insert("",i,text=i,values=(rows2[i][0],rows2[i][1],rows2[i][3],rows2[i][2]))


    vsb = ttk.Scrollbar(tablex1, orient="vertical", command=tablex1.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex1.place(relx = 0.9,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex1.lift()

    mainloop()

def common_Latitude():			#display common latitude data 0.
    conn=sqlite3.connect("test1.db")
    cur=conn.cursor()
    cur.execute('SELECT * FROM t WHERE t.Latitude= (SELECT t1.Latitude from t1 where t.Latitude=t1.Latitude)')
    rows1=cur.fetchall()
    cur.execute('SELECT * FROM t1 WHERE t1.Latitude= (SELECT t.Latitude from t where t1.Latitude=t.Latitude)')
    rows2=cur.fetchall()
    conn.close()
    tree = ttk.Treeview(root)
    tablex=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex.column("#0",width = 50)
    tablex.column("#1",width = 100)
    tablex.column("#2",width = 100)
    tablex.column("#3",width = 100)
    tablex.column("#4",width = 70)
    tablex.heading('#0',text='Id')
    tablex.heading('#1',text='LATITUDE')
    tablex.heading('#2',text='LONGITUDE')
    tablex.heading('#3',text='Date')
    tablex.heading('#4',text='Time')



    for i in range(len(rows1)):
         tablex.insert("",i,text=i,values=(rows1[i][0],rows1[i][1],rows1[i][3],rows1[i][2]))


    vsb = ttk.Scrollbar(tablex, orient="vertical", command=tablex.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex.place(relx = 0.36,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex.lift()
    tree = ttk.Treeview(root)
    tablex1=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex1.column("#0",width = 50)
    tablex1.column("#1",width = 100)
    tablex1.column("#2",width = 100)
    tablex1.column("#3",width = 100)
    tablex1.column("#4",width = 70)
    tablex1.heading('#0',text='Id')
    tablex1.heading('#1',text='LATITUDE')
    tablex1.heading('#2',text='LONGITUDE')
    tablex1.heading('#3',text='Date')
    tablex1.heading('#4',text='Time')



    for i in range(len(rows2)):
         tablex1.insert("",i,text=i,values=(rows2[i][0],rows2[i][1],rows2[i][3],rows2[i][2]))


    vsb = ttk.Scrollbar(tablex1, orient="vertical", command=tablex1.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex1.place(relx = 0.9,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex1.lift()

    mainloop()
# if common Latitude
# if common time
def common_time():
    conn=sqlite3.connect("test1.db")
    cur=conn.cursor()
    print(cur.execute('SELECT * FROM t WHERE t.Time= (SELECT t1.Time from t1 where t.Time=t1.Time)'))
    rows1=cur.fetchall()
    print(cur.execute('SELECT * FROM t1 WHERE t1.Time= (SELECT t.Time from t where t1.Time=t.Time)'))
    rows2=cur.fetchall()
    conn.close()
    tree = ttk.Treeview(root)
    tablex=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex.column("#0",width = 50)
    tablex.column("#1",width = 100)
    tablex.column("#2",width = 100)
    tablex.column("#3",width = 100)
    tablex.column("#4",width = 70)
    tablex.heading('#0',text='Id')
    tablex.heading('#1',text='LATITUDE')
    tablex.heading('#2',text='LONGITUDE')
    tablex.heading('#3',text='Date')
    tablex.heading('#4',text='Time')



    for i in range(len(rows1)):
         tablex.insert("",i,text=i,values=(rows1[i][0],rows1[i][1],rows1[i][3],rows1[i][2]))


    vsb = ttk.Scrollbar(tablex, orient="vertical", command=tablex.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex.place(relx = 0.36,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex.lift()
    tree = ttk.Treeview(root)
    tablex1=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex1.column("#0",width = 50)
    tablex1.column("#1",width = 100)
    tablex1.column("#2",width = 100)
    tablex1.column("#3",width = 100)
    tablex1.column("#4",width = 70)
    tablex1.heading('#0',text='Id')
    tablex1.heading('#1',text='LATITUDE')
    tablex1.heading('#2',text='LONGITUDE')
    tablex1.heading('#3',text='Date')
    tablex1.heading('#4',text='Time')



    for i in range(len(rows2)):
         tablex1.insert("",i,text=i,values=(rows2[i][0],rows2[i][1],rows2[i][3],rows2[i][2]))


    vsb = ttk.Scrollbar(tablex1, orient="vertical", command=tablex1.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex1.place(relx = 0.9,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex1.lift()

    mainloop()
# if common Latitude
#if common dat
def common_Date():
    conn=sqlite3.connect("test1.db")
    cur=conn.cursor()
    cur.execute('SELECT * FROM t WHERE t.Date= (SELECT t1.Date from t1 where t.Date=t1.Date)')
    rows1=cur.fetchall()
    cur.execute('SELECT * FROM t1 WHERE t1.Date= (SELECT t.Date from t where t1.Date=t.Date)')
    rows2=cur.fetchall()
    conn.close()
    tree = ttk.Treeview(root)
    tablex=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex.column("#0",width = 50)
    tablex.column("#1",width = 100)
    tablex.column("#2",width = 100)
    tablex.column("#3",width = 100)
    tablex.column("#4",width = 70)
    tablex.heading('#0',text='Id')
    tablex.heading('#1',text='LATITUDE')
    tablex.heading('#2',text='LONGITUDE')
    tablex.heading('#3',text='Date')
    tablex.heading('#4',text='Time')



    for i in range(len(rows1)):
         tablex.insert("",i,text=i,values=(rows1[i][0],rows1[i][1],rows1[i][3],rows1[i][2]))


    vsb = ttk.Scrollbar(tablex, orient="vertical", command=tablex.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex.place(relx = 0.36,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex.lift()
    tree = ttk.Treeview(root)
    tablex1=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex1.column("#0",width = 50)
    tablex1.column("#1",width = 100)
    tablex1.column("#2",width = 100)
    tablex1.column("#3",width = 100)
    tablex1.column("#4",width = 70)
    tablex1.heading('#0',text='Id')
    tablex1.heading('#1',text='LATITUDE')
    tablex1.heading('#2',text='LONGITUDE')
    tablex1.heading('#3',text='Date')
    tablex1.heading('#4',text='Time')



    for i in range(len(rows2)):
         tablex1.insert("",i,text=i,values=(rows2[i][0],rows2[i][1],rows2[i][3],rows2[i][2]))


    vsb = ttk.Scrollbar(tablex1, orient="vertical", command=tablex1.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex1.place(relx = 0.9,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)

    mainloop()
def common_Date1(dt):			#display date data for a particular date
    conn=sqlite3.connect("test1.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM t WHERE t.Date=\'%s\'"%dt)
    rows1=cur.fetchall()
    cur.execute("SELECT * FROM t1 WHERE t1.Date=\'%s\'"%dt)
    rows2=cur.fetchall()
    conn.close()
    tree = ttk.Treeview(root)
    tablex=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex.column("#0",width = 50)
    tablex.column("#1",width = 100)
    tablex.column("#2",width = 100)
    tablex.column("#3",width = 100)
    tablex.column("#4",width = 70)
    tablex.heading('#0',text='Id')
    tablex.heading('#1',text='LATITUDE')
    tablex.heading('#2',text='LONGITUDE')
    tablex.heading('#3',text='Date')
    tablex.heading('#4',text='Time')



    for i in range(len(rows1)):
         tablex.insert("",i,text=i,values=(rows1[i][0],rows1[i][1],rows1[i][3],rows1[i][2]))


    vsb = ttk.Scrollbar(tablex, orient="vertical", command=tablex.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex.place(relx = 0.36,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex.lift()
    tree = ttk.Treeview(root)
    tablex1=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex1.column("#0",width = 50)
    tablex1.column("#1",width = 100)
    tablex1.column("#2",width = 100)
    tablex1.column("#3",width = 100)
    tablex1.column("#4",width = 70)
    tablex1.heading('#0',text='Id')
    tablex1.heading('#1',text='LATITUDE')
    tablex1.heading('#2',text='LONGITUDE')
    tablex1.heading('#3',text='Date')
    tablex1.heading('#4',text='Time')



    for i in range(len(rows2)):
         tablex1.insert("",i,text=i,values=(rows2[i][0],rows2[i][1],rows2[i][3],rows2[i][2]))


    vsb = ttk.Scrollbar(tablex1, orient="vertical", command=tablex1.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex1.place(relx = 0.9,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
# if you want to print common data which is match with enter data
def common_Longitude1(lg):
    conn=sqlite3.connect("test1.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM t WHERE t.Longitude="+lg)
    rows1=cur.fetchall()
    cur.execute("SELECT * FROM t1 WHERE t1.Longitude="+lg)
    rows2=cur.fetchall()
    conn.close()
    tree = ttk.Treeview(root)
    tablex=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex.column("#0",width = 50)
    tablex.column("#1",width = 100)
    tablex.column("#2",width = 100)
    tablex.column("#3",width = 100)
    tablex.column("#4",width = 70)
    tablex.heading('#0',text='Id')
    tablex.heading('#1',text='LATITUDE')
    tablex.heading('#2',text='LONGITUDE')
    tablex.heading('#3',text='Date')
    tablex.heading('#4',text='Time')



    for i in range(len(rows1)):
         tablex.insert("",i,text=i,values=(rows1[i][0],rows1[i][1],rows1[i][3],rows1[i][2]))


    vsb = ttk.Scrollbar(tablex, orient="vertical", command=tablex.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex.place(relx = 0.36,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex.lift()
    tree = ttk.Treeview(root)
    tablex1=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex1.column("#0",width = 50)
    tablex1.column("#1",width = 100)
    tablex1.column("#2",width = 100)
    tablex1.column("#3",width = 100)
    tablex1.column("#4",width = 70)
    tablex1.heading('#0',text='Id')
    tablex1.heading('#1',text='LATITUDE')
    tablex1.heading('#2',text='LONGITUDE')
    tablex1.heading('#3',text='Date')
    tablex1.heading('#4',text='Time')



    for i in range(len(rows2)):
         tablex1.insert("",i,text=i,values=(rows2[i][0],rows2[i][1],rows2[i][3],rows2[i][2]))


    vsb = ttk.Scrollbar(tablex1, orient="vertical", command=tablex1.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex1.place(relx = 0.9,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)

# if you want to print common data which is match with enter data
def common_Latitude1(lt):
    print(lt,type(lt))
    #input()
    conn=sqlite3.connect("test1.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM t WHERE t.Latitude = "+str(lt))
    rows1=cur.fetchall()
    cur.execute("SELECT * FROM t1 WHERE t1.Latitude ="+str(lt))
    rows2=cur.fetchall()
    conn.close()
    tree = ttk.Treeview(root)
    tablex=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex.column("#0",width = 50)
    tablex.column("#1",width = 100)
    tablex.column("#2",width = 100)
    tablex.column("#3",width = 100)
    tablex.column("#4",width = 70)
    tablex.heading('#0',text='Id')
    tablex.heading('#1',text='LATITUDE')
    tablex.heading('#2',text='LONGITUDE')
    tablex.heading('#3',text='Dates')
    tablex.heading('#4',text='Time')



    for i in range(len(rows1)):
         tablex.insert("",i,text=i,values=(rows1[i][0],rows1[i][1],rows1[i][3],rows1[i][2]))


    vsb = ttk.Scrollbar(tablex, orient="vertical", command=tablex.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex.place(relx = 0.36,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex.lift()
    tree = ttk.Treeview(root)
    tablex1=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex1.column("#0",width = 50)
    tablex1.column("#1",width = 100)
    tablex1.column("#2",width = 100)
    tablex1.column("#3",width = 100)
    tablex1.column("#4",width = 70)
    tablex1.heading('#0',text='Id')
    tablex1.heading('#1',text='LATITUDE')
    tablex1.heading('#2',text='LONGITUDE')
    tablex1.heading('#3',text='Date')
    tablex1.heading('#4',text='Time')



    for i in range(len(rows2)):
         tablex1.insert("",i,text=i,values=(rows2[i][0],rows2[i][1],rows2[i][3],rows2[i][2]))


    vsb = ttk.Scrollbar(tablex1, orient="vertical", command=tablex1.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex1.place(relx = 0.9,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)




def common_date11(dt1,dt2):				            #displaying common data table
    conn=sqlite3.connect("test1.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM t WHERE t.Date BETWEEN \'%s\' AND \'%s\'"  %(dt1,dt2))
    rows1=cur.fetchall()
    cur.execute("SELECT * FROM t1 WHERE t1.Date BETWEEN \'%s\' AND \'%s\'"  %(dt1,dt2))
    rows2=cur.fetchall()
    conn.close()
    tree = ttk.Treeview(root)
    tablex=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex.column("#0",width = 50)
    tablex.column("#1",width = 100)
    tablex.column("#2",width = 100)
    tablex.column("#3",width = 100)
    tablex.column("#4",width = 70)
    tablex.heading('#0',text='Id')
    tablex.heading('#1',text='LATITUDE')
    tablex.heading('#2',text='LONGITUDE')
    tablex.heading('#3',text='Dates')
    tablex.heading('#4',text='Time')



    for i in range(len(rows1)):
         tablex.insert("",i,text=i,values=(rows1[i][0],rows1[i][1],rows1[i][3],rows1[i][2]))


    vsb = ttk.Scrollbar(tablex, orient="vertical", command=tablex.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex.place(relx = 0.36,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex.lift()
    tree = ttk.Treeview(root)
    tablex1=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex1.column("#0",width = 50)
    tablex1.column("#1",width = 100)
    tablex1.column("#2",width = 100)
    tablex1.column("#3",width = 100)
    tablex1.column("#4",width = 70)
    tablex1.heading('#0',text='Id')
    tablex1.heading('#1',text='LATITUDE')
    tablex1.heading('#2',text='LONGITUDE')
    tablex1.heading('#3',text='Date')
    tablex1.heading('#4',text='Time')



    for i in range(len(rows2)):
         tablex1.insert("",i,text=i,values=(rows2[i][0],rows2[i][1],rows2[i][3],rows2[i][2]))


    vsb = ttk.Scrollbar(tablex1, orient="vertical", command=tablex1.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex1.place(relx = 0.9,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)

def common_Longitude11(tm1,tm2):
    conn=sqlite3.connect("test1.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM t WHERE t.Longitude BETWEEN \'%s\' AND \'%s\'"  %(tm1,tm2))
    rows1=cur.fetchall()
    cur.execute("SELECT * FROM t1 WHERE t1.Longitude BETWEEN \'%s\' AND \'%s\'"  %(tm1,tm2))
    rows2=cur.fetchall()
    conn.close()
    tree = ttk.Treeview(root)
    tablex=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex.column("#0",width = 50)
    tablex.column("#1",width = 100)
    tablex.column("#2",width = 100)
    tablex.column("#3",width = 100)
    tablex.column("#4",width = 70)
    tablex.heading('#0',text='Id')
    tablex.heading('#1',text='LATITUDE')
    tablex.heading('#2',text='LONGITUDE')
    tablex.heading('#3',text='Dates')
    tablex.heading('#4',text='Time')



    for i in range(len(rows1)):
         tablex.insert("",i,text=i,values=(rows1[i][0],rows1[i][1],rows1[i][3],rows1[i][2]))


    vsb = ttk.Scrollbar(tablex, orient="vertical", command=tablex.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex.place(relx = 0.36,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex.lift()
    tree = ttk.Treeview(root)
    tablex1=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex1.column("#0",width = 50)
    tablex1.column("#1",width = 100)
    tablex1.column("#2",width = 100)
    tablex1.column("#3",width = 100)
    tablex1.column("#4",width = 70)
    tablex1.heading('#0',text='Id')
    tablex1.heading('#1',text='LATITUDE')
    tablex1.heading('#2',text='LONGITUDE')
    tablex1.heading('#3',text='Date')
    tablex1.heading('#4',text='Time')



    for i in range(len(rows2)):
         tablex1.insert("",i,text=i,values=(rows2[i][0],rows2[i][1],rows2[i][3],rows2[i][2]))


    vsb = ttk.Scrollbar(tablex1, orient="vertical", command=tablex1.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex1.place(relx = 0.9,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)

def common_Latitude11(tm1,tm2):			#displaying common latitude data
    conn=sqlite3.connect("test1.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM t WHERE t.Latitude BETWEEN \'%s\' AND \'%s\'"  %(tm1,tm2))
    rows1=cur.fetchall()
    cur.execute("SELECT * FROM t1 WHERE t1.Latitude BETWEEN \'%s\' AND \'%s\'"  %(tm1,tm2))
    rows2=cur.fetchall()
    conn.close()
    tree = ttk.Treeview(root)
    tablex=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex.column("#0",width = 50)
    tablex.column("#1",width = 100)
    tablex.column("#2",width = 100)
    tablex.column("#3",width = 100)
    tablex.column("#4",width = 70)
    tablex.heading('#0',text='Id')
    tablex.heading('#1',text='LATITUDE')
    tablex.heading('#2',text='LONGITUDE')
    tablex.heading('#3',text='Dates')
    tablex.heading('#4',text='Time')



    for i in range(len(rows1)):
         tablex.insert("",i,text=i,values=(rows1[i][0],rows1[i][1],rows1[i][3],rows1[i][2]))


    vsb = ttk.Scrollbar(tablex, orient="vertical", command=tablex.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex.place(relx = 0.36,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)
    tablex.lift()
    tree = ttk.Treeview(root)
    tablex1=ttk.Treeview(heigh=10,columns=("#0","#1","#2","#3"))
    tablex1.column("#0",width = 50)
    tablex1.column("#1",width = 100)
    tablex1.column("#2",width = 100)
    tablex1.column("#3",width = 100)
    tablex1.column("#4",width = 70)
    tablex1.heading('#0',text='Id')
    tablex1.heading('#1',text='LATITUDE')
    tablex1.heading('#2',text='LONGITUDE')
    tablex1.heading('#3',text='Date')
    tablex1.heading('#4',text='Time')



    for i in range(len(rows2)):
         tablex1.insert("",i,text=i,values=(rows2[i][0],rows2[i][1],rows2[i][3],rows2[i][2]))


    vsb = ttk.Scrollbar(tablex1, orient="vertical", command=tablex1.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    tablex1.place(relx = 0.9,rely=0.3,anchor = NE,relwidth=0.28,relheight=0.6)



#Browsing multiple file  and their buttions
root.geometry('700x600')
browsebutton = Button(root, text="Browse", command=browsefunc,justify="left")
browsebutton.place(relx = 0.7,rely=0.026,relwidth=0.12)

browsebutton1 = Button(root, text="Browse", command=browsefunc1)
browsebutton1.place(relx = 0.7,rely=0.086,relwidth=0.12)

pathlabel = Label(root)
#All features of tool
tkvar = StringVar(root)
choices = sorted({'ALL','DATE', 'LATITUDE', 'LONGITUDE',"Particular Date","Particular Latitude","Particular Longitude","Date Range","Latitude Range","Longitude Range"})
tkvar.set('Select Compare Option')

popupMenu = OptionMenu(root, tkvar, *choices)

l1=Label(root, text="Please select compare feature")
l1.config(font = ("Courier bold",9))
l1.place(relx=.05, rely=.15)

popupMenu.place(relx=.05, rely=.2)
num3 = Entry(root)                              		#User input for specific compare type
Label(root, text="START").place(relx=.28, rely=.15)
num3.place(relx = 0.38,rely=0.2, relwidth = 0.1,anchor = NE)

num4 = Entry(root)					#User input for range compare type
Label(root, text="END").place(relx=.48, rely=.15)
num4.place(relx = 0.58,rely=0.2, relwidth = 0.1,anchor = NE)

#Creating a dropdown file list for selection of the compare feature
def change_dropdown(*args):
    global dropdown
    dropdown = str(tkvar.get())

    if tkvar.get() == 'ALL':
        common()
    if tkvar.get() == "LONGITUDE":
        common_Latitude()
    if tkvar.get() == 'LATITUDE':
        common_Latitude()
    if tkvar.get() == "DATE":
        common_Date()
    if tkvar.get() == "Particular Latitude":
        s=num3.get()
        common_Latitude1(s)
    if tkvar.get() == "Particular Longitude":
        s=num3.get()
        common_Longitude1(s)
    if tkvar.get() == "Particular Date":
        s=num3.get()
        common_Date1(s)
    if tkvar.get() == "Date Range":
        s=num3.get()
        s1=num4.get()
        common_date11(s,s1)
    if tkvar.get() == "Latitude Range":
        s=num3.get()
        s1=num4.get()
        common_Latitude11(s,s1)
    if tkvar.get() == "Longitude Range":
        s=num3.get()
        s1=num4.get()
        common_Longitude11(s,s1)


# link function to change dropdown
tkvar.trace('w', change_dropdown)

#Deleting the database, if created
mainloop()
try:
    os.remove("test1.db")
except:
    print("No File")
try:
    os.remove("test1.db")
except:
    print("No File")
