import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

mongo = PyMongo(app)


@app.route("/")
@app.route("/tasks")
def tasks():
    return render_template("tasks.html", tasks=mongo.db.tasks.find())


@app.route("/new_task")
def new_task():
    return render_template("new_task.html", categories=mongo.db.categories.find())


@app.route("/insert_task", methods=["POST"])
def insert_task():
    tasks = mongo.db.tasks
    tasks.insert_one(request.form.to_dict())
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
                  "is_urgent": request.form.get("is_urgent")
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


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), port=int(
        os.environ.get("PORT")), debug=False)
