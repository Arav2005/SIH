from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("farm.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS risk_assessments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        farmer_name TEXT,
                        farm_type TEXT,
                        location TEXT,
                        num_animals INTEGER,
                        score INTEGER,
                        risk_level TEXT,
                        recommendations TEXT
                    )''')
    conn.commit()
    conn.close()

init_db()

# ---------- Homepage ----------
@app.route("/")
def home():
    return render_template("home.html")

# ---------- Risk Assessment Form ----------
@app.route("/RiskAssessmentModule", methods=["GET", "POST"])
def RiskAssessmentModule():
    if request.method == "POST":
        farmer_name = request.form.get("farmer_name")
        farm_type = request.form.get("farm_type")
        location = request.form.get("location")
        num_animals = int(request.form.get("num_animals"))

        # Checklist responses (yes = 1, no = 0)
        q1 = int(request.form.get("q1", 0))
        q2 = int(request.form.get("q2", 0))
        q3 = int(request.form.get("q3", 0))
        q4 = int(request.form.get("q4", 0))
        q5 = int(request.form.get("q5", 0))

        score = q1 + q2 + q3 + q4 + q5

        # Determine risk level
        if score <= 2:
            risk_level = "High Risk ❌"
            recommendations = "⚠️ Improve housing, sanitation, and vaccination protocols immediately."
        elif score <= 4:
            risk_level = "Medium Risk ⚠️"
            recommendations = "✔️ Improve biosecurity by controlling farm access and hygiene."
        else:
            risk_level = "Low Risk ✅"
            recommendations = "👌 Keep up the good biosecurity practices."

        # Save to database
        conn = sqlite3.connect("farm.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO risk_assessments (farmer_name, farm_type, location, num_animals, score, risk_level, recommendations) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (farmer_name, farm_type, location, num_animals, score, risk_level, recommendations))
        conn.commit()
        conn.close()

        return render_template("result.html",
                               farmer_name=farmer_name,
                               farm_type=farm_type,
                               score=score,
                               risk_level=risk_level,
                               recommendations=recommendations)

    return render_template("risk_form.html")

# ---------- Dashboard ----------
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("farm.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM risk_assessments")
    data = cursor.fetchall()
    conn.close()
    return render_template("dashboard.html", records=data)

if __name__ == "__main__":
    app.run(debug=True)
