#===========================

from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from MySQLdb import IntegrityError

app = Flask(__name__)
app.secret_key = 'shida_mooc_key_group16'

# ==========================================
# MySQL Configuration
# ==========================================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'F096@ggame'
app.config['MYSQL_DB'] = 'shida_mooc'

mysql = MySQL(app)

# ==========================================
# Routes: Main Pages
# ==========================================

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/general')
def general_logout():
    return render_template('general.html')

@app.route('/general_register')
def general_register():
    return render_template('general_regis.html')

# ==========================================
# Routes: Authentication
# ==========================================

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    user_type = request.form.get('user_type', 'EXTERNAL')

    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO Users (name, email, password, role_type) VALUES (%s, %s, %s, %s)",
                    (name, email, password, user_type))
        mysql.connection.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for('login_general_process'))
    except IntegrityError:
        return "<script>alert('This Email is already registered.'); window.history.back();</script>"
    finally:
        cur.close()

@app.route('/general_login', methods=['GET', 'POST'])
def login_general_process():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT id, name, role_type FROM Users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close()
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_type'] = user['role_type']
            return redirect(url_for('dashboard'))
            
        return "<script>alert('Login Failed. Invalid credentials.'); window.history.back();</script>"
    
    return render_template('general_login.html')

@app.route('/login_ntnu', methods=['GET', 'POST'])
def login_ntnu():
    if request.method == 'POST':
        student_id = request.form['student_id']
        password = request.form['password']
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("""
            SELECT u.id, u.name, u.role_type FROM Users u
            JOIN Student_Details s ON u.id = s.user_id
            WHERE s.student_id=%s AND u.password=%s
        """, (student_id, password))
        user = cur.fetchone()
        cur.close()
        
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_type'] = 'STUDENT'
            return redirect(url_for('dashboard'))
            
        return "<script>alert('Login Failed. Invalid Student ID or Password.'); window.history.back();</script>"
    
    return render_template('ntnu_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ==========================================
# Routes: Core Features
# ==========================================

# ==================== 1. DASHBOARD PAGE ====================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html')

# ==================== 2. COURSE CATALOG PAGE ====================
# ==================== 2. COURSE CATALOG PAGE ====================
@app.route('/courses')
def courses():
    if 'user_id' not in session:
        return redirect(url_for('login_general_process'))
        
    user_id = session['user_id']
    user_type = session.get('user_type')
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # 1. ่join
    cur.execute("""
        SELECT c.id, c.title, c.price, i.name AS teachers 
        FROM Courses c 
        JOIN Instructors i ON c.instructor_id = i.id
    """)
    all_courses = cur.fetchall()

    cur.execute("SELECT course_id FROM Owned_Courses WHERE user_id = %s", (user_id,))
    owned_records = cur.fetchall()
    owned_ids = [row['course_id'] for row in owned_records]
    
    cur.close()

    return render_template('course.html', courses=all_courses, user_type=user_type, owned_ids=owned_ids)
# ==================== 3. OWNED COURSE PAGE ====================
@app.route('/owned_courses')
def owned_courses():
    if 'user_id' not in session:
        return redirect(url_for('login_general_process'))
        
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cur.execute("""
        SELECT c.id, c.title 
        FROM Owned_Courses oc
        JOIN Courses c ON oc.course_id = c.id
        WHERE oc.user_id = %s
    """, (session['user_id'],))
    
    user_owned = cur.fetchall()
    cur.close()

    return render_template('owned_course.html', owned_courses=user_owned)

@app.route('/enroll/<int:course_id>')
def enroll(course_id):
    user_id = session.get('user_id')
    if not user_id: 
        return redirect(url_for('login_general_process'))
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Updated query to only fetch 'price'
    cur.execute("SELECT price FROM Courses WHERE id=%s", (course_id,))
    c = cur.fetchone()
    
    # If the user is a student, the price is 0. Otherwise, use the DB price.
    final_price = 0 if session.get('user_type') == 'STUDENT' else c['price']
    
    try:
        cur.execute("INSERT INTO Orders (user_id, total_amount, status) VALUES (%s, %s, 'PAID')", (user_id, final_price))
        order_id = cur.lastrowid
        
        cur.execute("INSERT INTO Order_Items (order_id, course_id, price_at_purchase) VALUES (%s, %s, %s)", (order_id, course_id, final_price))
        cur.execute("INSERT INTO Owned_Courses (user_id, course_id) VALUES (%s, %s)", (user_id, course_id))
        
        mysql.connection.commit()
    except IntegrityError:
        mysql.connection.rollback()
    finally:
        cur.close()
        
    return redirect(url_for('courses'))

# ==================== STUDY ROOM ====================
@app.route('/study/<int:course_id>')
def study_room(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login_general_process'))
        
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cur.execute("""
        SELECT c.title 
        FROM Owned_Courses oc
        JOIN Courses c ON oc.course_id = c.id
        WHERE oc.user_id = %s AND oc.course_id = %s
    """, (session['user_id'], course_id))
    
    course = cur.fetchone()
    
    if not course:
        cur.close()
        return "<script>alert('You do not own this course!'); window.location.href='/owned_courses';</script>"
        
    cur.execute("""
        SELECT m.id as module_id, m.title as module_title, mat.content_url
        FROM Modules m
        LEFT JOIN Materials mat ON m.id = mat.module_id
        WHERE m.course_id = %s
        ORDER BY m.sort_order ASC
    """, (course_id,))
    
    modules = cur.fetchall()
    cur.close()
    
    return render_template('study_room.html', course_title=course['title'], modules=modules)

# ==================== CHART (CART) & CHECKOUT ====================

@app.route('/add_to_cart/<int:course_id>')
def add_to_cart(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login_general_process'))
    
    if 'cart' not in session:
        session['cart'] = []
        
    if course_id not in session['cart']:
        session['cart'].append(course_id)
        session.modified = True 
        
    # ตรงนี้เปลี่ยนให้กลับไปหน้า courses แทนที่จะไป dashboard
    return redirect(url_for('courses'))

@app.route('/chart')
def chart():
    if 'user_id' not in session:
        return redirect(url_for('login_general_process'))
        
    cart_ids = session.get('cart', [])
    
    if not cart_ids:
        return render_template('chart.html', cart_items=[])

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    format_strings = ','.join(['%s'] * len(cart_ids))
    
    # Updated query to only fetch 'price'
    query = f"SELECT id, title, price FROM Courses WHERE id IN ({format_strings})"
    cur.execute(query, tuple(cart_ids))
    cart_items = cur.fetchall()
    cur.close()

    return render_template('chart.html', cart_items=cart_items)


@app.route('/remove_from_cart/<int:course_id>')
def remove_from_cart(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login_general_process'))
    
    # check if 'cart' exists in session and if the course_id is in the cart before trying to remove it
    if 'cart' in session and course_id in session['cart']:
        session['cart'].remove(course_id)
        session.modified = True # แจ้ง Flask ว่ามีการเปลี่ยนแปลงข้อมูลใน Session
        
    # after removing the item, redirect back to the chart page to see the updated cart
    return redirect(url_for('chart'))




@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('home'))
        
    user_id = session['user_id']
    selected_courses = request.form.getlist('selected_courses')
    
    if not selected_courses:
        return redirect(url_for('chart')) 
        
    cur = mysql.connection.cursor()
    
    for course_id in selected_courses:
        try:
            cur.execute("INSERT INTO Owned_Courses(user_id, course_id) VALUES(%s, %s)", (user_id, course_id))
        except IntegrityError:
            pass 
            
        if int(course_id) in session.get('cart', []):
            session['cart'].remove(int(course_id))
            session.modified = True
            
    mysql.connection.commit()
    cur.close()
    
    # จ่ายเงินเสร็จ กลับไปที่หน้าวิชาของฉัน (owned_courses) ดีกว่าครับ จะได้เรียนได้เลย
    return "<script>alert('Payment Successful!'); window.location.href='/owned_courses';</script>"

if __name__ == '__main__':
    app.run(debug=True)