#-*- coding: UTF-8 -*-
from flask import Flask, render_template, redirect, url_for, request, session, flash
from packages import random_pwd_gen as rpg
from flask_mysqldb import MySQL


#configuração inicial do flask, secret key do session e MySQL
app = Flask(__name__)
mysql = MySQL()
app.secret_key = "default"

#configuração de conexão com a base de dados

def db_connect():
	app.config['MYSQL_HOST'] = 'lucknfx5.mysql.pythonanywhere-services.com'
	app.config['MYSQL_USER'] = 'lucknfx5'
	app.config['MYSQL_PASSWORD'] = 'defaultpassword123'
	app.config['MYSQL_DB'] = 'lucknfx5$UserAuth'
	mysql.init_app(app)

	#único jeito que achei de a database não ficar desconectando foi estabelecer variáveis globais dentro do contexto do app e desconectar a db imediatamente após as consultas.
	with app.app_context():
		global conn
		conn = mysql.connect
		global sql_cursor
		sql_cursor = conn.cursor()

def db_close_connection():
	sql_cursor.close()
	conn.close()


def atribuir_status(num_processo, tecnicos_string):
	db_connect()
	sql_cursor.execute("UPDATE envio_preview SET tech_resp=%s WHERE numprocesso=%s", (tecnicos_string, num_processo,))
	conn.commit()
	db_close_connection()

# função para gerar um número de processo sequencial
def ger_num_processo():
	db_connect()
	sql_cursor.execute("SELECT cont_num_processo FROM settings")
	num_extract = sql_cursor.fetchone()
	num = '{:06.0f}'.format(int(num_extract[0]))
	proximo_num = int(num_extract[0])+1
	este_ano = 2020

	if int(num)<10:
		num_processo = "SE" + str(num) + "/" + str(este_ano)
		sql_cursor.execute("UPDATE settings SET cont_num_processo=%s", (proximo_num,))
		conn.commit()

	db_close_connection()
	return num_processo

def ger_pwd_random(size):
	db_connect()
	sql_cursor.execute("SELECT ID FROM UserAuth WHERE type='ext'")
	ids =  sql_cursor.fetchall()
	conv_tup_list =[x[0] for x in ids] # converting the list of tuples into a list
	for x in conv_tup_list:
		randompass = rpg.pwd_gen(size)
		sql_cursor.execute("UPDATE UserAuth SET password=%s WHERE ID=%s", (randompass, x,))
		conn.commit()
	db_close_connection()

def ver_dados_envios():
	db_connect()
	munic = session.get('munic', None)
	sql_cursor.execute("SELECT anoanalise, numprocesso, reqtipo, situacao, indice  FROM envio_preview WHERE mun=%s ORDER BY anoanalise DESC", (munic,))
	dados_envios=[]
	for row in sql_cursor:
		dados_envios.append(row)
	db_close_connection()
	return dados_envios

def ver_addlock():
	db_connect()
	sql_cursor.execute("SELECT addlock FROM settings")
	add_lock = sql_cursor.fetchone()
	db_close_connection()
	return add_lock

def ver_dados_usuarios(tipo):
	db_connect()
	if tipo == "todos":
		sql_cursor.execute("SELECT * FROM UserAuth ORDER BY ID ASC")
	elif tipo == "ext":
		sql_cursor.execute("SELECT * FROM UserAuth WHERE type='ext' ORDER BY ID ASC")
	if tipo == "tech":
		sql_cursor.execute("SELECT * FROM UserAuth WHERE type='tech' ORDER BY ID ASC")
	dados_usuarios=[]
	for row in sql_cursor:
		dados_usuarios.append(row)
	db_close_connection()
	return dados_usuarios

def ver_historico_anoanalise():
	db_connect()
	sql_cursor.execute("SELECT DISTINCT anoanalise FROM envio_preview WHERE anoanalise IS NOT NULL ORDER BY anoanalise DESC")
	hist_catcher = sql_cursor.fetchall()
	db_close_connection()
	return hist_catcher

def ver_historico_processos(ano):
	db_connect()
	sql_cursor.execute("SELECT * FROM envio_preview WHERE anoanalise=%s", (ano,))
	hist_proc = sql_cursor.fetchall()
	db_close_connection()
	return hist_proc

def ver_user_exist(name, login):
	db_connect()
	sql_cursor.execute("SELECT MUN FROM UserAuth WHERE MUN=%s", (name,))
	check_name = sql_cursor.fetchone()
	sql_cursor.execute("SELECT username FROM UserAuth WHERE username=%s", (login,))
	check_login = sql_cursor.fetchone()
	db_close_connection()
	if check_name == None and check_login == None:
		return False
	else:
		return True

def ver_id_exist(id_spec):
	db_connect()
	check_id = sql_cursor.execute("SELECT ID FROM UserAuth WHERE ID=%s", (id_spec,))
	db_close_connection()
	if check_id == None:
		return False
	else:
		return True

def ver_last_id():
	db_connect()
	sql_cursor.execute("SELECT ID FROM UserAuth ORDER BY ID DESC LIMIT 1")
	get_last_id = sql_cursor.fetchone()
	db_close_connection()
	return int(get_last_id[0])


#def valida_usuario(): para que o usuário em uma seção não interfira em um de outra


# criando roteamento para endereço com barras simples ou home e definindo autenticação de login
@app.route("/home", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
def home():
	if request.method == "POST":
		username = str(request.form["un"])
		password = str(request.form["pass"])

		db_connect()

		sql_cursor.execute("SELECT MUN FROM UserAuth WHERE username=%s", (username,))
		municipio = sql_cursor.fetchone()
		sql_cursor.execute("SELECT username FROM UserAuth WHERE username=%s", (username,))
		UsernameData = sql_cursor.fetchone()
		sql_cursor.execute("SELECT password FROM UserAuth WHERE username=%s", (username,))
		PasswordData = sql_cursor.fetchone()
		sql_cursor.execute("SELECT type FROM UserAuth WHERE username=%s", (username,))
		TypeofUser	= sql_cursor.fetchone()

		if UsernameData == None or PasswordData == None:
			return render_template("loginfail.html")

		else:
			if username == UsernameData[0] and password == PasswordData[0] and TypeofUser[0] == "ext":
				session["user"] = username
				session["munic"] = str(municipio[0])
				session["typeofuser"] = TypeofUser[0]
				return redirect(url_for("userext"))
			elif username == UsernameData[0] and password == PasswordData[0] and TypeofUser[0] == "tech":
				session["user"] = username
				session["munic"] = str(municipio[0])
				session["typeofuser"] = TypeofUser[0]
				return redirect(url_for("usertech"))
			elif username == UsernameData[0] and password == PasswordData[0] and TypeofUser[0] == "admin":
				session["user"] = username
				session["munic"] = str(municipio[0])
				session["typeofuser"] = TypeofUser[0]
				return redirect(url_for("admin"))
			else:
				return render_template("loginfail.html")

		db_close_connection()
	return render_template("login.html")

# Seção de endpoints dedicada ao roteamento de páginas do usuário externo (municipio)
@app.route("/userext")
def userext():
	if "user" in session:
		munic = session.get('munic', None)
		return render_template("userext.html", mun_name=munic)
	else:
		return render_template("nouser.html")

@app.route("/userext/envios")
def userext_envios():
	if "user" in session:
		este_ano = 2020
		session["ano"] = este_ano
		munic = session.get('munic', None)
		data = ver_dados_envios()
		add_lock = ver_addlock() # trava para controlar a partir de quando um novo requerimento de ICMS pode ser feito
		db_connect()
		sql_cursor.execute("SELECT reqcheck FROM res_urb_data WHERE ano_analise=%s AND mun=%s", (este_ano, munic))
		req_check = sql_cursor.fetchone()
		db_close_connection()
		return render_template("userext_envios.html", este_ano=este_ano, data=data, add_lock=add_lock[0], req_check=req_check)
	else:
		return render_template("nouser.html")

@app.route("/userext/envios/novo")
def userext_envios_novo():
	if "user" in session:
		este_ano = session.get('ano', None)
		munic = session.get('munic', None)
		ano_base = int(este_ano)-1
		num_processo = ger_num_processo()
		db_connect()
		sql_cursor.execute("INSERT INTO res_urb_data(mun, ano_base, ano_analise, reqcheck) VALUES (%s, %s, %s, 'Verdadeiro')", (munic,), (ano_base,), (este_ano,))
		sql_cursor.execute("INSERT INTO envio_preview(mun, anoanalise, numprocesso, reqtipo, situacao, indice) VALUES (%s, %s, %s,'UC + RS', 'Novo', '0')",(munic,), (este_ano,), (num_processo,))
		conn.commit()
		db_close_connection()
		return render_template("userext_envios_novo.html")
	else:
		return render_template("nouser.html")

@app.route("/userext/pendencias")
def userext_pendencias():
	if "user" in session:
		return render_template("userext_pendencias.html")
	else:
		return render_template("nouser.html")

@app.route("/userext/recurso")
def userext_recurso():
	if "user" in session:
		return render_template("userext_recurso.html")
	else:
		return render_template("nouser.html")

@app.route("/userext/resumo")
def userext_resumo():
	if "user" in session:
		return render_template("userext_resumo.html")
	else:
		return render_template("nouser.html")


# Seção de endpoints dedicada ao roteamento de páginas do usuário interno (Imasul).
@app.route("/usertech")
def usertech():
	if "user" in session:
		return render_template("usertech.html")
	else:
		return render_template("nouser.html")




# Seção de endpoints dedicada ao roteamento de páginas do usuário administrador.
@app.route("/admin")
def admin():
	if "user" in session:
		return render_template("admin.html")
	else:
		return render_template("nouser.html")

@app.route("/admin/historico/")
def admin_historico():
	if "user" in session:
		data_anoanalise = ver_historico_anoanalise()
		return render_template("admin_historico.html", data=data_anoanalise)
	else:
		return render_template("nouser.html")

@app.route("/admin/historico/<ano>")
def admin_historico_processos(ano):
	if "user" in session:
		data_processos = ver_historico_processos(ano)
		return render_template("admin_historico_processos.html", data=data_processos)
	else:
		return render_template("nouser.html")

@app.route("/admin/historico/<ano>/<cod_processo>")
def admin_historico_especifico(ano, cod_processo):
	if "user" in session:
		#passar dados deste processo a serem mostrados na tela
		return render_template("admin_historico_especifico.html", cod_processo=cod_processo)

@app.route("/admin/estatisticas")
def admin_estatisticas():
	if "user" in session:
		return render_template("admin_estatisticas.html")
	else:
		return render_template("nouser.html")

@app.route("/admin/configuracoes", methods=["POST", "GET"])
def admin_configuracoes():
	if "user" in session:
		add_lock = ver_addlock()
		if request.method == "POST":
			if str(request.form['action']) == "addlock_change":
				db_connect()
				if add_lock[0] == '0':
					sql_cursor.execute("UPDATE settings SET addlock=%s", ('1',))
					conn.commit()
				else:
					sql_cursor.execute("UPDATE settings SET addlock=%s", ('0',))
					conn.commit()
				db_close_connection()
		add_lock = ver_addlock()
		if add_lock[0] == '1':
			add_lock = "Ativada"
		else:
			add_lock = "Desativada"
		return render_template("admin_configuracoes.html", addlock_status=add_lock)
	else:
		return render_template("nouser.html")


@app.route("/admin/usermgmt", methods=["POST", "GET"])
def admin_usermgmt():
	if "user" in session:
		if request.method == "POST":
			#adiciona novo usuário
			if str(request.form['action']) == "add":
				#pega as variáveis do formulário
				new_user = str(request.form["new_user"])
				new_username = str(request.form["new_username"])
				new_pwd = str(request.form["new_pwd"])
				new_usr_type = str(request.form["new_usr_type"])

				#verifica se o usuário já existe com base no nome e no login
				user_exist = ver_user_exist(new_user, new_username)

				if user_exist == False:
					#insere as novas credenciais na base de dados
					new_id = ver_last_id() + 1
					db_connect()
					sql_cursor.execute("INSERT INTO UserAuth(ID, MUN, username, password, type) VALUES(%s, %s, %s, %s, %s)", (new_id, new_user, new_username, new_pwd, new_usr_type,))
					conn.commit()
					db_close_connection()
					flash(u'O usuário foi adicionado com sucesso!')

				else:
					flash(u'Erro: Não foi possível adicionar o novo usuário, pois ele já existe!')

			#edita um usuário existente
			elif str(request.form['action']) == "edit":
				try:
					user_id = int(request.form['user_id'])
					edit_user = str(request.form["edit_user"])
					edit_username = str(request.form["edit_username"])
					edit_pwd = str(request.form["edit_pwd"])
					edit_usr_type = str(request.form["edit_usr_type"])

					id_exist = ver_id_exist(user_id)

					#código para atualizar apenas os campos que foram preenchidos no formulário
					db_connect()
					if id_exist == True:
						if edit_user != "":
							sql_cursor.execute("UPDATE UserAuth SET MUN=%s WHERE ID=%s", (edit_user, user_id,))
						if edit_username != "":
							sql_cursor.execute("UPDATE UserAuth SET username=%s WHERE ID=%s", (edit_username, user_id,))
						if edit_pwd != "":
							sql_cursor.execute("UPDATE UserAuth SET password=%s WHERE ID=%s", (edit_pwd, user_id,))
						if edit_usr_type != "":
							sql_cursor.execute("UPDATE UserAuth SET type=%s WHERE ID=%s", (edit_usr_type, user_id,))
						conn.commit()
						db_close_connection()
						flash(f'Os campos do usuário de Id {user_id} foram alterados com sucesso!')
					else:
						flash(f'Não existe usuário cujo id seja {user_id}.')

				except Exception:
					flash('Erro: valor inserido é nulo ou não é um número referente à coluna ID da lista abaixo!')

			elif str(request.form['action']) == "del":
				try:
					user_id = int(request.form['user_id'])
					last_id = ver_last_id()

					if user_id <= 0 or user_id > last_id:
						raise Exception

					else:
						db_connect()
						sql_cursor.execute("DELETE FROM UserAuth WHERE ID=%s", (user_id,))
						conn.commit()
						db_close_connection()
						flash(u'Usuário excluído com sucesso!')

				except Exception:
					flash('Erro: valor inserido é nulo ou não é um número referente à coluna ID da lista abaixo!')

			elif str(request.form['action']) == "randomize_ext":
				try:
					pwd_size = request.form['pwd_size']
					pwd_size = int(pwd_size)

					if pwd_size > 6:
						ger_pwd_random(pwd_size)

					else:
						raise Exception

				except Exception:
					flash('Erro: Por questões de segurança, o número de caracteres da senha deve ser superior a 6')

		#chama a função para mostrar todos os usuários do sistema
		data_usrs = ver_dados_usuarios("todos")
		return render_template("admin_usermgmt.html", data=data_usrs)
	else:
		return render_template("nouser.html")

@app.route("/admin/atribuir")
def admin_atribuir():
	if "user" in session:
		data_anoanalise = ver_historico_anoanalise()
		return render_template("admin_atribuir.html", data=data_anoanalise)
	else:
		return render_template("nouser.html")

@app.route("/admin/atribuir/<ano>", methods=["POST", "GET"])
def admin_atribuir_processos(ano):
	if "user" in session:
		check_tecnicos = ver_dados_usuarios("tech")
		tecnicos = [x[1] for x in check_tecnicos]
		data_processos = ver_historico_processos(ano)
		if request.method == "POST":
			#inserido os resultados das checkbox em uma variavel e formatando ela para extrair os valores
			verifier = []
			for row in data_processos:
				for tecnico in tecnicos:
					atrib_string = 'checkbox_'+str(row[2])+'_'+str(tecnico)
					try:
						verifier.append(request.form[f'{atrib_string}'])
					except:
						continue
			#formatando a bagunça que sai de output do verifier - manipulação de strings
			verifier = [s.strip("(") for s in verifier]
			verifier = [s.strip(")") for s in verifier]
			verifier = [s.replace("'", "") for s in verifier]
			newlist=[]
			for n in verifier:
				split_entry = n.split(",")
				newlist.append(split_entry)
			flattened_newlist = [val for sublist in newlist for val in sublist]

			#obtendo o número do processo e concatenando o nome dos técnicos responsáveis para inserir no banco de dados.
			try:
				num_processo_atribuir = flattened_newlist[0]
				concat_tecnicos = ''
				tecnicos_resp = []

				for y in range(1,len(flattened_newlist),2):
					tecnicos_resp.append(flattened_newlist[y])
				concat_tecnicos = ", ".join(tecnicos_resp)

				#Atualiza a base de dados para mostrar no front-end quem são os técnicos responsáveis.
				atribuir_status(num_processo_atribuir, concat_tecnicos)

				#verifica a base de dados para atualizar a tabela mostrada na página.
				data_processos = ver_historico_processos(ano)
				flash('O campo foi alterado com sucesso!')

			except Exception:
				flash('Erro: O campo de técnicos responsáveis não pode ficar em branco depois de alterado pela primeira vez!')

		return render_template("admin_atribuir_processos.html", data=data_processos, tecnicos=tecnicos)
	else:
		return render_template("nouser.html")


# Seção dedicada ao roteamento de páginas de acesso público.
@app.route("/logout")
def logout():
	session.pop("munic", None)
	session.pop("user", None)
	session.pop("ano", None)
	try:
		sql_cursor.close()
		conn.close()
	except Exception:
		pass
	return redirect(url_for("home"))

@app.route("/ICMS_indice")
def ICMS_indice():
	if "user" in session:
		return render_template("ICMS_indice.html")


#if __name__ == "__main__":
#	app.run(debug=True)
