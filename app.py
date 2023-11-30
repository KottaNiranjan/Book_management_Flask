from flask import Flask,redirect,render_template,request,jsonify,url_for,session,make_response
from flask_jwt_extended import JWTManager, jwt_required, create_access_token,decode_token
from pymongo import MongoClient,errors
import json
import jwt
from jwt import DecodeError
from functools import wraps
from login import user_db
from datetime import timedelta,datetime

app=Flask(__name__)
app.secret_key="Niranjan8822"
app.config['JWT_SECRET_KEY'] = 'Niranjan8822'  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt1 = JWTManager(app)
client=MongoClient("localhost",27017)
Assignment_3=client.Assignment_3 
books=Assignment_3.books
books.create_index("id", unique=True)


def validate_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            t=request.args.get("token")
            token=session.get("jwt_token",None)
            decoded_token = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        
            if t==token:
                print("Token is Valid")
                return f(*args,**kwargs)
            else:
                return jsonify("Token is invalid")
        except:
            return jsonify({"error":"Token is not fetched"})
    return wrapper


def validate_token1(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            t=request.headers.get("auth")
            print(t)
            token=session.get("jwt_token")
            print(token)
            decoded_token = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            if t==token:
                print("Token is Valid")
                return f(*args,**kwargs)
            else:
                return jsonify({"error":"Token is invalid"})
        except DecodeError as e:
            print("error")
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            print("error")
            return jsonify({"error":e})
    return wrapper

def generate_token(username):
    access_token = create_access_token(identity=username)
    return access_token

@app.route("/access_token")
def access_token():
    if 'jwt_token' in session:
        return jsonify(session["jwt_token"])
    return jsonify({"error":"Token is not fetched"})

def generate_id():
    try:
        max_numeric_id = books.find_one(sort=[('id', -1)])
        numeric_id = int(max_numeric_id['id']) + 1 if max_numeric_id else 1
    except:
        return 1


from flask import request, jsonify

@app.route("/your_route", methods=["POST"])
def your_route():
    try:
        # Retrieve the Authorization header
        authorization_header = request.headers.get("Authorization")

        # Check if the header is present and starts with "Bearer "
        if authorization_header and authorization_header.startswith("Bearer "):
            # Extract the token
            bearer_token = authorization_header.split(" ")[1]

            # Now you can use the bearer_token as needed
            # ...

            return jsonify({"message": bearer_token})
        else:
            return jsonify({"error": "Bearer token missing or invalid"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

  
@app.route("/")
def main():
    if "username" in session:
        return redirect(url_for("home"))
    return redirect("login")

@app.route("/home")
@validate_token
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    else:
        user=session["username"]
        response = make_response(render_template('home.html',user=user))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return render_template("home.html",user=user)
        
@app.route("/login")
def login():
    if 'login_error'  in session:
        error=session.pop("login_error")
        return render_template("login.html",error=error)
    if 'username' in session:
        return redirect(url_for("home"))
    else:
        return render_template("login.html")

@app.route("/login_validator",methods=["POST"])
def login_validator():
    user=request.form["username"]
    password=request.form["password"]
    try:
        user_data=list(user_db.find({"username":user,"password":password},{"_id":0}))
        print(user_data)
        if len(user_data):
            payload = {
                    'exp': datetime.utcnow() + timedelta(days=1),
                    'iat': datetime.utcnow(),
                    'identity': user}
            token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
            
            session['jwt_token'] = token
            session['username'] = user
            return redirect(url_for("home",token=token))
        else:
            print("eErroko")
            session["login_error"] = "Invalid Username or Password"
            return redirect(url_for("login"))

    except TypeError as te:
        session["login_error"] = "Invalid Username or Password"
        return redirect(url_for("login"))

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
try:
    @app.route("/register_validator",methods=['POST'])
    def register_validator():
        r=request.form
        user={"username":r.get("username"),"password":r.get("password"),"email":r.get("email")}
        if r.get("password")!=r.get("repass"):
            session["reg_error"]="Password doesn't Match"
            return redirect(url_for("register"))
        try:
            user_db.insert_one(user)
            session['username']=r.get("username")
            return redirect(url_for("home"))
        except Exception as e:
            return render_template("register.html",error="Registration Unsuccessful!!")
except:
    def solve():
        return redirect(url_for("register"))

@app.route("/register")
def register():
    if 'reg_error' in session:  
        error=session["reg_error"]
        session.pop("reg_error")
        return render_template("register.html",error=error)
    if 'username' in session:
        return redirect(url_for("main"))
    else:
        return render_template("register.html")
    
    
@app.route("/logout")
def logout():
    session.pop('jwt_token', None)
    session.pop("username",None)
    response=make_response(url_for("home"))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return redirect(url_for("main"))

@app.route("/books",methods=['GET'])
def get_books():
    try:
        book= [book for book in books.find({},{"_id": 0})]
        return jsonify(book)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/get_books/<book_id>")

def get_book_id(book_id):
    try:
        book=list(books.find({"id":int(book_id)},{"_id": 0}))
        return jsonify(book)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app.route("/add_books",methods=['POST'])
@validate_token1
def add_books():
    try:
        r=request.get_json()
        book_id=r.get("id")
        book={'id':int(r.get('id')),'title':r.get('title'),'author':r.get('author'),'genre':r.get('genre'),'publication_year':r.get('publication_year')}
        flag=list(books.find({"id":int(book_id)},{"_id": 0}))
        if len(flag)==0:
            books.insert_one(book)
            return jsonify({"message": "Book added successfully"})
        else:
            return jsonify({"error": "Duplicate ID. Book not added."})
    except errors.DuplicateKeyError:
        return jsonify({"error": "Duplicate ID. Book not added."})
    except:
        return jsonify({"error": str(e)})

@app.route("/delete_book/<book_id>",methods=['DELETE'])
@validate_token1
def delete(book_id):
    try:
        updated_book=book=list(books.find({"id":int(book_id)},{"_id": 0}))
        if len(updated_book)==0:
            return jsonify({"error":"Book Id is not Found"})
        else:  
            books.delete_one({'id':int(book_id)})
            return jsonify({"msg":"Book is deleted successfully"})
        
    except :
        return jsonify({"error":"Book is not found"})

@app.route("/update_book/<book_id>",methods=["PUT"])
@validate_token1
def update(book_id):
    try:
        json_data=request.get_json()
        books.update_one({'id':int(book_id)},{'$set':json_data})
        updated_book=book=list(books.find({"id":int(book_id)},{"_id": 0}))
        if updated_book:
            return jsonify(updated_book)
        else:
            return {"error":"Book Id not Found"}
    except Exception as e:
        return jsonify({"error":str(e)}),400
    
    
    
if __name__=="__main__":
    app.run(debug=True)