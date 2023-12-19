from flask import session, redirect
import functools

# From https://blog.teclado.com/protecting-endpoints-in-flask-apps-by-requiring-login/
def with_auth(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login", code=303)
        return func(*args, **kwargs)
    return secure_function
