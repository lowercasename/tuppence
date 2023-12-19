import secrets

# Currency is stored in the database as an integer in cents, but comes in as a string
def currency_string_to_database(value):
    return int(float(value) * 100)

def currency_database_to_string(value):
    if value < 0:
        return f'-£{abs(value) / 100:,.2f}'
    return f'£{value / 100:,.2f}'

def generate_login_token():
    return secrets.token_hex(32)

def generate_password():
    return secrets.token_hex(32)
