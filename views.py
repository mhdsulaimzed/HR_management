import flask
import models
from sqlalchemy import select, join, func


app = flask.Flask("hrsw")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///hrsw"
app.secret_key = "abc"

db = models.SQLAlchemy(model_class=models.Base)
db.init_app(app)


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/employees")
def employees():
    qs = db.select(models.Employee).order_by(models.Employee.fname)
    users = db.session.execute(qs).scalars()
    # user_list = [{"id":user.id,"fname":user.fname,"lname":user.lname,"title":user.title.title,"email":user.email,"phone":user.phone}for user in users]
    return flask.render_template("employee.html", users=users)


@app.route("/employee/<int:id>")
def employee_details(id):
    qs1 = db.select(models.Employee).order_by(models.Employee.fname)
    users = db.session.execute(qs1).scalars()

    if id < 1 or id > len(list(users)):
        flask.flash("Employee Not Found")
        id = 1

    query_for_leaves = (
        db.select(func.count(models.Employee.id))
        .join(models.Leave, models.Employee.id == models.Leave.employee_id)
        .filter(models.Employee.id == id)
    )
    leave = db.session.execute(query_for_leaves).scalar()

    qs2 = db.select(models.Employee).where(models.Employee.id == id)
    user = db.session.execute(qs2).scalar()
    user_list = {
        "id": user.id,
        "fname": user.fname,
        "lname": user.lname,
        "title": user.title.title,
        "email": user.email,
        "phone": user.phone,
        "max_leaves": user.title.max_leaves,
        "leave_taken": leave,
    }
    return flask.jsonify(user=user_list)

def get_leave_data(id):
    print("yes")
    query_for_leaves = (
        db.select(func.count(models.Employee.id))
        .join(models.Leave, models.Employee.id == models.Leave.employee_id)
        .filter(models.Employee.id == id)
    )
    leave = db.session.execute(query_for_leaves).scalar()
    print("yes2")

    qs2 = db.select(models.Employee).where(models.Employee.id == id)
    user = db.session.execute(qs2).scalar()
    print("yes3")
    data = {"leave_taken": leave,"max_leaves":user.title.max_leaves}
    return data


@app.route("/leave/<int:id>", methods=["GET", "POST"])
def add_leave(id):
    leaves = get_leave_data(id)
    print('kkkkkkkkkk',leaves)


    if flask.request.method == "POST":
        if leaves['leave_taken'] < leaves['max_leaves']:
           
            date = flask.request.form["date"]
            reason = flask.request.form["reason"]
            s = models.Leave(employee_id=id, date=date, reason=reason)
            db.session.add(s)
            db.session.commit()
            flask.flash("Leave added successfully!")
            return flask.redirect(flask.url_for("employees"))
        else:
            flask.flash("Maximum Leave Limit attained added!")
            return flask.redirect(flask.url_for("employees"))


@app.route("/search", methods=["GET", "POST"])
def search_employee():
    if flask.request.method == "POST":
        employee_id = flask.request.form.get("employee_id")

        if employee_id:
            qs = db.select(models.Employee).where(models.Employee.id == employee_id)
            user = db.session.execute(qs).scalar()

            if user:
                return flask.redirect(flask.url_for("employee_details", id=user.id))
            else:
                flask.flash("Employee not found.")
        else:
            flask.flash("Please enter an employee ID.")

    return flask.render_template("search.html")


@app.route("/about")
def about():
    return flask.render_template("about.html")


if __name__ == "__main__":
    app.run()
   
    
    
