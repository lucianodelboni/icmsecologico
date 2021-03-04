#-*- coding: UTF-8 -*-
import pyodbc

# define the server name and the database name
server = 'DESKTOP-S9KLVST\SQLEXPRESS'
database = 'ICMSTest'

# define our connection string
cnxn = pyodbc.connect('DRIVER={SQL Server}; \
					  SERVER=' + server + '; \
					  DATABASE=' + database + ';\
					  Trusted_Connection=yes;')


# create the connection cursor
cursor = cnxn.cursor()

name = 'Dorian'
age = 15
grade = 3.4

# define our insert query to insert data
insert_query = 'INSERT INTO Test (name, age, grade) VALUES (?, ?, ?);'

#insert the data into the database
cursor.execute(insert_query, (name, age, grade))

# commit the inserts
cnxn.commit()

# Grab all the rows in our database table
cursor.execute('SELECT * FROM Test')

# Loop through the Results
for row in cursor:
	print(row)