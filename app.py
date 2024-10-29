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

# Add custom CSS for smaller buttons
st.markdown("""
    <style>
    .small-button {
        font-size: 10px;
        padding: 3px 8px;
        margin: 0px 2px;
    }
    .button-container {
        display: flex;
        gap: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Convert employee data to DataFrame and add Action buttons
st.subheader("Employee List")
employee_df = pd.DataFrame(employees, columns=["ID", "Name", "Salary", "Joining Date"])

# Add actions for each row in the table
for index, row in employee_df.iterrows():
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 2])
    with col1:
        st.write(row["ID"])
    with col2:
        st.write(row["Name"])
    with col3:
        st.write(f"${row['Salary']:.2f}")
    with col4:
        st.write(row["Joining Date"])
    with col5:
        # Arrange Edit and Delete buttons in a single row
        edit_col, delete_col = st.columns(2)
        
        # Edit button with icon label
        edit_label = f"🖉"
        delete_label = f"🗑️"
        
        if edit_col.button(edit_label, key=f"edit_{row['ID']}"):
            st.session_state[f"edit_mode_{row['ID']}"] = True
        if delete_col.button(delete_label, key=f"delete_{row['ID']}"):
            delete_employee(row['ID'])
            st.warning(f"Deleted employee: {row['Name']}")
            st.session_state["data_updated"] = True

    # Edit fields within an expander if in edit mode
    if st.session_state.get(f"edit_mode_{row['ID']}", False):
        with st.expander(f"Edit Employee ID: {row['ID']}"):
            new_name = st.text_input("Name", value=row["Name"], key=f"name_{row['ID']}")
            new_salary = st.number_input("Salary", value=row["Salary"], key=f"salary_{row['ID']}")
            new_joining_date = st.date_input("Joining Date", datetime.strptime(row["Joining Date"], "%Y-%m-%d"), key=f"joining_{row['ID']}")

            if st.button("Save Changes", key=f"save_{row['ID']}"):
                update_employee(row['ID'], new_name, new_salary, new_joining_date.strftime("%Y-%m-%d"))
                st.success(f"Updated employee: {new_name}")
                st.session_state[f"edit_mode_{row['ID']}"] = False  # Exit edit mode
                st.session_state["data_updated"] = True  # Trigger data reload
