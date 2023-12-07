import flask
import models
from sqlalchemy import select,join,func


app = flask.Flask("hrsw")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///hrsw"
app.secret_key="abc"

db = models.SQLAlchemy(model_class=models.Base)
db.init_app(app)



@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/employees")
def employees():
    qs = db.select(models.Employee).order_by(models.Employee.fname)
    users = db.session.execute(qs).scalars()
    return flask.render_template("employee.html",users=users)

@app.route("/employee/<int:id>")
def employee_details(id):
    qs1 = db.select(models.Employee).order_by(models.Employee.fname)
    users = db.session.execute(qs1).scalars()
   
    if id == 0:
        id = len(list(users))
        
    elif id == len(list(users))+1:
        id = 1
    
    query_for_leaves = db.select(func.count(models.Employee.id)).join(models.Leave, models.Employee.id == models.Leave.employee_id).filter(models.Employee.id == id)
    leave = db.session.execute(query_for_leaves).scalar()
    
    
    qs2 = db.select(models.Employee).where(models.Employee.id ==id) 
    user = db.session.execute(qs2).scalar()
    return flask.render_template("employee-details.html",user=user,users=users,leave=leave)

@app.route("/leave/<int:id>",methods = ["GET","POST"])
def add_leave(id):
    if flask.request.method == "GET":
        qs2 = db.select(models.Employee).where(models.Employee.id ==id) 
        user = db.session.execute(qs2).scalar()
    
        return flask.render_template("leave-form.html",id=id,user=user)
    
    if flask.request.method == "POST":  
        date=flask.request.form.get("date")
        reason=flask.request.form.get("reason")
        s =models.Leave(employee_id = id,date = date,reason = reason)
        db.session.add(s)
        db.session.commit()
        flask.flash('Leave added successfully!')
        return flask.redirect(flask.url_for('employee_details',id=id))
    

@app.route("/search", methods=["GET", "POST"])
def search_employee():
    if flask.request.method == "POST":
        employee_id = flask.request.form.get("employee_id")

        if employee_id:
            
            qs = db.select(models.Employee).where(models.Employee.id == employee_id)
            check_user = db.session.execute(qs).scalar()

            if check_user:
                return flask.redirect(flask.url_for("employee_details", id=check_user.id))
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