#-*- coding: UTF-8 -*-
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_mysqldb import MySQL
import yaml

#configuração inicial do flask, secret key do session e MySQL
app = Flask(__name__)
app.secret_key = "master123"
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)
sql.cursor = mysql.connection.cursor()


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

def ver_dados_envios():
	munic = session.get('munic', None)
	sql.cursor.execute("SELECT anoanalise, numprocesso, reqtipo, situacao, indice  FROM envio_preview WHERE mun=? ORDER BY anoanalise DESC", (munic))
	data=[]	
	for row in sql.cursor:
		data.append(row)
	return data

def ver_addlock():
	add_lock = sql.cursor.execute("SELECT addlock FROM settings").fetchone()
	return add_lock

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

		municipio = sql.cursor.execute("SELECT MUN FROM UserAuth WHERE username=?", (username)).fetchone()
		UsernameData = sql.cursor.execute("SELECT username FROM UserAuth WHERE username=?", (username)).fetchone()
		PasswordData = sql.cursor.execute("SELECT password FROM UserAuth WHERE username=?", (username)).fetchone()
		TypeofUser	= sql.cursor.execute("SELECT type FROM UserAuth WHERE username=?", (username)).fetchone()

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

@app.route("/admin/configuracoes")
def admin_configuracoes():
	if "user" in session:
		add_lock = ver_addlock()
		return render_template("admin_configuracoes.html", addlock_status=str(add_lock[0]))
	else:
		return render_template("nouser.html")

@app.route("/change_addlock")
def change_addlock():
	if "user" in session:
		add_lock = ver_addlock()
		if add_lock[0] == False:
			sql.cursor.execute("UPDATE settings SET addlock=?", (True))
			sql.cnxn.commit()
		else:
			sql.cursor.execute("UPDATE settings SET addlock=?", (False))
			sql.cnxn.commit()
		return redirect(url_for("admin_configuracoes"))
	else:
		return render_template("nouser.html")


@app.route("/admin/usermgmt")
def admin_usermgmt():
	if "user" in session:
		return render_template("admin_usermgmt.html")
	else:
		return render_template("nouser.html")



# Seção dedicada ao roteamento de páginas de acesso público.
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
