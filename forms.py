from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import (StringField,
                     TextAreaField,
                     SubmitField,
                     PasswordField,
                     DateField,
                     SelectField, SubmitField, validators)
from wtforms.validators import (DataRequired,
                                Email,
                                EqualTo,
                                Length,
                                URL)


class RegistrationForm(FlaskForm):

    nome = StringField('Nome:', [validators.Length(
        min=6, max=50)])
    email = StringField('Email:     ', [validators.Length(
        min=6, max=50)])
    password = PasswordField('Password:', [validators.Length(
        min=6, max=50),
        DataRequired(message="Por favor insira uma password.")
    ])
    confirmPassword = PasswordField('Repetir Password', [validators.Length(
        min=6, max=50),
        EqualTo('password', message='Passwords têm de ser iguais.')
    ])


class LoginForm(FlaskForm):
    email = StringField('Email:', [validators.Length(min=6, max=50)])

    password = PasswordField('Password:', [
        DataRequired(message="Por favor insira uma password."),
    ])


class AddPatient(FlaskForm):

    nome = StringField('Nome', [validators.Length(min=6, max=50)])
    morada = StringField('Morada:', [validators.Length(min=6, max=50)])
    email = StringField('Email:', [validators.Length(min=6, max=50)])
    telefone = StringField('Telefone:', [validators.Length(min=6, max=50)])
    Add = SubmitField('Adicionar Paciente')


