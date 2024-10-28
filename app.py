import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Initialize session state for data updates if not already present
if "data_updated" not in st.session_state:
    st.session_state["data_updated"] = False

# Database functions
def create_employee_table():
    with sqlite3.connect('employees.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                salary REAL,
                joining_date TEXT
            )
        ''')

def add_employee(name, salary, joining_date):
    with sqlite3.connect('employees.db') as conn:
        conn.execute('INSERT INTO employees (name, salary, joining_date) VALUES (?, ?, ?)', (name, salary, joining_date))
        conn.commit()

def get_all_employees():
    with sqlite3.connect('employees.db') as conn:
        return conn.execute('SELECT * FROM employees').fetchall()

def delete_employee(emp_id):
    with sqlite3.connect('employees.db') as conn:
        conn.execute('DELETE FROM employees WHERE id = ?', (emp_id,))
        conn.commit()

def update_employee(emp_id, name, salary, joining_date):
    with sqlite3.connect('employees.db') as conn:
        conn.execute('UPDATE employees SET name = ?, salary = ?, joining_date = ? WHERE id = ?', (name, salary, joining_date, emp_id))
        conn.commit()

# Initialize database and create the employee table
create_employee_table()

# Streamlit app code
st.title("Employee Salary Management System")

# Form to add employee
with st.form("Add Employee"):
    emp_name = st.text_input("Employee Name")
    emp_salary = st.number_input("Salary", min_value=0.0)
    emp_joining_date = st.date_input("Joining Date", datetime.now())
    
    if st.form_submit_button("Add Employee"):
        if emp_name and emp_salary and emp_joining_date:
            add_employee(emp_name, emp_salary, emp_joining_date.strftime("%Y-%m-%d"))
            st.success(f"Added employee: {emp_name}")
            st.session_state["data_updated"] = True  # Trigger data reload
        else:
            st.error("Please fill in all fields.")

# Check if data was updated and reset the flag
if st.session_state["data_updated"]:
    employees = get_all_employees()
    st.session_state["data_updated"] = False
else:
    employees = get_all_employees()

# Display all employees in a table with edit and delete options
st.subheader("Employee List")
employee_df = pd.DataFrame(employees, columns=["ID", "Name", "Salary", "Joining Date"])
st.table(employee_df)  # Display the DataFrame as a table

# Edit/Delete functionality
for index, row in employee_df.iterrows():
    st.write(f"**Employee ID:** {row['ID']} | **Name:** {row['Name']} | **Salary:** {row['Salary']} | **Joining Date:** {row['Joining Date']}")

    # Initializing session state to track edit mode for each employee
    if f"edit_mode_{row['ID']}" not in st.session_state:
        st.session_state[f"edit_mode_{row['ID']}"] = False

    # Toggle edit mode when edit button is clicked
    if st.button(f"Edit {row['Name']}", key=f"edit_{row['ID']}"):
        st.session_state[f"edit_mode_{row['ID']}"] = not st.session_state[f"edit_mode_{row['ID']}"]
    
    # Display editable fields if in edit mode
    if st.session_state[f"edit_mode_{row['ID']}"]:
        emp_name = st.text_input("Update Name", value=row['Name'], key=f"upd_name_{row['ID']}")
        emp_salary = st.number_input("Update Salary", value=row['Salary'], min_value=0.0, key=f"upd_salary_{row['ID']}")
        emp_joining_date = st.date_input("Update Joining Date", datetime.strptime(row['Joining Date'], "%Y-%m-%d"), key=f"upd_date_{row['ID']}")

        # Save changes
        if st.button(f"Save Changes for {row['Name']}", key=f"save_{row['ID']}"):
            update_employee(row['ID'], emp_name, emp_salary, emp_joining_date.strftime("%Y-%m-%d"))
            st.success(f"Updated employee: {emp_name}")
            st.session_state[f"edit_mode_{row['ID']}"] = False  # Exit edit mode after save
            st.session_state["data_updated"] = True  # Trigger data reload

    # Delete Button
    if st.button(f"Delete {row['Name']}", key=f"delete_{row['ID']}"):
        delete_employee(row['ID'])
        st.warning(f"Deleted employee: {row['Name']}")
        st.session_state["data_updated"] = True  # Trigger data reload
