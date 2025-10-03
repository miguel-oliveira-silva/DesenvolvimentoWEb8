from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask import request
from flask import make_response
from flask import redirect, url_for, flash, session
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

app.config['SECRET_KEY'] = "Chave forte"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

class NameForm(FlaskForm):
    name = StringField("What is your name?", validators = [DataRequired()])
    role = SelectField("Role?:", choices = [('Administrator', 'Administrator'), ('Moderator', 'Moderator'), ('User', 'User')], validators = [DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    usuario = StringField('Usuário ou e-mail', validators = [DataRequired()], render_kw={"placeholder": "Usuário ou e-mail"})
    senha = PasswordField('Informe a sua senha', validators = [DataRequired()], render_kw={"placeholder": "Informe a sua senha"})
    submit = SubmitField('Enviar')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

@app.route('/', methods=['GET','POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user_role = Role.query.filter_by(name = form.role.data).first()
            user = User(username=form.name.data, role = user_role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    usuarios = User.query.all()
    funcoes = Role.query.order_by(Role.name).all()
    qtdUsuarios = User.query.count()
    qtdFuncoes = Role.query.count()
    return render_template('index.html', form=form, nome=session.get('name'), known=session.get('known', False), usuarios = usuarios, funcoes = funcoes, qtdUsuarios = qtdUsuarios, qtdFuncoes = qtdFuncoes)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['usuario'] = form.usuario.data
        return redirect(url_for('loginResponse'))
    return render_template('login.html', form = form)

@app.route('/loginResponse')
def loginResponse():
    return render_template('loginResponse.html', usuario = session.get('usuario'))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', nome=name)

@app.route('/user/')
def userr():
    return render_template('user.html')

@app.route('/rotainexistente')
def rotainexistente():
    return render_template('404.html')

@app.route('/user/<nome>/<prontuario>/<instituicao>')
def identificacao(nome, prontuario, instituicao):
    return render_template('user.html', nome=nome, prontuario=prontuario, instituicao=instituicao)

@app.route('/contextorequisicao/<nome>')
def contextorequisicao(nome):
    requisicao = request.headers.get('User-Agent')
    IP = request.remote_addr
    host = request.host
    return render_template('contextorequisicao.html', nome=nome, requisicao=requisicao, IP=IP, host=host)
