#-*- coding: UTF-8 -*-
from flask import Flask, render_template, redirect, url_for, request, session, flash
from packages import sql_connection as sql
from time import ctime
import ntplib

#configuração inicial do flask, secret key do session e ntplib
app = Flask(__name__)
app.secret_key = "master123"
ntp_client = ntplib.NTPClient()
time_response = ntp_client.request('br.pool.ntp.org')


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
			municipio = sql.cursor.execute("SELECT MUN FROM auth_userext WHERE username=?", (username)).fetchone()
			UsernameData = sql.cursor.execute("SELECT username FROM auth_userext WHERE username=?", (username)).fetchone()
			PasswordData = sql.cursor.execute("SELECT password FROM auth_userext WHERE username=?", (username)).fetchone()
			TypeofUser	= sql.cursor.execute("SELECT tipo FROM auth_userext WHERE username=?", (username)).fetchone()

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

# Seção dedicada ao roteamento de páginas do usuário externo (municipio)
@app.route("/userext")
def userext():
	if "user" in session:
		munic = session.get('munic', None)
		return render_template("userext.html", mun_name=munic)
	else:
		return(render_template("nouser.html"))

@app.route("/userext/envios")
def userext_envios():
	if "user" in session:
		time_check = ctime(time_response.tx_time).split(" ")
		session['ano'] = str(time_check[-1])
		este_ano = session.get('ano', None)
		munic = session.get('munic', None)
		sql.cursor.execute("SELECT anoanalise, numprocesso, reqtipo, situacao, indice  FROM envio_preview WHERE mun=? ORDER BY anoanalise DESC", (munic))
		data=[]	
		for row in sql.cursor:
			data.append(row)

		return render_template("userext_envios.html", este_ano=este_ano, data=data)
	else:
		return(render_template("nouser.html"))

@app.route("/userext/envios/novo")
def userext_envios_novo():
	if "user" in session:
		add_lock = sql.cursor.execute("SELECT addlock FROM settings").fetchone() # trava para controlar a partir de quando um novo requerimento de ICMS pode ser feito
		if add_lock[0] == False:
			este_ano = session.get('ano', None)
			munic = session.get('munic', None)
			ano_base = int(este_ano)-1
			req_check = sql.cursor.execute("SELECT reqcheck FROM res_urb_data WHERE ano_analise=? AND mun=?", (este_ano), (munic)).fetchone() # Verifica se o usuário já iniciou o preenchimento de um requerimento
			if req_check[0] == None: # existe um erro nesta parte do código, corrigir mais tarde
				sql.cursor.execute("INSERT INTO res_urb_data(mun, ano_base, ano_analise, reqcheck) VALUES (?, ?, ?, 'True')", (munic), (ano_base), (este_ano))
				return render_template("userext_envios_novo.html")
			else:
				pass #inserir ação popover (bootstrap) para reqcheck true
		else:
			pass #inserir ação popover (bootstrap) para addlock true
	else:
		return(render_template("nouser.html"))

@app.route("/userext/pendencias")
def userext_pendencias():
	if "user" in session:
		return render_template("userext_pendencias.html")
	else:
		return(render_template("nouser.html"))

@app.route("/userext/recurso")
def userext_recurso():
	if "user" in session:
		return render_template("userext_recurso.html")
	else:
		return(render_template("nouser.html"))

@app.route("/userext/resumo")
def userext_resumo():
	if "user" in session:
		return render_template("userext_resumo.html")
	else:
		return(render_template("nouser.html"))


# Seção dedicada ao roteamento de páginas do usuário interno (Imasul), incluindo admin.
@app.route("/usertech")
def usertech():
	if "user" in session:
		return render_template("usertech.html")
	else:
		return(render_template("nouser.html"))

@app.route("/admin")
def admin():
	if "user" in session:
		return render_template("admin.html")
	else:
		return(render_template("nouser.html"))


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