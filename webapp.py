import streamlit as st
import pandas as pd
import os
import pickle
import bcrypt

# File paths
DATA_FILE = 'data.csv'
USERS_FILE = 'users.pkl'

# Initialize users
def init_users():
    default_users = {
        "admin": {"password": hash_password("admin123"), "full_name": "Admin User"}
    }
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'wb') as f:
            pickle.dump(default_users, f)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode(), stored_password.encode())

# Function to save users to a pickle file
def save_users(users):
    with open(USERS_FILE, 'wb') as f:
        pickle.dump(users, f)

# Function to load users from a pickle file
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'rb') as f:
            return pickle.load(f)
    else:
        init_users()
        return load_users()

# Function to save data to CSV
def save_data(data):
    data.to_csv(DATA_FILE, index=False)

# Function to load data from CSV
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=['Full Name', 'Email', 'Phone 📞', 'PC Name/Brand 💻', 'Price 💵', 'Note 📝'])

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'users' not in st.session_state:
    st.session_state.users = load_users()

# Login function
def login(username, password):
    users = st.session_state.users
    if username in users and verify_password(users[username]['password'], password):
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success(f"Welcome, {users[username]['full_name']}!")
    else:
        st.error("Invalid credentials.")

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""

# Add new user function (admin only)
def add_user(username, password, full_name):
    users = st.session_state.users
    if username in users:
        st.error("Username already exists.")
    else:
        hashed_password = hash_password(password)
        users[username] = {"password": hashed_password, "full_name": full_name}
        save_users(users)
        st.success(f"User '{username}' added successfully!")

# Remove user function (admin only)
def remove_user(username):
    users = st.session_state.users
    if username in users:
        del users[username]
        save_users(users)
        st.success(f"User '{username}' removed successfully!")
    else:
        st.error("User not found.")

# Function to delete a data entry
def delete_entry(index):
    if not st.session_state.data.empty and index < len(st.session_state.data):
        st.session_state.data = st.session_state.data.drop(index).reset_index(drop=True)
        save_data(st.session_state.data)
        st.success("Entry deleted!")
    else:
        st.error("Invalid index. Please ensure the index is within the range of available entries.")

# Apply custom styles
st.markdown("""
    <style>
    .title {
        font-size: 2.5em;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5em;
    }
    .subtitle {
        font-size: 1.8em;
        color: #34495e;
        margin-bottom: 1em;
    }
    .button {
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        cursor: pointer;
        font-size: 1em;
    }
    .button:hover {
        background-color: #2980b9;
    }
    .success {
        color: #2ecc71;
    }
    .error {
        color: #e74c3c;
    }
    .sidebar .sidebar-content {
        background-color: #ecf0f1;
    }
    .container {
        padding: 2em;
    }
    .input {
        margin-bottom: 1em;
    }
    </style>
""", unsafe_allow_html=True)

# Login page
if not st.session_state.logged_in:
    st.title('Bad Trade')
    st.markdown("<h2 class='title'>Login to Your Account</h2>", unsafe_allow_html=True)
    st.markdown("Please log in to access the dashboard.")
    
    username = st.text_input('Username', placeholder='Enter your username', key='login_username')
    password = st.text_input('Password', type='password', placeholder='Enter your password', key='login_password')
    
    if st.button('Login', key='login_button'):
        login(username, password)

else:
    # Logout button
    st.sidebar.button('Logout', on_click=logout, key='logout_button')

    # Main content
    user_full_name = st.session_state.users[st.session_state.username]['full_name']
    is_admin = st.session_state.username == "admin"

    st.title('Dad Trade')
    st.markdown(f"<h2 class='title'>Welcome, {user_full_name}!</h2>", unsafe_allow_html=True)

    if is_admin:
        st.sidebar.header('Admin Actions')

        with st.sidebar.expander('Admin Controls'):
            if st.button('Clear All Data', key='clear_data'):
                st.session_state.data = pd.DataFrame(columns=['Full Name', 'Email', 'Phone 📞', 'PC Name/Brand 💻', 'Price 💵', 'Note 📝'])
                save_data(st.session_state.data)
                st.sidebar.success('Data cleared.')

            if st.button('Download All Data', key='download_data'):
                st.download_button(
                    label='Download CSV',
                    data=st.session_state.data.to_csv(index=False),
                    file_name='all_data.csv',
                    mime='text/csv'
                )

        with st.sidebar.expander('Add New User'):
            new_username = st.text_input('New Username', key='new_username')
            new_password = st.text_input('New Password', type='password', key='new_password')
            new_full_name = st.text_input('Full Name', key='new_full_name')
            if st.button('Add User', key='add_user'):
                if all([new_username, new_password, new_full_name]):
                    add_user(new_username, new_password, new_full_name)
                else:
                    st.error('Please fill out all fields.')

        with st.sidebar.expander('Remove User'):
            remove_username = st.selectbox('Select User to Remove', options=[user for user in st.session_state.users if user != 'admin'], key='remove_username')
            if st.button('Remove User', key='remove_user'):
                remove_user(remove_username)

        with st.sidebar.expander('Delete Data Entry'):
            if not st.session_state.data.empty:
                delete_index = st.number_input(
                    'Index of Entry to Delete',
                    min_value=0,
                    max_value=len(st.session_state.data)-1,
                    step=1,
                    key='delete_index'
                )
                if st.button('Delete Entry', key='delete_entry'):
                    delete_entry(delete_index)
            else:
                st.error("No entries available to delete.")

        # Data entry form (admin only)
        st.subheader('Add New Entry')
        selected_user = st.selectbox('Select User for Data Entry', options=list(st.session_state.users.keys()), key='select_user')

        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input('Full Name', value=st.session_state.users[selected_user]['full_name'], key='entry_full_name')
            email = st.text_input('Email 📧', key='entry_email')
            phone = st.text_input('Phone 📞', key='entry_phone')

        with col2:
            pc_name_brand = st.text_input('PC Name/Brand 💻', key='entry_pc_name_brand')
            price = st.number_input('Price 💵', min_value=0.0, step=0.01, key='entry_price')
            note = st.text_input('Note 📝', key='entry_note')

        if st.button('Add Entry', key='add_entry'):
            if all([full_name, email, phone, pc_name_brand, price, note]):
                new_entry = pd.DataFrame([{
                    'Full Name': full_name,
                    'Email': email,
                    'Phone 📞': phone,
                    'PC Name/Brand 💻': pc_name_brand,
                    'Price 💵': price,
                    'Note 📝': note
                }])
                st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
                save_data(st.session_state.data)
                st.success('Entry added!')
            else:
                st.error('Please fill out all fields.')

        # Admin can view all data
        st.subheader('View All Data')

        # Display data
        data_to_display = st.session_state.data
        st.dataframe(data_to_display, use_container_width=True)

    else:
        # Regular user view
        st.subheader('Your Data')
        user_data = st.session_state.data[st.session_state.data['Full Name'] == user_full_name]

        st.dataframe(user_data, use_container_width=True)

        # Download button to export data as CSV
        st.download_button(
            label='Download CSV',
            data=user_data.to_csv(index=False),
            file_name=f"{user_full_name}_data.csv",
            mime='text/csv'
        )
