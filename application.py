import os
import requests

import sqlalchemy 
from RegistrationForm import *
from LoginForm import *

from flask import Flask, render_template, request, session, flash, jsonify, url_for, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = "hhhhhh7788@@@77@4llh5sjdgsdstfsw"

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
    try:
        books = db.execute("SELECT * FROM books ORDER BY av_rating DESC").fetchmany(50)
        return render_template("index.html", books=books)
    except sqlalchemy.exc.OperationalError:
        return render_template("error.html", message="Please check your internet connection")
    
    

@app.route("/rating", methods=["GET","POST"])
def rating():

    return render_template("rating.html",)

@app.route("/yourreview", methods=["POST"])
def review():
    
    if request.method == "POST":
        review = request.form.get("review")
        rating=request.form.get("rating[rating]")
        book_id1=request.form.get("book_id")
        book_isbn=request.form.get("book_isbn")

        db.execute("INSERT INTO reviews (review_isbn, review_username, review, rating) VALUES (:review_isbn, :review_username, :review, :rating)",
                    {"review_isbn":book_isbn, "review_username":session["username"],"review" :review,"rating" :rating})
        db.commit()
        session['reviewed']=145


        return redirect(url_for("book", book_id=book_id1))



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
       
        reviews1 = db.execute("SELECT * FROM reviews WHERE review_isbn = :isbn", {"isbn": book.isbn}).fetchall()
        
        r=0
        if reviews1 is not None:
            session['reviews']=[]
            for review in reviews1:
                r=1
                re=review.review
                session['reviews'].append(re)
        if r==1:
            av_rating=0
            n=0
            for rating in reviews1:
                n=n+1
                av_rating=av_rating + rating.rating
            av_rating=(av_rating/n)
            
            db.execute("UPDATE books SET av_rating = :av_rating WHERE id= :id", {"av_rating" :av_rating, "id": book_id})
            db.commit()
            book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()



    if "username" in session:
        r = db.execute("SELECT * FROM reviews WHERE review_isbn = :isbn and review_username= :username", {"isbn": book.isbn,"username":session["username"] }).fetchone()
        if r is not None:
            session['reviewed']=1


    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Ve44OwUOVU2PJIzwb8NYCQ", "isbns": book.isbn})
    if res.status_code == 404:
        avrg="No goodreads review available"
    else:
        data=res.json()
        avrg=data["books"][0]["average_rating"] 
    
    

    return render_template("book.html", avrg=avrg, book=book, reviews= reviews1)
