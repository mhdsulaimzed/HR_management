import flask
import models
from sqlalchemy import select
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
    qs = db.select(models.Employee)
    
    users = db.session.execute(qs).scalars()
    
    
    return flask.render_template("employee.html",users=users)
@app.route("/employee/<int:id>")
def employee_details(id):
    qs = db.select(models.Employee)
    users = db.session.execute(qs).scalars()
    if id == 0:
        id = len(list(users))
        
    elif id == len(list(users))+1:
        id = 1
    
    
    qs = db.select(models.Employee).where(models.Employee.id ==id) 
    user = db.session.execute(qs).scalar()
    return flask.render_template("employee-details.html",user = user)

@app.route("/leave/<int:id>",methods = ["GET","POST"])
def add_leave(id):
    if flask.request.method == "GET":
    
        return flask.render_template("leave-form.html",id=id)
    
    if flask.request.method == "POST":
        date=flask.request.form.get("date")
        reason=flask.request.form.get("reason")
        

        s =models.Leave(employee_id = id,date = date,reason = reason)

        db.session.add(s)
        db.session.commit()
        flask.flash('Leave added successfully!')
        return flask.redirect(flask.url_for('employees'))

    
    







if __name__ == "__main__":

    app.run()