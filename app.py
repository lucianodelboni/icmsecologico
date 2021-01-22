#-*- coding: UTF-8 -*-
from flask import Flask, render_template, redirect, url_for, request, session
from flask_mysqldb import MySQL

#configuração inicial do flask, secret key do session e MySQL
app = Flask(__name__)
mysql = MySQL()
app.secret_key = "default"

app.config['MYSQL_HOST'] = 'lucknfx5.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'lucknfx5'
app.config['MYSQL_PASSWORD'] = 'defaultpassword123'
app.config['MYSQL_DB'] = 'lucknfx5$UserAuth'
mysql.init_app(app)

with app.app_context():
    conn = mysql.connect
    sql_cursor = conn.cursor()



# função para gerar um número de processo sequencial
def ger_num_processo():
    sql_cursor.execute("SELECT cont_num_processo FROM settings")
    num_extract = sql_cursor.fetchone()
    num = '{:06.0f}'.format(int(num_extract[0]))
    proximo_num = int(num_extract[0])+1
    este_ano = 2020

    if int(num)<10:
        num_processo = "SE" + str(num) + "/" + str(este_ano)
        sql_cursor.execute("UPDATE settings SET cont_num_processo=%s", (proximo_num,))
        conn.commit()

    return num_processo

def ver_dados_envios():
	munic = session.get('munic', None)
	sql_cursor.execute("SELECT anoanalise, numprocesso, reqtipo, situacao, indice  FROM envio_preview WHERE mun=%s ORDER BY anoanalise DESC", (munic,))
	data=[]
	for row in sql_cursor:
		data.append(row)
	return data

def ver_addlock():
	sql_cursor.execute("SELECT addlock FROM settings")
	add_lock = sql_cursor.fetchone()
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

		sql_cursor.execute("SELECT MUN FROM UserAuth WHERE username=%s", (username,))
		municipio = sql_cursor.fetchone()
		sql_cursor.execute("SELECT username FROM UserAuth WHERE username=%s", (username,))
		UsernameData = sql_cursor.fetchone()
		sql_cursor.execute("SELECT password FROM UserAuth WHERE username=%s", (username,))
		PasswordData = sql_cursor.fetchone()
		sql_cursor.execute("SELECT type FROM UserAuth WHERE username=%s", (username,))
		TypeofUser	= sql_cursor.fetchone()

		#Caso o usuario nao esteja na base de dados, redireciona para uma pagina de login falhou
		if UsernameData == None or PasswordData == None:
			return render_template("loginfail.html")

		#Caso contrário, realiza o login na página certa
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
		sql_cursor.execute("SELECT reqcheck FROM res_urb_data WHERE ano_analise=%s AND mun=%s", (este_ano, munic))
		req_check = sql_cursor.fetchone()
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
		sql_cursor.execute("INSERT INTO res_urb_data(mun, ano_base, ano_analise, reqcheck) VALUES (%s, %s, %s, 'Verdadeiro')", (munic,), (ano_base,), (este_ano,))
		sql_cursor.execute("INSERT INTO envio_preview(mun, anoanalise, numprocesso, reqtipo, situacao, indice) VALUES (%s, %s, %s,'UC + RS', 'Novo', '0')",(munic,), (este_ano,), (num_processo,))
		conn.commit()
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
		if add_lock[0] == "Falso":
			sql_cursor.execute("UPDATE settings SET addlock=%s", ("Verdadeiro",))
			conn.commit()
		else:
			sql_cursor.execute("UPDATE settings SET addlock=%s", ("Falso",))
			conn.commit()
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


#if __name__ == "__main__":
#	app.run(debug=True)
