from flask import session, redirect
import functools
from lib.supabase import supabase

# From https://blog.teclado.com/protecting-endpoints-in-flask-apps-by-requiring-login/
def with_auth(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        print("with_auth")
        print(session)
        res = supabase.auth.get_user(session["access_token"])
        print(res)
        if res.user is None:
            return redirect("/login", code=303)
        return func(*args, **kwargs)
    return secure_function
