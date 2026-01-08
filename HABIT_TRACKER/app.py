from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///habit.db"
app.config["SECRET_KEY"] = "supersecretkey"

db.init_app(app)

with app.app_context():
    db.create_all()
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/auth/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users and check_password_hash(users[email], password):
            session["user"] = email
            return redirect(url_for("home"))
        else:
            return "Invalid email or password"

    return render_template("auth/login.html")
@app.route("/auth/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users:
            return "User already exists"
        
        users[email] = generate_password_hash(password)
        session["user"] = email
        return redirect(url_for("home"))

    return render_template("auth/register.html")
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
