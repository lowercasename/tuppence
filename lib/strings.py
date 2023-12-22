import secrets

# Currency is stored in the database as an integer in cents, but comes in as a string
def currency_string_to_database(value):
    return int(float(value) * 100)

def currency_database_to_string(value: int, floor=False):
    if value < 0:
        if floor:
            return f'-£{abs(value) / 100:,.0f}'
        return f'-£{abs(value) / 100:,.2f}'
    if floor:
        return f'£{value / 100:,.0f}'
    return f'£{value / 100:,.2f}'

def generate_login_token():
    return secrets.token_hex(32)
