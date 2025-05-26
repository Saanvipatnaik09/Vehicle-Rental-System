# 🚗 Vehicle Rental Management System

A web-based Car Rental Management System built with **Streamlit** and **MySQL**, designed to manage car rentals, returns, customer information, and admin operations through an intuitive UI.

---

## 📦 Features

- 🔍 View all cars and filter available ones
- 🧾 Rent a car with rental dates, customer details, and driver option
- 🧾 Generate rental receipts
- 🔁 Return cars with optional damage/late fee inputs
- 📊 View rental history with statistics
- 🔐 Admin portal for:
  - Adding new cars
  - Updating car status (AVAILABLE, RENTED, MAINTENANCE)
  - Viewing and exporting rental records
  - Changing admin password

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: MySQL
- **Environment Config**: `.env` via `python-dotenv`
- **Data Handling**: Pandas

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/car-rental-streamlit.git
cd car-rental-streamlit
```

### 2. Create the `.env` File

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=car_rental
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run streamlitCar1.py
```

---

## 🧾 Requirements

These Python packages are required:

```txt
streamlit
mysql-connector-python
python-dotenv
pandas
```

To install:

```bash
pip install -r requirements.txt
```

---

## 🔑 Default Admin Access

- **Password**: `1289`
- Changeable in the Admin Portal

---

## 📄 License

This project is licensed under the MIT License.

