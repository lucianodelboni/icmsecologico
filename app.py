#-*- coding: UTF-8 -*-
from flask import Flask, render_template, redirect, url_for, request, session, flash
from packages import sql_connection as sql, random_pwd_gen as rpg
from time import ctime
import ntplib


#configuração inicial do flask, secret key do session e ntplib
app = Flask(__name__)
app.secret_key = "master123"
ntp_client = ntplib.NTPClient()
time_response = ntp_client.request('br.pool.ntp.org')

# função para gerar um número de processo sequencial
def ger_num_processo():
	num_extract = sql.cursor.execute("SELECT cont_num_processo FROM settings").fetchone()
	num = '{:06.0f}'.format(int(num_extract[0]))
	proximo_num = int(num_extract[0])+1
	este_ano = session.get('ano', None)

	if int(num)<10:
		num_processo = "SE" + str(num) + "/" + str(este_ano)
		sql.cursor.execute("UPDATE settings SET cont_num_processo=?", (proximo_num))
		sql.cnxn.commit()

	return num_processo

def ger_pwd_random(size):
	qtd_userext = len(sql.cursor.execute("SELECT * FROM UserAuth WHERE tipo='ext'").fetchall())
	ids = sql.cursor.execute("SELECT id FROM UserAuth WHERE tipo='ext'").fetchall()
	conv_tup_list =[x[0] for x in ids] # converting the list of tuples into a list
	for x in conv_tup_list:
		randompass = rpg.pwd_gen(size)
		sql.cursor.execute("UPDATE UserAuth SET password=? WHERE id=?", (randompass), (x))
		sql.cnxn.commit()


def ver_dados_envios():
	munic = session.get('munic', None)
	sql.cursor.execute("SELECT anoanalise, numprocesso, reqtipo, situacao, indice  FROM envio_preview WHERE mun=? ORDER BY anoanalise DESC", (munic))
	data=[]	
	for row in sql.cursor:
		data.append(row)
	return data

def ver_dados_usuarios():
	sql.cursor.execute("SELECT * FROM UserAuth ORDER BY tipo ASC")
	data=[]
	for row in sql.cursor:
		data.append(row)
	return data

def ver_addlock():
	add_lock = sql.cursor.execute("SELECT addlock FROM settings").fetchone()
	return add_lock

def ver_user_exist(name, login):
	check_name = sql.cursor.execute("SELECT MUN FROM UserAuth WHERE MUN=?", (name)).fetchone()
	check_login = sql.cursor.execute("SELECT username FROM UserAuth WHERE username=?", (login)).fetchone()
	if check_name == None and check_login == None:
		return False
	else:
		return True

def ver_id_exist(ID):
	check_id = sql.cursor.execute("SELECT id FROM UserAuth WHERE id=?", (ID))
	if check_id == None:
		return False
	else:
		return True

def ver_last_id():
	get_last_id = sql.cursor.execute("SELECT TOP 1 id FROM UserAuth ORDER BY id DESC").fetchone()
	return int(get_last_id[0])


#def ver_dados_historico():


#def valida_usuario(): para que o usuário em uma seção não interfira em um de outra


# criando roteamento para endereço com barras simples ou home e definindo autenticação de login
@app.route("/home", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
def home():
	if request.method == "POST":

		username = str(request.form["un"])
		password = str(request.form["pass"])
		session["user"] = username

		#Por enquanto não precisa constar em base de dados posteriormente pode ser integrado ao Siriema, por enquanto conta com login/pass fixo para admin
		if username == "imasul" and password == "123":
			return redirect(url_for("admin"))
		
		#Procura se existe um usuario externo/interno com as credenciais de login e senha e redireciona para sua pagina
		else:
			municipio = sql.cursor.execute("SELECT MUN FROM UserAuth WHERE username=?", (username)).fetchone()
			UsernameData = sql.cursor.execute("SELECT username FROM UserAuth WHERE username=?", (username)).fetchone()
			PasswordData = sql.cursor.execute("SELECT password FROM UserAuth WHERE username=?", (username)).fetchone()
			TypeofUser	= sql.cursor.execute("SELECT tipo FROM UserAuth WHERE username=?", (username)).fetchone()

			#Caso o usuario nao esteja na base de dados, redireciona para uma pagina de login falhou
			if UsernameData == None or PasswordData == None:
				return render_template("loginfail.html")
			#Caso contrário, realiza o login na página certa
			else:
				if municipio != None:
					session["munic"] = str(municipio[0])

				if username == UsernameData[0] and password == PasswordData[0] and TypeofUser[0] == "ext" :
					return redirect(url_for("userext"))
	
				if username == UsernameData[0] and password == PasswordData[0] and TypeofUser[0] == "tech" :
					return redirect(url_for("usertech"))

				else:
					return render_template("loginfail.html")
	
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
		time_check = ctime(time_response.tx_time).split(" ")
		session['ano'] = str(time_check[-1])
		este_ano = session.get('ano', None)
		munic = session.get('munic', None)
		data = ver_dados_envios()
		add_lock = ver_addlock() # trava para controlar a partir de quando um novo requerimento de ICMS pode ser feito
		req_check = sql.cursor.execute("SELECT reqcheck FROM res_urb_data WHERE ano_analise=? AND mun=?", (este_ano), (munic)).fetchone()
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
		sql.cursor.execute("INSERT INTO res_urb_data(mun, ano_base, ano_analise, reqcheck) VALUES (?, ?, ?, 'True')", (munic), (ano_base), (este_ano))
		sql.cursor.execute("INSERT INTO envio_preview(mun, anoanalise, numprocesso, reqtipo, situacao, indice) VALUES (?, ?, ?,'UC + RS', 'Novo', '0')",(munic), (este_ano), (num_processo))
		sql.cnxn.commit()
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

@app.route("/admin/historico")
def admin_historico():
	if "user" in session:
		return render_template("admin_historico.html")
	else:
		return render_template("nouser.html")

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

				if add_lock[0] == False:
					sql.cursor.execute("UPDATE settings SET addlock=?", (True))
					sql.cnxn.commit()
					addlock_status = "Ativada"
				else:
					sql.cursor.execute("UPDATE settings SET addlock=?", (False))
					sql.cnxn.commit()
					addlock_status = "Desativada"
		return render_template("admin_configuracoes.html", addlock_status=addlock_status)
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
					sql.cursor.execute("INSERT INTO UserAuth(id, MUN, username, password, tipo) VALUES(?, ?, ?, ?, ?)", (new_id), (new_user), (new_username), (new_pwd), (new_usr_type))
					sql.cnxn.commit()
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
					if id_exist == True:
						if edit_user != "":
							sql.cursor.execute("UPDATE UserAuth SET MUN=? WHERE id=?", (edit_user), (user_id))
						if edit_username != "":
							sql.cursor.execute("UPDATE UserAuth SET username=? WHERE id=?", (edit_username), (user_id))
						if edit_pwd != "":
							sql.cursor.execute("UPDATE UserAuth SET password=? WHERE id=?", (edit_pwd), (user_id))
						if edit_usr_type != "":
							sql.cursor.execute("UPDATE UserAuth SET tipo=? WHERE id=?", (edit_usr_type), (user_id))
						sql.cnxn.commit()
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
						sql.cursor.execute("DELETE FROM UserAuth WHERE id=?", (user_id))
						sql.cnxn.commit()
						flash(u'Usuário excluído com sucesso!')

				except Exception:
					flash('Erro: valor inserido é nulo ou não é um número referente à coluna ID da lista abaixo!')

			elif str(request.form['action']) == "randomize_ext":
				try:
					pwd_size = int(request.form['pwd_size'])

					if pwd_size > 6:
						ger_pwd_random(pwd_size)

					else:
						raise Exception

				except Exception:
					flash('Erro: Por questões de segurança, o número de caracteres da senha deve ser superior a 6')

		#chama a função para mostrar todos os usuários do sistema
		data = ver_dados_usuarios()
		return render_template("admin_usermgmt.html", data=data)
	else:
		return render_template("nouser.html")

@app.route("/admin/atribuir")
def admin_atribuir():
	if "user" in session:
		return render_template("admin_atribuir.html")
	else:
		return render_template("nouser.html")



# Seção dedicada ao roteamento de endpoints de acesso público.
@app.route("/logout")
def logout():
	session.pop("munic", None)
	session.pop("user", None)
	session.pop("ano", None)
	return redirect(url_for("home"))

@app.route("/ICMS_indice")
def ICMS_indice():
	if "user" in session:
		return render_template("ICMS_indice.html")


if __name__ == "__main__":
	app.run(debug=True)
