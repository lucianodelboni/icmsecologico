#-*- coding: UTF-8 -*-
import pyodbc

# define the server name and the database name
server = 'DESKTOP-S9KLVST\SQLEXPRESS'
database = 'ICMSTest'

# define our connection string
cnxn = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server}; \
					  SERVER=' + server + '; \
					  DATABASE=' + database + ';\
					  Trusted_Connection=yes;')


# create the connection cursor
cursor = cnxn.cursor()


clone = input("Type your login credentials: ")
clone2 = input("Type your password: ")


check = cursor.execute("SELECT name FROM Test WHERE name=?;", (clone)).fetchone()
check2 = cursor.execute("SELECT brand FROM Test WHERE name=?", (clone)).fetchone()


# define our insert query to insert data
#insert_query = 'INSERT INTO Test (name, age, grade) VALUES (?, ?, ?);'

#insert the data into the database
#cursor.execute(insert_query, (name, age, grade))

# commit the inserts
#cnxn.commit()
print(str(check))
print(str(check2))
print(clone)
print(clone2)

if clone == check[0] and clone2 == check2[0]:
	# Grab all the rows in our database table
	cursor.execute('SELECT * FROM Test')

	# Loop through the Results
	for row in cursor:
		print(row)

	print("you've got it!")
else:
	print("It didn't work, sorry!")

input:("are you satisfied with your software? ")
