import os
from datetime import datetime
from flask import Flask, render_template, session
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(64), unique=True, index=True)
    subject = db.Column(db.String(64), unique=False, index=True)

    def __repr__(self):
        return '<Teacher %r>' % self.fullname


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

    fullname = StringField('Cadastre o novo Professor:', validators=[DataRequired()])
    choices = [('DSWA5', 'DSWA5'), ('GPSA5', 'GPSA5'), ('IHCA5', 'IHCA5'), ('IHCA5', 'IHCA5'), ('SODA5', 'SODA5'), ('PJIA5', 'PJIA5'), ('TCOA5', 'TCOA5'),]
    subject = SelectField('Disciplina associada:', choices=choices)

    submit = SubmitField('Enviar')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html', current_time=datetime.utcnow())

@app.route('/professores', methods=['GET', 'POST'])
def professores():
    form = NameForm()
    if form.validate_on_submit():
        fullname = form.fullname.data
        subject = form.subject.data

        teacher = Teacher.query.filter_by(fullname=fullname).first()

        if teacher is None:

            teacher = Teacher(fullname=fullname, subject=subject)
            db.session.add(teacher)
            db.session.commit()
            session['known'] = False

        else:

            teacher.subject = subject
            db.session.commit()
            session['known'] = True

        session['name'] = fullname
        session['subject'] = subject

    teachers = Teacher.query.all()

    return render_template('professores.html', form=form, known=session.get('known', False), teachers=teachers)


@app.route('/disciplinas', methods=['GET', 'POST'])
def disciplinas():
    return render_template('disciplinas.html')


@app.route('/alunos', methods=['GET', 'POST'])
def alunos():
    return render_template('alunos.html')
