# ⚡ TIC Matrix

<div align="center">

[![Live App](https://img.shields.io/badge/Live_App-PythonAnywhere-0052CC?style=for-the-badge&logo=python&logoColor=white)](https://pranavvasankar404.pythonanywhere.com/register/)

[![Official Site](https://img.shields.io/badge/Club-TIC_Matrix-FF5722?style=for-the-badge)](https://tic-official.netlify.app/)

[![GitHub stars](https://img.shields.io/github/stars/PranavVasankar/tic-matrix?style=for-the-badge)](https://github.com/PranavVasankar/tic-matrix/stargazers)

[![GitHub issues](https://img.shields.io/github/issues/PranavVasankar/tic-matrix?style=for-the-badge)](https://github.com/PranavVasankar/tic-matrix/issues)

[![GitHub license](https://img.shields.io/github/license/PranavVasankar/tic-matrix?style=for-the-badge)](LICENSE)

**A high-concurrency, full-stack event application featuring real-time synchronization and microsecond-accurate data processing.**

[Live Demo](https://pranavvasankar404.pythonanywhere.com/register/) | [Club Website](https://tic-official.netlify.app/)

</div>

## 📖 Overview

TIC Matrix is a robust, full-stack web application designed for The Innovators and Creativa Matrix Club to host competitive quiz events. Engineered with a focus on seamless data flow, the platform integrates a live leaderboard, a high-precision buzzer system, and a dynamic headless CMS via Google Sheets. It demonstrates advanced capabilities in backend routing, real-time state synchronization, and database management, ensuring a highly responsive and fair competitive environment.

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
    git clone [https://github.com/PranavVasankar/tic-matrix.git](https://github.com/PranavVasankar/tic-matrix.git)
    cd tic-matrix
    ```

2.  **Set up the virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables**
    Create a `.env` file in the root directory:
    ```env
    SECRET_KEY=your_secret_key
    GOOGLE_SHEETS_CREDENTIALS=path/to/your/credentials.json
    ```

5.  **Run migrations and start the server**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

## 📁 Project Structure

```text
tic-matrix/
├── .gitignore
├── requirements.txt       # Python dependencies
├── manage.py              # Django execution script
├── core/                  # Main project settings and routing
│   ├── settings.py
│   └── urls.py
└── quiz_app/              # Core application logic
    ├── models.py          # Database models for users/scores
    ├── views.py           # Buzzer logic and Google Sheets data fetching
    ├── templates/         # HTML structure for the UI
    └── static/            # CSS stylesheets and JavaScript files
