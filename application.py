import os
import requests
from RegistrationForm import *
from LoginForm import *

from flask import Flask, render_template, request, session, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = "hhhhhh7788@@@77@4llh55))"

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/search", methods=["POST"])
def search():
    text=request.form.get("searchText")
    text='%'+text+'%'
    results = db.execute("SELECT * FROM books WHERE (isbn LIKE :text) OR (title LIKE  :text) OR (author LIKE :text) LIMIT 100",
            { "text": text })


    return render_template("search.html", results=results)



@app.route("/")



def index():

    books = db.execute("SELECT * FROM books").fetchmany(50)
    return render_template("index.html", books=books)

@app.route("/rating", methods=["GET","POST"])
def rating():

    return render_template("rating.html",)

@app.route("/yourreview", methods=["GET","POST"])
def review():
    avrg=0
    if request.method == "POST":
        review = request.form.get("review")
        rating=request.form.get("rating[rating]")

        db.execute("INSERT INTO reviews (review_isbn, review_username, review, rating) VALUES (:review_isbn, :review_username, :review, :rating)",
                    {"review_isbn":session["book_isbn"], "review_username":session["username"],"review" :review,"rating" :rating})
        db.commit()
        session['reviewed']=145


        return render_template("book.html", avrg=avrg, review=review, rating=rating)



    return render_template("book.html", avrg=avrg)

@app.route("/logout", methods=["GET","POST"])
def logout():
    session.pop('username', None)
    return render_template("logout.html",)


@app.route("/login", methods=["GET","POST"])
def login():
    form1 = LoginForm(request.form)
    if session.get("username") is None:

        if request.method == 'POST' and form1.validate():
            username=form1.username.data
            password=form1.password.data

            u=db.execute("SELECT * FROM users WHERE username = :username and psw =:password", {"username": username, "password": password}).fetchone()
            session['username']=username
            if u is None:
                flash(u"Either username or password is worng", 'incorrect')
                return render_template('login.html', form=form1)
            else:
                session['username']=username
                return render_template('sucess.html', username=form1.username.data, password=form1.password.data )

    return render_template("login.html", form=form1)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if session.get("username") is None:

        if request.method == 'POST' and form.validate():
            username=form.username.data

            email=form.email.data
            password=form.password.data
            name=form.name.data
            u=db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
            e=db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone()
            if u is not None:
                flash(u"That username is already taken, please choose another", 'user')
                return render_template('register.html', form=form)


            elif e is not None:
                flash(u"That email is already use please choose another", 'email')
                return render_template('register.html', form=form)

            else:
                db.execute("INSERT INTO users (username, psw, email, name) VALUES (:username, :password, :email, :name)",
                            {"username": username, "password": password, "email": email, "name": name})
                db.commit()

            #db_session.add(user)

            return render_template('sucess.html', username=form.username.data )
        else:
           return render_template('register.html', form=form)
    else:
        return render_template('sucess.html', username=session["username"] )


@app.route("/ratingshow", methods=["GET", "POST"])
def ratingshow():
         if request.method == "POST":
            rating= request.form.get("rating[rating]")


         return render_template("ratingshow.html", rating=rating)

"""@app.route("/register/sucess", methods=["GET", "POST"])
def sucess():

         if request.method == "POST":
            return render_template("sucess.html", email= request.form['psw'])"""

@app.route("/<int:book_id>")
def book(book_id):





    session.pop('reviewed', None)
    session.pop('reviewes', None)
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()

    if book is None:
        return render_template("error.html", message="No such book.")
    else:
        session['book_title']=book.title
        session['book_isbn']=book.isbn
        reviews = db.execute("SELECT * FROM reviews WHERE review_isbn = :isbn", {"isbn": book.isbn}).fetchall()

        if reviews is not None:
            session['reviews']=[]
            for review in reviews:
                re=review.review
                session['reviews'].append(re)




    if "username" in session:
        r = db.execute("SELECT * FROM reviews WHERE review_isbn = :isbn and review_username= :username", {"isbn": book.isbn,"username":session["username"] }).fetchone()
        if r is not None:
            session['reviewed']=1


    """res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Ve44OwUOVU2PJIzwb8NYCQ", "isbns": book.isbn})
    if res.status_code == 404:
        avrg="No goodreads review available"
    else:
        data=res.json()
        avrg=data["books"][0]["average_rating"] """
    avrg=0

    return render_template("book.html", avrg=reviews    )
