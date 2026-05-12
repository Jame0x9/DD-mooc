from flask import Flask, render_template, request, redirect, session, url_for
from MySQLdb import IntegrityError
from flask_mysqldb import MySQL

app = Flask(__name__)

# ตั้งค่าการเชื่อมต่อ (Config)
app.secret_key = 'shida_mooc_key_group16'
app.config['MYSQL_HOST'] = 'localhost'    
app.config['MYSQL_USER'] = 'root'         
app.config['MYSQL_PASSWORD'] = 'F096@ggame'         
app.config['MYSQL_DB'] = 'shida_mooc'     

mysql = MySQL(app)

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# ==================== GENERAL USER ====================
@app.route('/general')
def general_page():
    return render_template('general.html')

@app.route('/general_register')
def general_register():
    return render_template('general_regis.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role_type = request.form['user_type'] #  'EXTERNAL'

    cur = mysql.connection.cursor()
    try:
        # อิงตาม Schema: ตาราง Users ใช้ role_type
        cur.execute("INSERT INTO Users(name, email, password, role_type) VALUES(%s, %s, %s, %s)",
                    (name, email, password, role_type))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login_general_process')) # go to login page after successful registration
        
    except IntegrityError as e:
        cur.close()
        if e.args[0] == 1062: # Duplicate entry
            return "<script>alert('Email has been used'); window.location.href='/general_register';</script>"
        return "An error occurred"

@app.route('/general_login', methods=['GET', 'POST'])
def login_general_process():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        # ตรวจสอบจาก Users และ role_type = 'EXTERNAL'
        cur.execute("SELECT id, name, role_type FROM Users WHERE email=%s AND password=%s AND role_type='EXTERNAL'", (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_type'] = user[2]
            return redirect(url_for('courses')) # สำเร็จไปหน้า Courses
        
        return "<script>alert('Login Failed: Invalid Email or Password'); window.location.href='/general_login';</script>"
    
    return render_template('general_login.html')

# ==================== NTNU STUDENT ====================
@app.route('/login_ntnu', methods=['GET', 'POST'])
def login_ntnu():
    if request.method == 'POST':
        student_id = request.form['student_id']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        # Logic: เด็ก NTNU ต้องหา student_id จากตาราง Student_Details และเช็ครหัสผ่านจากตาราง Users
        cur.execute("""
            SELECT u.id, u.name, u.role_type 
            FROM Users u
            JOIN Student_Details s ON u.id = s.user_id
            WHERE s.student_id=%s AND u.password=%s
        """, (student_id, password))
        
        user = cur.fetchone()
        cur.close()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_type'] = user[2] # จะเป็น 'STUDENT'
            return redirect(url_for('courses'))
        
        return "<script>alert('Login Failed: Wrong Student ID or Password'); window.location.href='/login_ntnu';</script>"
    
    return render_template('ntnu_login.html')

# ==================== COURSES & ENROLLMENT ====================
@app.route('/courses')
def courses():
    if 'user_id' not in session:
        return redirect(url_for('home')) # ถ้ายังไม่ล็อกอินให้กลับไปหน้าแรก

    user_type = session.get('user_type')
    
    cur = mysql.connection.cursor()
    # ดึงข้อมูลที่จำเป็นมาแสดงให้ตรงลำดับ index (id=0, title=1, discount_price=2)
    cur.execute("SELECT id, title, discount_price FROM Courses")
    all_courses = cur.fetchall()
    cur.close()

    return render_template('course.html', courses=all_courses, user_type=user_type)

@app.route('/enroll/<int:course_id>')
def enroll(course_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    try:
        # Schema ของคุณใช้ตาราง Owned_Courses ไม่ใช่ Enrollments
        cur.execute("INSERT INTO Owned_Courses(user_id, course_id) VALUES(%s, %s)", (user_id, course_id))
        mysql.connection.commit()
    except IntegrityError:
        pass # ถ้าผู้ใช้ซื้อแล้ว (ซ้ำ) ให้ข้ามไป
    
    cur.close()
    return redirect('/courses')

# ==================== REVIEWS ====================
# หมายเหตุ: ใน Schema เดิมไม่มีตาราง Reviews แต่ผมคงโค้ดไว้ให้ 
# อย่าลืมสร้างตาราง Reviews ใน MySQL Workbench ด้วยนะครับ
@app.route('/reviews')
def reviews():
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * FROM Reviews")
        reviews = cur.fetchall()
    except:
        reviews = [] # ป้องกัน error หากยังไม่ได้สร้างตาราง
    return render_template('reviews.html', reviews=reviews)

@app.route('/add_review', methods=['POST'])
def add_review():
    if 'user_id' not in session:
        return redirect(url_for('home'))
        
    user_id = session['user_id']
    course_id = request.form['course_id']
    rating = request.form['rating']
    comment = request.form['comment']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Reviews(user_id, course_id, rating, comment) VALUES(%s, %s, %s, %s)",
                (user_id, course_id, rating, comment))
    mysql.connection.commit()
    return redirect('/reviews')

if __name__ == '__main__':
    app.run(debug=True)