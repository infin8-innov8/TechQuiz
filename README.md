# ⚡ TIC Matrix

<div align="center">

[![Live App](https://img.shields.io/badge/Live_App-PythonAnywhere-0052CC?style=for-the-badge&logo=python&logoColor=white)](https://pranavvasankar404.pythonanywhere.com/register/)

[![Official Site](https://img.shields.io/badge/Club-TIC_Matrix-FF5722?style=for-the-badge)](https://tic-official.netlify.app/)


**A high-concurrency, full-stack event application featuring real-time synchronization and microsecond-accurate data processing.**

[Live Demo](https://pranavvasankar404.pythonanywhere.com/register/) | [Club Website](https://tic-official.netlify.app/)

</div>

## 📖 Overview

TechQuiz is a robust, full-stack web application designed for The Innovators and Creativa Matrix Club to host competitive quiz events. Engineered with a focus on seamless data flow, the platform integrates a live leaderboard, a high-precision buzzer system, and a dynamic headless CMS via Google Sheets. It demonstrates advanced capabilities in backend routing, real-time state synchronization, and database management, ensuring a highly responsive and fair competitive environment.

## ✨ Features

- ⏱️ **Microsecond-Accuracy Buzzer**: Captures and timestamps user inputs with extreme precision to resolve simultaneous requests fairly.
- 📊 **Live Leaderboard**: Real-time scoring engine that instantly processes incoming data and updates rankings for all active participants.
- 🔄 **Dynamic Data Pipeline**: Integrates the Google Sheets API to fetch questions automatically, allowing non-technical coordinators to update content on the fly.
- 🔒 **Secure Authentication**: Streamlined user registration, session management, and state tracking.
- 🚀 **End-to-End Deployment**: Fully deployed and routed on PythonAnywhere for immediate access.

## 🖥️ Screenshots

## 🛠️ Tech Stack

**Backend & Data Source:**

![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)

![Google Cloud](https://img.shields.io/badge/Google_Sheets_API-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)

**Frontend:**

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)

![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

## 🚀 Quick Start

### Prerequisites
- Python 3.x
- A Google Cloud Service Account JSON file (for Sheets API access)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/infin8-innov8/TechQuiz
    cd TechQuiz/TechQuiz
    ```

2.  **Set up the virtual environment**
    ```bash
    python3 -m venv .venv # ON windows use: python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables**
    Create a `.env` file in :
    ```env
    SECRET_KEY= your_secret_key
    DEBUG = Flase or True
    EMAIL_HOST_USER= your_email
    EMAIL_HOST_PASSWORD= your_email_app_passowrd                                     
    ```

5.  **Run migrations and start the server**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

## 📁 Project Structure

```text
TechQuiz
    ├── api
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── google_auth_setup.py
    ├── instructor
    │   ├── admin.py
    │   ├── apps.py
    │   ├── forms.py
    │   ├── __init__.py
    │   ├── models.py
    │   ├── templates
    │   │   └── instructor
    │   │       └── dashboard.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── keys.json #keys given by Google Cloud Console to connct to the Google Sheets
    ├── manage.py
    ├── registration_n_login
    │   ├── admin.py
    │   ├── apps.py
    │   ├── forms.py
    │   ├── models.py
    │   ├── static
    │   │   └── registration_n_login
    │   │       └── images
    │   │           └── tic_logo.png
    │   ├── templates
    │   │   └── registration_n_login
    │   │       ├── eliminated.html
    │   │       ├── leaderboard.html
    │   │       ├── login.html
    │   │       ├── register.html
    │   │       ├── round_3.html
    │   │       ├── success.html
    │   │       ├── verify_otp.html
    │   │       └── waiting_room.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── requirements.txt
    ├── round_1
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── __pycache__
    │   ├── templates
    │   │   └── round_1
    │   │       └── round_1.html
    │   ├── tests.py
    │   ├── urls.py
    │   ├── utils.py
    │   └── views.py
    ├── round_2
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── templates
    │   │   └── round_2
    │   │       └── round_2.html
    │   ├── tests.py
    │   ├── urls.py
    │   ├── utils.py
    │   └── views.py
    ├── service_account.json # a file given by Google Cloud Cosole to authenticate the host user.
    └── TechQuiz
        ├── asgi.py
        ├── settings.py
        ├── urls.py
        └── wsgi.py
