import sqlite3
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Image
from reportlab.lib import colors

# FÜGGVÉNYEK
def csvin(fname):
    " Beolvassa a csv fájl adatait egy tömbbe -> list:*tuple "
    with open(fname, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader) # 0.sort kihagyja
        data = [tuple(i) for i in reader]
    return data

def csvout(out_csv, data, col):
    " SQL query-t beolvassa egy csv fájlba "
    # col = len(tabla_adat[i]) ?
    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        #writer.writerow(['']*col) # 1.sor/mezők <- csvin() kihagyja!
        for i in data:
            writer.writerow(i)
    return out_csv

# ADATBÁZIS létrehozás és csatlakozás
db_name = "c:\\temp\\test_results.db"
conn = sqlite3.connect(db_name)
c = conn.cursor()

# Teszt - létezik-e a tábla?
try:
    c.execute("SELECT * FROM value_table")
except:
    pass
else:
    c.execute("DROP TABLE value_table")

# FÁJL tartalmának beolvasása tömbbe
fname = "c:\\temp\\results.csv"
file_cont = csvin(fname)

# ADATTÁBLA létrehoz
create_res = " CREATE TABLE IF NOT EXISTS value_table (Id INTEGER PRIMARY KEY NOT NULL, kód TEXT, érték REAL); "
c.execute(create_res)

# ADATTÁBLA feltölt
insert_res = " INSERT INTO value_table (Id,kód,érték) VALUES (?,?,?); "
c.executemany(insert_res, file_cont)

# ÁTLAGOK kiszámol
result_atlag = " SELECT kód, COUNT(*) as kód, round(AVG(érték),2) as result_avg FROM value_table GROUP BY kód "
c.execute(result_atlag)

# A SELECT lekérdezés tömbbe másolása
avgs = c.fetchall()
avgs.insert(0,("Id","kód","érték")) # fejléc 

# OUTPUT -> csv fájl -> pdf táblázat  
# Eredmények csv fájlba
newFile = "c:\\temp\\avg.csv"
csvout(newFile,avgs,3)

# Eredmények pdf fájlba
width, height = A4
pdfmetrics.registerFont(TTFont('Times', 'Times.ttf'))
pdf_name = "c:\\temp\\avg.pdf" 
c = canvas.Canvas(pdf_name) # fájl neve
c.setFont('Times', 16)
title_names = "Átlagok:"
c.drawCentredString(150,height-50,title_names)
c.setFont('Times', 12)

table = Table(avgs, 100, 25)
table.setStyle(TableStyle([            
            
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ('FONTNAME', (0,0),(-1,-1), 'Times'),
    ('BACKGROUND',(0,0),(-1,-1), colors.whitesmoke),
    ('BACKGROUND',(0,0),(2,0), colors.lightskyblue),

    ]))

table.wrapOn(c, width,height)
table.drawOn(c, 100,height-180)
c.save()

# ADATBÁZIS bezárása
conn.commit()
conn.close()

# English
# first row ignored!
# create db and connect
# read file
# create table
# add data to table
# average
# copy query to array
# output: formatted table to pdf, csv file
# close database