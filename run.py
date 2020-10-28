import os
from flask import Flask, flash, render_template, redirect, request, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/tasks")
def tasks():
    tasks = list(mongo.db.tasks.find())
    return render_template("tasks.html", tasks=tasks)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    tasks = list(mongo.db.tasks.find(({"$text": {"$search": query}})))
    return render_template("tasks.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = session["user"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/new_task")
def new_task():
    return render_template("new_task.html", categories=mongo.db.categories.find())


@app.route("/insert_task", methods=["POST"])
def insert_task():
    tasks = mongo.db.tasks
    tasks.insert_one(
        {"task_name": request.form.get("task_name"),
         "category_name": request.form.get("category_name"),
         "task_description": request.form.get("task_description"),
         "due_date": request.form.get("due_date"),
         "is_urgent": request.form.get("is_urgent"),
         "created_by": session["user"]
         })
    return redirect(url_for("tasks"))


@app.route("/edit_task/<task_id>")
def edit_task(task_id):
    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    categories = mongo.db.categories.find()
    return render_template("edit_task.html", task=task, categories=categories)


@app.route("/update_task/<task_id>", methods=["POST"])
def update_task(task_id):
    tasks = mongo.db.tasks
    tasks.update({"_id": ObjectId(task_id)},
                 {"task_name": request.form.get("task_name"),
                  "category_name": request.form.get("category_name"),
                  "task_description": request.form.get("task_description"),
                  "due_date": request.form.get("due_date"),
                  "is_urgent": request.form.get("is_urgent"),
                  "created_by": session["user"]
                  })
    return redirect(url_for("tasks"))


@app.route("/delete_task/<task_id>")
def delete_task(task_id):
    tasks = mongo.db.tasks
    tasks.remove({"_id": ObjectId(task_id)})
    return redirect(url_for("tasks"))


@app.route("/categories")
def categories():
    return render_template("categories.html", categories=mongo.db.categories.find())


@app.route("/edit_category/<category_id>")
def edit_category(category_id):
    return render_template("edit_category.html", category=mongo.db.categories.find_one({"_id": ObjectId(category_id)}))


@app.route("/update_category/<category_id>", methods=["POST"])
def update_category(category_id):
    mongo.db.categories.update({"_id": ObjectId(category_id)},
                               {"category_name": request.form.get("category_name")})
    return redirect(url_for("categories"))


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    return redirect(url_for("categories"))


@app.route("/insert_category", methods=["POST"])
def insert_category():
    categories = mongo.db.categories
    category_doc = {"category_name": request.form.get("category_name")}
    categories.insert_one(category_doc)
    return redirect(url_for("categories"))


@app.route("/add_category")
def add_category():
    return render_template("add_category.html")


app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=False)
