import pyodbc

# define o nome e database no servidor alvo
server = 'DESKTOP-S9KLVST\SQLEXPRESS'
database = 'ICMSTest'

# define a string de conexão com o SQL Server
cnxn = pyodbc.connect('DRIVER={SQL Server}; \
					  SERVER=' + server + '; \
					  DATABASE=' + database + ';\
					  Trusted_Connection=yes;')

cursor = cnxn.cursor()