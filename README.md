# TaLaan

## Project Overview
TaLaan is an artificial intelligence-powered web application that helps users create a budget-friendly grocery list based on family size, budget, ration period, and requested items. 
---

## Features

- Household demographic input
- AI-assisted grocery item alternative generation
- Automatic grocery list generation
- Receipt-style grocery summary
- Nearby grocery store locator using Google Maps

---

## Technologies Used

### Backend
- Python
- Flask

### Database
- MySQL

### APIs
- Google Gemini API
- Google Maps Places API

### Frontend
- HTML
- CSS
- JavaScript

### Development Tools
- Visual Studio Code
- MySQL Workbench
- Git
- GitHub

---

## ⚙️ Installation & Setup

Follow these steps to run the application locally on your machine.

### 1. Clone the Repository
Open your terminal and clone this project:
```bash
git clone [https://github.com/H3llo-o/talaan-CommuniCart-PasaBuy.git](https://github.com/H3llo-o/talaan-CommuniCart-PasaBuy.git)
cd talaan-CommuniCart-PasaBuy
```

### 2. Configure Environment Variables
Create a file named .env in the root directory. Copy the structure below and fill in the values:
GEMINI_API_KEY='AQ.Ab8RN6I8ZL8_SEZaSUN-8JRGnEzbKdVNgAFl_f1sjggn1EYM8w'
MAPS_API_KEY='AIzaSyBRI4Mwuojqms-qI1fdOQa9-f57ltLpBNM'

MYSQL_HOST='mysql-3e7455b8-talaan.j.aivencloud.com'
MYSQL_PORT='14221'
MYSQL_USER='avnadmin'
MYSQL_PASSWORD='AVNS_axsG4OXYIRfh2C-Bvd2'
MYSQL_DB='pasabuy_db'

### 3. Setup Virtual Environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Start the Application
```bash
python app.py
```
### 6. Link
Copy the link and add /auth

--- 

## Project Structure
│
├── database/
│   ├── sample_products.csv
│   ├── schema.sql
│   ├── seed.sql
│   └── seed_db.py
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│
├── .gitignore
├── app.py
├── crud.py
├── requirements.txt
└── README.md

---

## Contributors
1. Leonard F. Futol
2. Joshua A. Renovales
3. Patrick DC. Quitoriano

## License

This project was developed for SparkFest 2026.
