from flask import Flask, session, request
from datetime import datetime, timedelta
from dateutil import relativedelta
from dotenv import load_dotenv
import os
from lib.date import validate_month, validate_year
from lib.strings import currency_database_to_string
from lib.db import Database

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET')

db = Database("tuppence.db")
db.init_db()

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=45)

@app.context_processor
def inject_month_year():
    path = request.path
    month = validate_month(request.args.get('m'))
    year = validate_year(request.args.get('y'))
    current_datetime = datetime.strptime(f'{year}-{month}', '%Y-%m')
    current_label = current_datetime.strftime("%B %Y")
    next_month = current_datetime + relativedelta.relativedelta(months=1)
    next_label = next_month.strftime("%B %Y")
    next_url = f'{path}?m={next_month.month}&y={next_month.year}'
    if next_month > datetime.now():
        next_month = None
        next_label = None
        next_url = None
    previous_month = current_datetime - relativedelta.relativedelta(months=1)
    previous_label = previous_month.strftime("%B %Y")
    previous_url = f'{path}?m={previous_month.month}&y={previous_month.year}'

    # Other fields
    current_date = datetime.now()
    current_page = request.path
    return {
        'current_month': current_label,
        'next_month': next_label,
        'previous_month': previous_label,
        'next_url': next_url,
        'previous_url': previous_url,
        'current_date': current_date.strftime("%Y-%m-%d"),
        'current_page': current_page
    }

@app.template_filter('price')
def format_price(s):
    if s is None or s == '':
        return f'£0.00'
    return currency_database_to_string(int(s))

@app.template_filter('price_floor')
def format_price_floor(s):
    if s is None or s == '':
        return f'£0.00'
    return currency_database_to_string(int(s), floor=True)

@app.template_global('is_authenticated')
def is_authenticated():
    return 'user_id' in session

@app.template_filter('floor')
def floor(s):
    return int(s)

from routes import auth, overview, account, pot, transaction