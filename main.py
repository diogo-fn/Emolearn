import cv2
import os
import time
from datetime import datetime
import random
import sqlite3
from EmotionRecognition import EmotionRecognition
import keras
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from keras.models import load_model
from PIL import Image
import io
import numpy as np
import flask
from flask import Flask, escape, request, render_template, redirect, url_for, Response, session, flash, jsonify, json, jsonify
from flask_bootstrap import Bootstrap
from forms import RegistrationForm, LoginForm, AddPatient
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
import json
from webcam import Webcam
SECRET_KEY = os.urandom(32)

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'

csrf = CSRFProtect(app)
db = SQLAlchemy(app)
Bootstrap(app)
pred = ""
percentage = 0
rating = ""
id_paciente = 0
id_terapeuta = 0
resultado_id = 0


class Terapeutas(db.Model):
    __tablename__ = 'Terapeutas'
    id = db.Column('id_terapeuta', db.Integer, primary_key=True)
    Nome = db.Column(db.String(80), unique=False, nullable=False)
    Email = db.Column(db.String(80), unique=False, nullable=False)
    Password = db.Column(db.String(120), unique=False, nullable=False)
    pacientes = db.relationship("Paciente")
    sessoes = db.relationship("Sessao")


"""
def __init__(self, nome, Email, Pass):
    self.Nome = nome
    self.Email = Email
    self.Password = Pass

"""


class Paciente(db.Model):
    __tablename__ = 'Paciente'
    id = db.Column('id_paciente', db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    morada = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    telefone = db.Column(db.String(80), nullable=False)
    terapeuta = db.Column(db.Integer, db.ForeignKey(
        'Terapeutas.id_terapeuta'), nullable=False)
    pacientes_sessao = db.relationship('Sessao')


"""
def __init__(self, name, morada, email, telefone):
    self.nome = name
    self.morada = morada
    self.email = email
    self.telefone = telefone

"""


class Sessao(db.Model):
    __tablename__ = 'Sessao'
    id = db.Column('id_sessao', db.Integer, primary_key=True)
    Data_Hora = db.Column(db.DateTime, nullable=False)
    id_resultados = db.Column(db.Integer, db.ForeignKey('Resultados.id_resultados'),
                              nullable=False)

    id_paciente = db.Column(db.Integer, db.ForeignKey('Paciente.id_paciente'),
                            nullable=False)

    id_terapeuta = db.Column(db.Integer, db.ForeignKey('Terapeutas.id_terapeuta'),
                             nullable=False)

    """
     id_terapeutas = db.Column(db.Integer, db.ForeignKey('Terapeutas.id_terapeuta'),
                              nullable = False)
    terapeutas_sessao = db.relationship('Paciente', backref='Sessão')
"""


"""
def __init__(self, Data_Hora):
    self.Data_Hora = Data_Hora
"""


class Resultados(db.Model):
    __tablename__ = 'Resultados'
    id = db.Column('id_resultados', db.Integer, primary_key=True)
    tipo_de_resultado = db.Column(db.String(50), nullable=False)
    percentagem = db.Column(db.Integer, nullable=False)
    resultados_sessao = db.relationship('Sessao')


"""
def __init__(self, name, Email, Pass):
    self.Nome = name
    self.Email = Email
    self.Password = Pass
"""

# função index
@app.route('/')
def index():
    return render_template('index.html')

# setup da webcam
def gen(webcam):
    global pred
    while True:

        pred, frame = webcam.get_frame()
        #  print(pred)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'
               # + b'Content-Type: text/html\r\n\r\n' + pred + b'\r\n\r\n'
               )
        # yield ('--frame\r\n''Content-Type: text/html\r\n\r\n'+pred)

# Função do video feed da webcam
@app.route('/video_feed/')
def video_feed():
    return Response(gen(Webcam()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Função de returnar previsão da emoção
@app.route('/prediction/')
def prediction():
    return jsonify(predict=pred)

# Função de registo do terapeuta
@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if request.method == 'POST':

            terapeuta = Terapeutas(
                Nome=request.form['nome'], Email=request.form['email'], Password=request.form['password'])

            db.session.add(terapeuta)
            db.session.commit()
            flash('Registo Sucedido')
            return redirect(url_for('Login'))

    return render_template('Registo_Terapeuta.html', form=form)

# Função de login
@app.route('/Login/', methods=['GET', 'POST'])
def Login():
    form = LoginForm()

    if form.validate_on_submit():

        if request.method == "POST":

            email = request.form["email"]
            password = request.form["password"]
            terapeuta = Terapeutas.query.filter_by(
                Email=request.form['email'], Password=request.form['password']).first()
            if terapeuta:
                if terapeuta.Password == password:
                    print(terapeuta)
                    session['Terapeuta'] = terapeuta.Nome
                    return redirect(url_for('index'))
                else:
                    flash("email errado ou password errada")
                    return redirect(url_for('Login'))

    return render_template('Login.html', form=form)

# Função de logout
@app.route("/logout/")
def logout():
    session.pop("Terapeuta", None)
    flash("Sessão Fechada!")
    return redirect(url_for('index'))

# @app.route("/pacientes/", methods=["GET", "POST"])
@app.route("/pacientes/")
def pacientes():
    global id_terapeuta
    form1 = AddPatient()
    terapeuta = session['Terapeuta']
    terapeuta_query = db.session.query(Terapeutas).filter(
        Terapeutas.Nome == terapeuta).first()
    id_terapeuta = terapeuta_query.id
    print(terapeuta)
    print(id_terapeuta)
    # if request.method == "POST":
    pacientes = Paciente.query.with_entities(Paciente.id,
                                             Paciente.nome, Paciente.morada, Paciente.morada, Paciente.email, Paciente.telefone)
    return render_template('pacientes.html', pacientes=pacientes, form1=form1, terapeuta=terapeuta)

# Função de adicionar pacientes
@app.route("/add_patients/<string:name>", methods=["GET", "POST"])
def add_patients(name):
    form = AddPatient()
    t = Terapeutas()
    terapeuta_query = db.session.query(Terapeutas).filter(
        Terapeutas.Nome == name).first()
    if form.validate_on_submit():
        if request.method == "POST":
            print(terapeuta_query.id)
           # paciente = Paciente(
            #    nome=request.form['nome'], morada=request.form['morada'], email=request.form['email'], telefone=request.form['telefone'], Terapeutas=Terapeutas(Nome=terapeuta.Nome))
            p = Paciente(nome=request.form['nome'], morada=request.form['morada'],
                         email=request.form['email'], telefone=request.form['telefone'], terapeuta=terapeuta_query.id)

           # t.paciente.append(p)
            db.session.add(p)
            db.session.commit()
            return redirect(url_for('pacientes'))

# Função de remover pacientes
@app.route("/remove_patients/<int:id>", methods=['GET', 'POST'])
def remove_patients(id):
    print(id)
    p = Paciente.query.filter_by(id=id).first()
    print(p)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('pacientes'))

# Função de obter sessoes de um paciente
@app.route("/get_sessions/<int:id>", methods=['GET', 'POST'])
def get_sessions(id):
    print(id)
    sessoes = db.session.query(Sessao, Resultados).join(
        Sessao).filter(Sessao.id_paciente == id).filter(Sessao.id_resultados == Resultados.id).all()

    print(sessoes)
    return render_template('ConsultarPaciente.html', sessoes=sessoes)

# Função de iniciar a sessão de um paciente
@app.route("/sessao/<int:id>", methods=["GET", "POST"])
def sessao(id):
    global id_paciente
    paciente_query = db.session.query(
        Paciente).filter(Paciente.id == id).first()
    id_paciente = paciente_query.id
    return render_template('Sessao.html')

# Função de submeter resultados de um paciente
@app.route('/submeterresultados/', methods=["GET", "POST"])
def submeterresultados():
    global rating
    global percentage
    global resultado_id
    json_string = request.get_json(force=True)
    value = int(json_string['Count'])
    if request.method == "POST":
        percentage = round(((value / 10) * 100))
        if(percentage == 0 or percentage == 10 or percentage == 20):
            rating = "Muito Fraco"
        elif(percentage == 30 or percentage == 40):
            rating = "Fraco"
        elif(percentage == 50 or percentage == 60):
            rating = "Médio"
        elif(percentage == 70 or percentage == 80):
            rating = "Bom"
        elif(percentage == 90 or percentage == 100):
            rating = "Muito Bom"
        resultado = Resultados(
            tipo_de_resultado=rating,
            percentagem=percentage)
        db.session.add(resultado)
        db.session.commit()
        resultado_id = resultado.id
        return redirect(url_for('resultados'))

# Função de retornar o resultado obtido pelo o paciente
@app.route('/resultados/', methods=["GET", "POST"])
def resultados():
    print(rating)
    print(percentage)
    return render_template('Resultado.html', percentage=percentage, rating=rating)

# Função de submeter a sessao na base de dados
@app.route('/submetersessao/', methods=["GET", "POST"])
def submetersessao():
    if request.method == "POST":
        s = Sessao(Data_Hora=datetime.now(),
                   id_resultados=resultado_id, id_paciente=id_paciente, id_terapeuta=id_terapeuta)

        db.session.add(s)
        db.session.commit()
        return redirect(url_for('pacientes'))


if __name__ == "__main__":
    app.run(host='127.0.0.1')
