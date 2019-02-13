

#allows us to access paths on our file system relative to our project directory.
import os

#import flask
from flask import Flask, render_template, request, redirect

from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))

#prefix to tell SQLAlchemy which database engine we are using.

database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdatabase.db"))

#initialize a flask application instance, 
#...passing in __name__ argument that helps flask to determine the root path of the application,
# ... so that it can find resource files relative to the location of the application.

app = Flask(__name__)

#we tell our web application where our database will be stored

app.config["SQLALCHEMY_DATABASE_URI"] = database_file

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#we initialize a connection to the database and keep this in the db variable:
#we will use this to interact with our database.

db = SQLAlchemy(app)

# a new class which inherits from a basic database model, provided by SQLAlchemy.
# This will also make SQLAlchemy create a table called book.
# which it will use to store our book objects 

class Book(db.Model):
    
    #we create an attribute of our book called tittle.book titles should be unique,every book should have a title,
    # title is the main way that we identify a specific book in our database(title is the primary_key) 
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)

    #we define how to represent our book object as a string.
    # This allows us to do things like print(book).
    def _repr_(self):

        return "<Title: {}>".format(self.title)

#decorator that maps the main part of our application (/) to the home() function.
#allow GET and POST requests.

@app.route("/", methods=["GET", "POST"]) #this will solve the "method not allowed" error that we saw if we tried submitting the form before

#define a function that simply returns a static string

def home():

    books = None
    #we check if someone just submitted the form

    if request.form:
        try: 

            #when we receive input from the user..
            #we grab the title from the form and use it to initialize a new Book object.
            #we save this new Book to a variable named book 
            book = Book(title=request.form.get("title"))
        
            #We then add the book to our database
            db.session.add(book)

            #we commit our changes to persist them
            db.session.commit()

        except Exception as e:
            
            db.session.rollback()

            print("Failed to add book")

            print(e) 

    #this is what will be displayed to the user when they visit our page.
    books = Book.query.all()

    #pass the books through to our front-end temlate
    return render_template("home.html", books=books)


@app.route("/update", methods=["POST"])

def update():

    try:

        # Gets the old and updated title from the form

        newtitle = request.form.get("newtitle")

        oldtitle = request.form.get("oldtitle")

        #Fetches the book with the old title from the databases
        book = Book.query.filter_by(title=oldtitle).first()

        #Updates that book's title to the new title
        book.title = newtitle

        #Saves the book to the database
        db.session.commit()

    except Exception as e:
        
        print("Couldn't update book title")

        print(e)

#redirect the user to the main page

    return redirect("/")

#DELETE ROUTE....looks the same to /update route

@app.route("/delete", methods=["POST"])

def delete():

    title = request.form.get("title")

    book = Book.query.filter_by(title=title).first()

    db.session.delete(book)

    db.session.commit()

    return redirect("/")

#we run the application behind an if guard.this ensures that we don't start up web servers 

#...if we ever import this script into another one.

if __name__ == "__main__":

    app.run(debug=True)

