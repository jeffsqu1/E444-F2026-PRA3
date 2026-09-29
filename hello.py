from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string' # Could be anything
bootstrap = Bootstrap(app)
moment = Moment(app)

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = StringField(
        'What is your UofT email address?',
        validators=[DataRequired()],
        render_kw={
            'pattern': '.*@.*',
            'oninvalid': "this.setCustomValidity('Please include an @ in the email address.')",
            'oninput': "this.setCustomValidity('')",
        },
    )
    submit = SubmitField('Submit')

    
@app.route('/', methods=['GET', 'POST'])
def index():
    # name = None
    form = NameForm()
    if request.method == 'POST' and request.form.get('name'):
        old_name = session.get('name')
        if old_name is not None and old_name != request.form['name']:
            flash('Looks like you have changed your name!')
        session['name'] = request.form['name']

    if form.validate_on_submit():
        old_email = session.get('email')
        email_address = form.email.data
        if old_email != email_address:
            flash('Looks like you have changed your email!')
        if 'utoronto' in email_address.lower():
            session['email'] = email_address
            session['username'] = email_address.split('@', 1)[0]
            session.pop('chat_name', None)
            return redirect(url_for('chat'))
        else:
            session.pop('email', None)
            session.pop('username', None)
        return redirect(url_for('index'))

    return render_template('index.html', form=form, name=session.get('name'), username=session.get('username'), email_address=session.get('email'), current_time=datetime.utcnow())

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('chat.html', username=session.get('username'))

    message = (request.get_json(silent=True) or {}).get('message', '').strip()
    lower_message = message.lower()
    if lower_message.startswith('my name is '):
        chat_name = message[11:].strip(' .!?') # get name without punctuation
        session['chat_name'] = chat_name
        reply = f'Nice to meet you, {chat_name}!'
    elif 'what is my name' in lower_message:
        chat_name = session.get('chat_name') # saved name from chat
        reply = f'Your name is {chat_name}.' if chat_name else "I don't know your name yet."
    elif 'hello' in lower_message or 'hi' in lower_message:
        reply = 'Hello!'
    else:
        reply = "I don't understand."

    return {'reply': reply}

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name, current_time=datetime.utcnow())