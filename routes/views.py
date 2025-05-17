from main import app
from flask import render_template


# rotas de templates
@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/nutricao")
def nutricao():
    return render_template("nutricao.html")

@app.route("/nutricao/registrar-refeicao")
def regRef():
    return render_template("registrar-refeicao.html")

@app.route("/nutricao/plano-alimentar")
def planAli():
    return render_template("plano-alimentar.html")

@app.route("/nutricao/bioimpedancia")
def bioimp():
    return render_template("bioimpedancia.html")

@app.route("/nutricao/chefbot")
def chefb():
    return render_template("chefbot.html")

@app.route("/nutricao/refeicao")
def ref():
    return render_template("refeicao.html")

@app.route("/nutricao/metas")
def metas():
    return render_template("metas.html")
