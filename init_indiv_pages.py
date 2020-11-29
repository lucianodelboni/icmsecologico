from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def test():
	Plano = "Plano Municipal de Resíduos Sólidos de Bonito."
	checkboxstatus = "checked"
	if request.method =='POST':
		print(request.form.getlist('firstcheckbox'))

		return 'Done'
	return render_template("Test_userext_envios_novo.html", plano=Plano, checkboxstatus=checkboxstatus)


if __name__ == "__main__":
	app.run(debug=True)

