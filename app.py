from flask import Flask, jsonify, request, render_template
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# MySQL Database Configuration
db = mysql.connector.connect(
    host="localhost",
    user="harukidhruv",  # Change to your MySQL username
    password="My$QLr00t#2024",  # Change to your MySQL password
    database="PENmanagement"  # Your database name
)

# Home Page Route
@app.route("/")
def home():
    return render_template("index.html")


# Admin Panel Route
@app.route("/admin")
def admin_panel():
    return render_template("admin.html")

# Add Student Route
@app.route("/students", methods=["POST"])
def add_student():
    try:
        data = request.json
        cursor = db.cursor()
        query = "INSERT INTO students (pen, student_name, dob, gender, address, phone) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (data['pen'], data['student_name'], data['dob'], data['gender'], data['address'], data['phone'])
        cursor.execute(query, values)
        db.commit()
        return jsonify({"message": "Student added successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Get Student Details Route
@app.route("/students/<pen>", methods=["GET"])
def get_student(pen):
    try:
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM students WHERE pen = %s"
        cursor.execute(query, (pen,))
        student = cursor.fetchone()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        return jsonify(student)
    except Exception as e:
        return jsonify({"error": str(e)})

# Enroll Student Route
@app.route("/enroll", methods=["POST"])
def enroll_student():
    try:
        data = request.json
        cursor = db.cursor()
        query = "INSERT INTO enrollments (pen, class_id, enrollment_date) VALUES (%s, %s, %s)"
        values = (data['pen'], data['class_id'], data['enrollment_date'])
        cursor.execute(query, values)
        db.commit()
        return jsonify({"message": "Student enrolled successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Record Student Performance Route
@app.route("/performance", methods=["POST"])
def record_performance():
    try:
        data = request.json
        cursor = db.cursor()
        query = "INSERT INTO performance (pen, class_id, grade, attendance) VALUES (%s, %s, %s, %s)"
        values = (data['pen'], data['class_id'], data['grade'], data['attendance'])
        cursor.execute(query, values)
        db.commit()
        return jsonify({"message": "Performance recorded successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)})

# Generate Attendance Report Route
@app.route("/report/<pen>")
def generate_report(pen):
    try:
        query = f"""
            SELECT s.student_name, c.class_name, p.grade, p.attendance
            FROM students s
            JOIN enrollments e ON s.pen = e.pen
            JOIN classes c ON e.class_id = c.class_id
            JOIN performance p ON s.pen = p.pen
            WHERE s.pen = '{pen}';
        """
        df = pd.read_sql(query, db)
        if df.empty:
            return jsonify({"error": "No data found for this student"}), 404

        # Create a graph for attendance
        plt.figure(figsize=(8, 5))
        plt.bar(df['class_name'], df['attendance'], color='blue')
        plt.title(f"Attendance Report for {pen}")
        plt.xlabel("Classes")
        plt.ylabel("Attendance (%)")
        graph_path = os.path.join("static", f"attendance_{pen}.png")
        plt.savefig(graph_path)
        plt.close()

        return jsonify({"message": "Report generated!", "path": f"/static/attendance_{pen}.png"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
