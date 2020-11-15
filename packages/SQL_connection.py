def sql_connect():
	# define o nome e database no servidor alvo
	server = 'DESKTOP-S9KLVST\SQLEXPRESS'
	database = 'ICMSTest'

	# define a string de conexão com o SQL Server
	cnxn = pyodbc.connect('DRIVER={ODBC Driver 11 for SQL Server}; \
						  SERVER=' + server + '; \
						  DATABASE=' + database + ';\
						  Trusted_Connection=yes;')

	cursor = cnxn.cursor()