# 🫁 Pneumonia Detection Web App

This is a deep learning–powered web application that detects **pneumonia from chest X-ray images** using a fine-tuned MobileNetV2 model. The app provides a user-friendly interface to upload X-rays, predict disease presence, view prediction history with charts, and export reports as PDF.

---

## 🚀 Features

- 🔐 **User Authentication** (login/signup with hashed passwords using bcrypt)
- 🧠 **AI-Based Prediction** using MobileNetV2 trained on pneumonia datasets
- 🖼 **Upload X-ray Images** and get predictions instantly
- 📊 **Prediction History** with confidence scores and chart visualization
- 📄 **PDF Export** of prediction reports
- 🧹 **Delete History** feature
- 🌙 **Dark Mode** toggle
- 📱 Responsive and clean UI

---

## 🛠 Technologies Used

- Python + Flask
- TensorFlow + Keras (MobileNetV2)
- OpenCV for image preprocessing
- SQLite for storing user data and predictions
- FPDF for PDF generation
- Chart.js for history visualization
- HTML/CSS (Poppins + Font Awesome)

## 🧪 How to Run Locally

> Make sure you have Python 3.8+ and `pip` installed.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/pneumonia-detection-app.git
cd pneumonia-detection-app
