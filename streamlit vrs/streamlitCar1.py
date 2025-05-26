import streamlit as st
import mysql.connector
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables for secure database connection
load_dotenv()

# Initialize database connection
def init_db():
    # Get database connection details from environment variables or use defaults
    db_host = os.getenv("DB_HOST", "localhost")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "Saanvi@2005")
    db_name = os.getenv("DB_NAME", "car_rental")
    
    # Connect to MySQL
    try:
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        
        # Create database if it doesn't exist
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        
        # Create tables if they don't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS cars (
            Car_no INT PRIMARY KEY, 
            Car_class VARCHAR(50), 
            Model_name VARCHAR(100), 
            Car_color VARCHAR(50), 
            Capacity INT, 
            Daily_Rent INT, 
            Car_Status VARCHAR(20) DEFAULT 'AVAILABLE', 
            Rent_ID INT DEFAULT NULL
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
            password VARCHAR(50)
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS rentings (
            Rent_ID INT AUTO_INCREMENT PRIMARY KEY,
            Cust_Name VARCHAR(100),
            Cust_Phone_no BIGINT,
            Car_no INT,
            Date_Rented DATE,
            Return_Date DATE,
            Driver VARCHAR(10),
            Total_Rent INT,
            FOREIGN KEY (Car_no) REFERENCES cars(Car_no)
        )''')
        
        # Insert default data if empty
        cursor.execute("SELECT COUNT(*) FROM admins")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO admins (password) VALUES ('1289')")
        
        cursor.execute("SELECT COUNT(*) FROM cars")
        if cursor.fetchone()[0] == 0:
            sample_cars = [
                (101, 'SUV', 'Toyota RAV4', 'Red', 5, 50, 'AVAILABLE', None),
                (102, 'SEDAN', 'Honda Civic', 'Blue', 4, 40, 'AVAILABLE', None),
                (103, 'SUV', 'Ford Explorer', 'Black', 7, 60, 'AVAILABLE', None),
                (104, 'SEDAN', 'Toyota Camry', 'Silver', 4, 45, 'AVAILABLE', None),
                (105, 'TRUCK', 'Ford F-150', 'White', 3, 70, 'AVAILABLE', None),
                (106, 'SUV', 'Chevrolet Tahoe', 'Black', 8, 65, 'AVAILABLE', None),
                (107, 'SEDAN', 'Nissan Altima', 'Gray', 4, 42, 'AVAILABLE', None),
                (108, 'COMPACT', 'Toyota Corolla', 'Red', 4, 35, 'AVAILABLE', None),
                (109, 'SUV', 'Jeep Grand Cherokee', 'White', 5, 55, 'AVAILABLE', None),
                (110, 'LUXURY', 'BMW 5 Series', 'Black', 4, 90, 'AVAILABLE', None),
                (111, 'LUXURY', 'Mercedes E-Class', 'Silver', 4, 95, 'AVAILABLE', None),
                (112, 'SPORTS', 'Porsche 911', 'Red', 2, 150, 'AVAILABLE', None),
                (113, 'COMPACT', 'Honda Fit', 'Blue', 4, 30, 'AVAILABLE', None),
                (114, 'MINIVAN', 'Honda Odyssey', 'Gray', 7, 60, 'AVAILABLE', None),
                (115, 'TRUCK', 'Chevrolet Silverado', 'Black', 3, 75, 'AVAILABLE', None),
                (116, 'HYBRID', 'Toyota Prius', 'Green', 4, 48, 'AVAILABLE', None)
            ]
            
            insert_query = '''INSERT INTO cars 
                            (Car_no, Car_class, Model_name, Car_color, Capacity, Daily_Rent, Car_Status, Rent_ID) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            cursor.executemany(insert_query, sample_cars)
        
        conn.commit()
        return conn
    except mysql.connector.Error as err:
        st.error(f"Database Error: {err}")
        st.stop()

def execute_query(conn, query, params=None, fetch=False):
    """Execute a query with proper error handling"""
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid else None
    except mysql.connector.Error as err:
        st.error(f"Query Error: {err}")
        conn.rollback()
        return None

def view_all_cars(conn):
    st.header("All Cars in Inventory")
    query = "SELECT * FROM cars"
    results = execute_query(conn, query, fetch=True)
    
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.info("No cars in inventory.")

def view_available_cars(conn):
    st.header("Available Cars for Rent")
    query = "SELECT * FROM cars WHERE Car_Status='AVAILABLE'"
    results = execute_query(conn, query, fetch=True)
    
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.info("No cars available for rent.")

def rent_car(conn):
    st.header("Rent a Car")
    
    query = "SELECT Car_no, Car_class, Model_name, Daily_Rent FROM cars WHERE Car_Status='AVAILABLE'"
    available_cars = execute_query(conn, query, fetch=True)
    
    if not available_cars:
        st.warning("No cars available for rent.")
        return
    
    available_df = pd.DataFrame(available_cars)
    car_options = [f"{row['Car_no']} - {row['Car_class']} {row['Model_name']} (${row['Daily_Rent']}/day)" 
                  for _, row in available_df.iterrows()]
    selected_car = st.selectbox("Select a Car", car_options)
    car_no = int(selected_car.split(" - ")[0])
    
    query = "SELECT * FROM cars WHERE Car_no=%s"
    car_details = execute_query(conn, query, (car_no,), fetch=True)[0]
    
    st.subheader("Customer Information")
    cust_name = st.text_input("Full Name")
    cust_phone = st.text_input("Phone Number")
    
    st.subheader("Rental Details")
    today = datetime.now().date()
    rent_date = st.date_input("Rental Date", today)
    return_date = st.date_input("Return Date", today + timedelta(days=1))
    
    if return_date <= rent_date:
        st.error("Return date must be after rental date.")
        return
    
    duration = (return_date - rent_date).days
    total_rent = duration * car_details['Daily_Rent']
    
    driver = st.radio("Need a driver? (Additional $20/day)", ("No", "Yes"))
    if driver == "Yes":
        total_rent += duration * 20
    
    st.subheader("Payment Summary")
    st.write(f"Car: {car_details['Car_class']} {car_details['Model_name']}")
    st.write(f"Rental Period: {duration} days")
    st.write(f"Daily Rate: ${car_details['Daily_Rent']}")
    if driver == "Yes":
        st.write("Driver Fee: $20/day")
    st.write(f"Total Rent: ${total_rent}")
    
    if st.button("Confirm Rental"):
        if not cust_name or not cust_phone:
            st.error("Please fill in all customer details.")
            return
        
        # Insert rental record
        insert_query = '''INSERT INTO rentings 
                        (Cust_Name, Cust_Phone_no, Car_no, Date_Rented, Return_Date, Driver, Total_Rent)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)'''
        params = (cust_name, cust_phone, car_no, 
                 rent_date.strftime("%Y-%m-%d"), 
                 return_date.strftime("%Y-%m-%d"), 
                 driver, total_rent)
        
        rent_id = execute_query(conn, insert_query, params)
        
        if rent_id:
            # Update car status
            update_query = "UPDATE cars SET Car_Status='RENTED', Rent_ID=%s WHERE Car_no=%s"
            execute_query(conn, update_query, (rent_id, car_no))
            st.success(f"Car rented successfully! Rent ID: {rent_id}")

def generate_rent_receipt(conn):
    st.header("Generate Rent Receipt")
    rent_id = st.number_input("Enter Rent ID", min_value=1, step=1)
    
    if st.button("Generate Receipt"):
        query = '''SELECT r.Rent_ID, r.Cust_Name, r.Cust_Phone_no, 
                         c.Car_no, c.Car_class, c.Model_name, c.Car_color,
                         r.Date_Rented, r.Return_Date, r.Driver, r.Total_Rent
                  FROM rentings r
                  JOIN cars c ON r.Car_no = c.Car_no
                  WHERE r.Rent_ID=%s'''
        
        result = execute_query(conn, query, (rent_id,), fetch=True)
        
        if result:
            rental = result[0]
            st.subheader("Rental Receipt")
            st.write(f"Receipt ID: {rental['Rent_ID']}")
            st.write(f"Customer Name: {rental['Cust_Name']}")
            st.write(f"Phone Number: {rental['Cust_Phone_no']}")
            st.write(f"Car Details: {rental['Car_class']} {rental['Model_name']} ({rental['Car_color']}) - #{rental['Car_no']}")
            st.write(f"Rental Period: {rental['Date_Rented']} to {rental['Return_Date']}")
            st.write(f"Driver Option: {rental['Driver']}")
            st.write(f"Total Amount: ${rental['Total_Rent']}")
        else:
            st.error("Rent ID not found.")

def return_car(conn):
    st.header("Return a Rented Car")
    
    query = '''SELECT r.Rent_ID, c.Car_no, c.Car_class, c.Model_name, r.Cust_Name 
               FROM rentings r
               JOIN cars c ON r.Car_no = c.Car_no
               WHERE c.Car_Status='RENTED' '''
    
    rented_cars = execute_query(conn, query, fetch=True)
    
    if not rented_cars:
        st.warning("No cars currently rented out.")
        return
    
    rented_df = pd.DataFrame(rented_cars)
    car_options = [f"Rent ID: {row['Rent_ID']} - Car #{row['Car_no']}: {row['Car_class']} {row['Model_name']} (Rented by: {row['Cust_Name']})" 
                   for _, row in rented_df.iterrows()]
    selected_car = st.selectbox("Select a Rental", car_options)
    rent_id = int(selected_car.split(" - ")[0].split(": ")[1])
    
    query = '''SELECT r.Rent_ID, c.Car_no, r.Total_Rent 
               FROM rentings r
               JOIN cars c ON r.Car_no = c.Car_no
               WHERE r.Rent_ID=%s'''
    
    rental = execute_query(conn, query, (rent_id,), fetch=True)[0]
    
    st.write(f"Car to be returned: #{rental['Car_no']}")
    st.write(f"Total Rent Paid: ${rental['Total_Rent']}")
    
    damage_fee = st.number_input("Damage Fee (if any)", min_value=0, value=0)
    late_fee = st.number_input("Late Return Fee (if any)", min_value=0, value=0)
    total_fees = damage_fee + late_fee
    
    if total_fees > 0:
        st.write(f"Additional Fees: ${total_fees}")
    
    if st.button("Confirm Return"):
        update_query = "UPDATE cars SET Car_Status='AVAILABLE', Rent_ID=NULL WHERE Car_no=%s"
        execute_query(conn, update_query, (rental['Car_no'],))
        
        if total_fees > 0:
            st.warning(f"Additional fees of ${total_fees} collected")
        
        st.success(f"Car #{rental['Car_no']} returned successfully!")

def view_rent_history(conn):
    st.header("Rental History")
    query = '''SELECT r.Rent_ID, r.Cust_Name, c.Car_no, c.Model_name, 
                      r.Date_Rented, r.Return_Date, r.Total_Rent
               FROM rentings r
               JOIN cars c ON r.Car_no = c.Car_no
               ORDER BY r.Date_Rented DESC'''
    
    results = execute_query(conn, query, fetch=True)
    
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
        st.subheader("Rental Statistics")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rentals", len(df))
        col2.metric("Total Revenue", f"${df['Total_Rent'].sum()}")
        
        # Convert string dates to datetime
        df['Date_Rented'] = pd.to_datetime(df['Date_Rented'])
        df['Return_Date'] = pd.to_datetime(df['Return_Date'])
        avg_duration = (df['Return_Date'] - df['Date_Rented']).dt.days.mean()
        col3.metric("Avg Rental Duration", f"{avg_duration:.1f} days")
    else:
        st.warning("No rental history found.")

def admin_portal(conn):
    st.header("Admin Portal")
    password = st.text_input("Enter Admin Password", type="password")
    
    query = "SELECT password FROM admins"
    result = execute_query(conn, query, fetch=True)
    correct_password = result[0]['password']
    
    if password != correct_password:
        st.error("Incorrect password")
        return
    
    st.success("Logged in as Admin")
    
    admin_menu = ["Add New Car", "Update Car Status", "View All Rentals", "Change Admin Password"]
    admin_choice = st.selectbox("Admin Options", admin_menu)
    
    if admin_choice == "Add New Car":
        add_new_car(conn)
    elif admin_choice == "Update Car Status":
        update_car_status(conn)
    elif admin_choice == "View All Rentals":
        view_all_rentals(conn)
    elif admin_choice == "Change Admin Password":
        change_admin_password(conn)

def add_new_car(conn):
    st.subheader("Add New Car to Inventory")
    
    car_no = st.number_input("Car Number", min_value=1, step=1)
    car_class = st.selectbox("Car Class", ["SUV", "SEDAN", "TRUCK", "COMPACT", "LUXURY", "SPORTS", "MINIVAN", "HYBRID"])
    model_name = st.text_input("Model Name")
    car_color = st.text_input("Color")
    capacity = st.number_input("Seating Capacity", min_value=1, max_value=10, step=1)
    daily_rent = st.number_input("Daily Rent ($)", min_value=1, step=1)
    
    if st.button("Add Car"):
        query = "SELECT Car_no FROM cars WHERE Car_no=%s"
        result = execute_query(conn, query, (car_no,), fetch=True)
        
        if not result:
            insert_query = '''INSERT INTO cars 
                          (Car_no, Car_class, Model_name, Car_color, Capacity, Daily_Rent)
                          VALUES (%s, %s, %s, %s, %s, %s)'''
            params = (car_no, car_class, model_name, car_color, capacity, daily_rent)
            execute_query(conn, insert_query, params)
            st.success(f"Car #{car_no} added successfully!")
        else:
            st.error(f"Car #{car_no} already exists.")

def update_car_status(conn):
    st.subheader("Update Car Status")
    query = "SELECT Car_no, Model_name, Car_Status FROM cars"
    results = execute_query(conn, query, fetch=True)
    
    if not results:
        st.warning("No cars in the database.")
        return
    
    cars_df = pd.DataFrame(results)
    car_options = [f"#{row['Car_no']} - {row['Model_name']} (Current: {row['Car_Status']})" 
                   for _, row in cars_df.iterrows()]
    selected_car = st.selectbox("Select a Car", car_options)
    car_no = int(selected_car.split(" - ")[0][1:])
    
    current_status = cars_df[cars_df['Car_no'] == car_no]['Car_Status'].values[0]
    new_status = st.selectbox("New Status", ["AVAILABLE", "RENTED", "MAINTENANCE"])
    
    if st.button("Update Status") and new_status != current_status:
        if new_status == "AVAILABLE":
            query = "SELECT Rent_ID FROM cars WHERE Car_no=%s"
            result = execute_query(conn, query, (car_no,), fetch=True)
            rent_id = result[0]['Rent_ID']
            
            if rent_id is not None:
                st.error("Cannot set to AVAILABLE - car has active rental.")
                return
        
        update_query = "UPDATE cars SET Car_Status=%s WHERE Car_no=%s"
        execute_query(conn, update_query, (new_status, car_no))
        st.success(f"Car #{car_no} status updated to {new_status}")

def view_all_rentals(conn):
    st.subheader("All Rental Records")
    query = '''SELECT r.Rent_ID, r.Cust_Name, r.Cust_Phone_no, 
                      c.Car_no, c.Model_name, 
                      r.Date_Rented, r.Return_Date, r.Total_Rent
               FROM rentings r
               JOIN cars c ON r.Car_no = c.Car_no
               ORDER BY r.Date_Rented DESC'''
    
    results = execute_query(conn, query, fetch=True)
    
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
        if st.button("Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", data=csv, file_name="rental_records.csv", mime="text/csv")
    else:
        st.warning("No rental records found.")

def change_admin_password(conn):
    st.subheader("Change Admin Password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Change Password"):
        if not new_password:
            st.error("Password cannot be empty.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif len(new_password) > 50:
            st.error("Password must be 50 characters or less.")
        else:
            update_query = "UPDATE admins SET password=%s"
            execute_query(conn, update_query, (new_password,))
            st.success("Password changed successfully!")

def main():
    st.set_page_config(page_title="Car Rental Management System", layout="wide")
    conn = init_db()
    
    st.title("🚗 Car Rental Management System")
    
    menu = ["View All Cars", "View Available Cars", "Rent Car", "Generate Rent Receipt", 
            "Return Car", "View Rent History", "Admin Portal"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "View All Cars":
        view_all_cars(conn)
    elif choice == "View Available Cars":
        view_available_cars(conn)
    elif choice == "Rent Car":
        rent_car(conn)
    elif choice == "Generate Rent Receipt":
        generate_rent_receipt(conn)
    elif choice == "Return Car":
        return_car(conn)
    elif choice == "View Rent History":
        view_rent_history(conn)
    elif choice == "Admin Portal":
        admin_portal(conn)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Credits")
    st.sidebar.markdown("Developed by Ananya, Ritisha, Saanvi")
    st.sidebar.markdown("Version 1.0")
    
    # Close the MySQL connection
    if 'conn' in locals() and conn.is_connected():
        conn.close()

if __name__ == "__main__":
    main()