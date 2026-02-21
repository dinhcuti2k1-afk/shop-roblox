from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SECRET_KEY'] = 'secretkey'

db = SQLAlchemy(app)

# ======================
# MODELS
# ======================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100))
    class_name = db.Column(db.String(20))

# Tạo database (Flask 3 cách mới)
with app.app_context():
    db.create_all()

# ======================
# REGISTER (Parent only)
# ======================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        email = request.form['email']

        if not username.startswith("02"):
            return "Chỉ phụ huynh (mã 02...) mới được đăng ký"

        student = Student.query.filter_by(code=username).first()
        if not student:
            return "Mã học sinh không tồn tại"

        if User.query.filter_by(username=username).first():
            return "Tài khoản đã tồn tại"

        if password != confirm:
            return "Mật khẩu không khớp"

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role="parent",
            email=email
        )

        db.session.add(new_user)
        db.session.commit()

        session['user'] = username
        session['role'] = "parent"

        return redirect('/parent')

    return render_template('register.html')

# ======================
# LOGIN
# ======================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Admin mặc định
        if username == "001" and password == "001":
            session['user'] = "001"
            session['role'] = "admin"
            return redirect('/admin')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            session['role'] = user.role

            if user.role == "parent":
                return redirect('/parent')

        return "Sai thông tin đăng nhập"

    return render_template('login.html')

# ======================
# DASHBOARD
# ======================

@app.route('/admin')
def admin():
    if session.get('role') != "admin":
        return redirect('/login')
    return "Trang Admin"

@app.route('/parent')
def parent():
    if session.get('role') != "parent":
        return redirect('/login')
    return "Trang Phụ Huynh"

# ======================

if __name__ == '__main__':
    app.run(debug=True)v