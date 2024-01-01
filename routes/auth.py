import traceback
from app import app
from flask import render_template, redirect, session, flash
from lib.server import validate_form_fields, MissingFieldException
from models.settings import Settings
from models.user import User
from lib.email import EmailException, send_verify_email, send_login_email
from sqlite3 import IntegrityError

@app.route('/register', methods=['GET'])
def register_get():
    allow_registration = Settings.get('allow_registration')
    return render_template('register.html', allow_registration=allow_registration)

@app.route('/register', methods=['POST'])
def register_post():
    if not Settings.get('allow_registration'):
        return 'Registrations are closed.', 403
    try:
        email_address, = validate_form_fields(['email_address']).values()
        user = User(email_address=email_address)
        user.generate_login_token()
        user.save()
        send_verify_email(user)
        message = "Check your email for the verification link."
        flash(message)
        return redirect('/login', code=303)
    except EmailException:
        message = "An error occurred while sending the verification email."
        flash(message)
        return redirect('/register', code=303)
    except IntegrityError:
        message = "That email address is already registered."
        flash(message)
        return redirect('/register', code=303)
    except MissingFieldException as e:
        message = str(e)
        flash(message)
        return redirect('/register', code=303)
    except Exception as e:
        message = "An unexpected error occurred."
        flash(message)
        return redirect('/register', code=303)

@app.route('/login', methods=['GET'])
def login_get():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    try:
        email_address, = validate_form_fields(['email_address']).values()
        user = User.get_by_email_address(email_address)
        if user is None:
            message = "Check your email for the login link. If you didn't receive it after a few minutes, you may not have an account registered with this email address."
            flash(message)
            return redirect('/register', code=303)
        user.generate_login_token()
        user.save()
        send_login_email(user)
        message = "Check your email for the login link. If you didn't receive it after a few minutes, you may not have an account registered with this email address."
        flash(message)
        return redirect('/login', code=303)
    except EmailException:
        message = "An error occurred while sending the login email."
        flash(message)
        return redirect('/register', code=303)
    except MissingFieldException as e:
        message = str(e)
        flash(message)
        return redirect('/register', code=303)
    except:
        print(traceback.format_exc())
        message = "An unexpected error occurred."
        flash(message)
        return redirect('/register', code=303)

@app.route('/logout', methods=['GET'])
def logout_get():
    session.pop('user_id', None)
    return redirect('/login', code=303)

@app.route('/auth/<token>', methods=['GET'])
def verify_token(token):
    user = User.login(token)
    if not user:
        return redirect('/login', code=303)
    # Create a session
    session['user_id'] = user.id
    return redirect('/', code=303)
