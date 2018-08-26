from flask import Flask,request,session,redirect,render_template,logging,url_for,flash
from passlib.hash import sha256_crypt
from models import *
from functools import wraps
from sqlalchemy import or_
import requests
 
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="postgres://lnhoohloogqvsw:628af073f9faa55f5ee434add0b3b45dd8eaf9c66270781be8efb43cc3661b9a@ec2-174-129-236-147.compute-1.amazonaws.com:5432/d5ga5nrqun3dl"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

@app.route("/") 
def main():
    return render_template("home.html")

# register route
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST": 
        #get the information from the user
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        secure_pass = sha256_crypt.encrypt(str(password))
        
        #make sure that it not the same user
        username_data  = users.query.filter_by(username = username).first()
        if username_data is None and password == confirm:
            user = users(username=username,password = secure_pass)
            db.session.add(user)
            db.session.commit()
            flash("You are registed.","success")
            return redirect(url_for("login"))
        
        if username_data is not None:
            flash("username exsits","danger")
            return render_template("register.html")


        #make sure the password match
        if password is not confirm:
            flash("Password not match","danger")
            return render_template("register.html")

            
    return render_template("register.html")
#login route
@app.route("/login",methods=["GET","POST"])

def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        data = users.query.filter_by(username = username).first()
        if data is None:
            flash("No such user","danger")
            return render_template("login.html")
        
        if data is not None and username == data.username:

            if sha256_crypt.verify(password,data.password):
                session["logged_in"]=True
                session["username"]= username
                flash("You are logged in","success")
                
                return redirect(url_for("book"))
            else:
                flash("Invalid password","danger")
                return render_template("login.html")


        
    return render_template("login.html")


def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash("Unauthorized , Please login","danger")
            return redirect(url_for('login'))
    return wrap

#logout
@app.route("/logout")
@is_logged_in

def logout():
    
    session.clear()
    flash("You are now logged out","success")
    return redirect(url_for("login"))

# book route
@app.route("/book",methods=["GET","POST"])
@is_logged_in

def book():
    if request.method=="POST":
        #get the information from the search 
        search = request.form.get("search")
        #query the book from the database
        book_data = books.query.filter(or_(books.author.like("%"+search+"%"),books.title.like("%"+search+"%"),books.isbn == search)).all()
        if book_data == []:
            flash("No book relate","danger")
            render_template("book.html")
        return render_template("book.html",book_data=book_data)


    return render_template("book.html")


@app.route("/book/<string:book_title>",methods=["GET","POST"])
@is_logged_in

def book_Detail(book_title):
    key =  "iTfh5Kar9Iu720qXQX1whA"
    bookDetail = books.query.filter_by(title= book_title).first()
    isbn = bookDetail.isbn
    
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data = res.json()
    new_data = {}
    for item in data["books"]:
        new_data.update(item)
    data["books"] = new_data
    averageRating = data['books']['average_rating']
    ratings_count = data['books']['work_ratings_count']
    

    if request.method=="POST":

    # get the comment for the user
      comment_data = request.form.get("comment")
    #insert comment into comment column
      bookDetail.add_comment(comment_data,isbn)

      
    #get the comment for database of each books 
    comment_book = bookDetail.Comment
      
      #return render_template("book_detail.html",bookDetail = bookDetail,averageRating = averageRating,ratings_count=ratings_count,comment_book=comment_book)

    return render_template("book_detail.html",bookDetail = bookDetail,averageRating = averageRating,ratings_count=ratings_count,comment_book=comment_book)

if __name__ == "__main__":
    with app.app_context():
         app.secret_key='1256090257Vuth'

         app.run(debug=True)
