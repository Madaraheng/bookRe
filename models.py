from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),nullable = False)
    password = db.Column(db.Text,nullable =False)

class books(db.Model):
    __tablename__ = "books1"
    id = db.Column(db.Integer,primary_key=True)
    isbn = db.Column(db.String(20),nullable=False)
    title = db.Column(db.String(100),nullable=False)
    author = db.Column(db.String(100),nullable=False)
    year   = db.Column(db.String(20),nullable=False)
    
    Comment = db.relationship("comments",backref ="book",lazy=True)

    def add_comment(self,comment,comment_isbn):
        c = comments(comment=comment,comment_isbn=self.isbn)
        db.session.add(c)
        db.session.commit()

class comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer,primary_key=True)
    #add , autoincrement  = False if we want to stop autoincrement
    comment = db.Column(db.Text,nullable=False)
    comment_isbn = db.Column(db.Integer, db.ForeignKey("books1.isbn"), nullable = False)
