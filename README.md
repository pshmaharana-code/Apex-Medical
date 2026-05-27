# ApexMedical - Modern Hospital Management System

[![Vue.js](https://img.shields.io/badge/Vue.js-3.X-4FC08D?style=flat&logo=vuedotjs)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=flat&logo=flask)](https://flask.palletsprojects.com/)
[![Redis](https://img.shields.io/badge/Redis-Task%20Queue-DC382D?style=flat&logo=redis)](https://redis.io/)

ApexMedical is a high-performance, full-stack Hospital Management System designed to redefine the digital healthcare experience. It bridges the gap between top-tier medical specialists and patients through a secure, seamless portal. 

The application features a custom, cinematic **Glassmorphism** and **Skeuomorphic** UI design, utilizing an "Apex Teal" (#0f766e) color palette to deliver a premium, modern aesthetic without sacrificing accessibility or speed.

## 🚀 Key Features

* **Secure Authentication:** Role-based access control (RBAC) for Patients, Doctors, and Administrators using JWT.
* **Cinematic UI/UX:** A bespoke frontend featuring frosted glass elements, abstract cinematic backgrounds, and smooth GSAP animations.
* **Appointment Management:** Real-time scheduling, booking, and portal access for patients.
* **Asynchronous Processing:** Integrated Celery and Redis task queues for handling heavy background operations.
* **Decoupled Architecture:** A clean separation of concerns with a Vue 3 (Vite) Single Page Application talking to a lightweight Flask REST API.

## 💻 Tech Stack

**Frontend:**
* Vue 3 (Composition API)
* Vite (Build Tool)
* Vue Router (Navigation)
* Pinia (State Management)
* GSAP (Animations)
* Custom CSS (Glassmorphism & CSS Masking)

**Backend:**
* Python 3 & Flask (REST API)
* SQLite / PostgreSQL (Database)
* Celery (Background Tasks)
* Redis (Message Broker)

## 🛠️ Local Development Setup

Follow these instructions to get a copy of the project up and running on your local machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/pshmaharana-code/Apex-Medical.git](https://github.com/pshmaharana-code/Apex-Medical.git)
cd Apex-Medical

2. Frontend Setup (Vue.js)
Open a terminal in the root directory and install the Node dependencies:

Bash
npm install

Start the Vite development server:
Bash
npm run dev

3. Backend Setup (Flask & Celery)
Open a separate terminal in the root directory. Create and activate a Python virtual environment:
Bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

Install the Python requirements:
Bash
pip install -r requirements.txt

Start the Flask development server:
Bash
python app.py

(Note: To test background tasks locally, ensure you have a Redis server running and start your Celery worker using celery -A celery_worker.celery worker --loglevel=info)

👨‍💻 Author
Piyush Maharana

GitHub: @pshmaharana-code

Designed and built to showcase modern web architecture and premium UI design patterns.