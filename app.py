from flask import Flask, render_template, request, redirect, url_for, session, send_file, g
from werkzeug.utils import secure_filename
import sqlite3, os, io
from datetime import datetime
from fpdf import FPDF
from predict import predict_image
import bcrypt

# Flask setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure value
DATABASE = 'pneumonia.db'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------------- DB Setup ----------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ---------------------- Routes ----------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and not session.get('logged_in'):
        username = request.form.get('username')
        password = request.form.get('password')

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('index.html', login_error="Invalid credentials")

    elif request.method == 'POST' and session.get('logged_in'):
        file = request.files['image']
        if file.filename == '':
            return render_template('index.html', image_error="Please upload an image")

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        prediction, confidence = predict_image(filepath)

        db = get_db()
        db.execute("INSERT INTO predictions (username, timestamp, prediction, confidence) VALUES (?, ?, ?, ?)",
                   (session['username'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), prediction, float(confidence)))
        db.commit()

        return render_template('index.html',
                               prediction=prediction,
                               confidence=f"{confidence:.2f}",
                               image='/' + filepath)

    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')

        if not new_username or not new_password:
            return render_template('index.html', signup_mode=True, signup_error="Both fields are required")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (new_username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template('index.html', signup_mode=True, signup_error="Username already exists")

        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, hashed_pw.decode()))
        db.commit()

        session['logged_in'] = True
        session['username'] = new_username
        return redirect(url_for('index'))

    return render_template('index.html', signup_mode=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/export_pdf', methods=['POST'])
def export_pdf():
    if not session.get('logged_in'):
        return redirect(url_for('index'))

    prediction = request.form.get('prediction')
    confidence = request.form.get('confidence')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Pneumonia Detection Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Username: {session['username']}", ln=True)
    pdf.cell(200, 10, txt=f"Prediction: {prediction}", ln=True)
    pdf.cell(200, 10, txt=f"Confidence: {confidence}%", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    pdf_output = io.BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)

    return send_file(
        pdf_output,
        as_attachment=True,
        download_name="pneumonia_report.pdf",
        mimetype="application/pdf"
    )

@app.route('/history')
def history():
    if not session.get('logged_in'):
        return redirect(url_for('index'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT timestamp, prediction, confidence FROM predictions WHERE username = ?", (session['username'],))
    rows = cursor.fetchall()

    records = [{
        "timestamp": row["timestamp"],
        "prediction": row["prediction"],
        "confidence": round(float(row["confidence"]), 2)
    } for row in rows]

    return render_template('history.html', records=records)

@app.route('/delete_history', methods=['POST'])
def delete_history():
    if not session.get('logged_in'):
        return redirect(url_for('index'))

    db = get_db()
    db.execute("DELETE FROM predictions WHERE username = ?", (session['username'],))
    db.commit()
    return redirect(url_for('history'))

# ---------------------- Run ----------------------
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
