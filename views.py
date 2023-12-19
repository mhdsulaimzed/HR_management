import flask
import models
from sqlalchemy import select, join, func
from flask_cors import CORS


app = flask.Flask("hrsw")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///hrsw"
app.secret_key = "abc"
CORS(app)

db = models.SQLAlchemy(model_class=models.Base)
db.init_app(app)


@app.route("/employees", methods=["GET","POST"])
def employees():
    if flask.request.method =="GET":
        qs = db.select(models.Employee).order_by(models.Employee.fname)
        users_fet = db.session.execute(qs).scalars()
        user_list = [{"id":user.id,"fname":user.fname,"lname":user.lname,"title":user.title.title,"email":user.email,"phone":user.phone}for user in users_fet]
        return flask.jsonify(users=user_list)
    
    
    if flask.request.method =="POST":
        try:
            print("email")
            
            data = flask.request.get_json()
            if not all(key in data for key in ["fname", "lname", "title_id", "email", "phone"]):
                return flask.jsonify({"message":"Missing required fields"})
            print(type(data))
            fname =data['fname']
            lname = data['lname']
            title = data['title_id']
            email = data['email']
            phone = data['phone']

            print(email)
           
            qs = models.Employee(fname=fname,lname=lname,title_id=title,email=email,phone=phone)
            db.session.add(qs)
            db.session.commit()
            return flask.jsonify({"message":"Employee Successfully added"})
        except Exception  as e:
            print(e)
            return flask.jsonify({"message":"Couldnt add Employee"},)
        


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
    query_for_leaves = (
        db.select(func.count(models.Employee.id))
        .join(models.Leave, models.Employee.id == models.Leave.employee_id)
        .filter(models.Employee.id == id)
    )
    leave = db.session.execute(query_for_leaves).scalar()
    qs2 = db.select(models.Employee).where(models.Employee.id == id)
    user = db.session.execute(qs2).scalar()
    data = {"leave_taken": leave, "max_leaves": user.title.max_leaves}
    return data


@app.route("/leave/<int:id>", methods=["POST"])
def add_leave(id):
    if flask.request.method == "POST":
        leaves = get_leave_data(id)
        
        if leaves["leave_taken"] < leaves["max_leaves"]:
            try:
                data = flask.request.get_json()
                date = data.get('date')
                reason = data.get('reason')
            except Exception as e:
                return flask.jsonify({"message": "Invalid JSON format"}), 400

            if date and reason:
                leave_entry = models.Leave(employee_id=id, date=date, reason=reason)
                
                try:
                    db.session.add(leave_entry)
                    db.session.commit()
                    return flask.jsonify({"message": "Leave added successfully"})
                except Exception as e:
                    db.session.rollback()
                    return flask.jsonify({"message":"Failed to add leave."}), 
            else:
                return flask.jsonify({"message": "Invalid 'date' or 'reason' in the request"})
        else:
            return flask.jsonify({"message": "Maximum leave limit attained"}), 400
    
    




    
