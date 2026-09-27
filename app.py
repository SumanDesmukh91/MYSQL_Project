import streamlit as st
import mysql.connector
import hashlib

# --------------------------
# MYSQL CONNECTION
# --------------------------
def get_connection():
    return mysql.connector.connect(
		host=st.secrets["DB_HOST"],
        port=int(st.secrets["DB_PORT"]),
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"]
    )

# --------------------------
# PASSWORD HASHING
# --------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --------------------------
# CHECK USER EXISTS
# --------------------------
def user_exists(user_id):
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT user_id FROM cust_details WHERE user_id=%s"
    cur.execute(query, (user_id,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result is not None

# --------------------------
# REGISTER USER
# --------------------------
def register_user(full_name, address, phone_number, user_id, password):

    if user_exists(user_id):
        return False, "User ID already exists."

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO cust_details
    (full_name,address,phone_number,user_id,password)
    VALUES(%s,%s,%s,%s,%s)
    """

    data = (
        full_name,
        address,
        phone_number,
        user_id,
        hash_password(password)
    )

    try:
        cur.execute(sql, data)
        conn.commit()

        cur.close()
        conn.close()

        return True, "Registration Successful"

    except Exception as e:
        conn.rollback()

        cur.close()
        conn.close()

        return False, str(e)

# --------------------------
# LOGIN USER
# --------------------------
def login_user(user_id, password):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    query = """
    SELECT *
    FROM cust_details
    WHERE user_id=%s
    """

    cur.execute(query, (user_id,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        if hash_password(password) == user["password"]:
            return user

    return None

# --------------------------
# SESSION STATE
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# --------------------------
# PAGE TITLE
# --------------------------
st.set_page_config(
    page_title="Login Authentication System",
    page_icon="🔐",
    layout="centered"
)

st.title("🔐 Login Authentication System")

# --------------------------
# LOGGED IN PAGE
# --------------------------
if st.session_state.logged_in:

    st.success(f"Welcome {st.session_state.username}")

    st.subheader("Dashboard")

    st.write("You are successfully logged in.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# --------------------------
# LOGIN / REGISTER
# --------------------------
else:

    menu = st.radio(
       "Select Option",
        ["Login", "Register"],
        horizontal=True
    )

    # --------------------------
    # LOGIN
    # --------------------------
    if menu == "Login":

        st.subheader("User Login")

        user_id = st.text_input("User ID")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            user = login_user(user_id, password)

            if user:

                st.session_state.logged_in = True
                st.session_state.username = user["full_name"]

                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Invalid User ID or Password")

    # --------------------------
    # REGISTER
    # --------------------------
    elif menu == "Register":

        st.subheader("New User Registration")

        full_name = st.text_input("Full Name")

        address = st.text_area("Address")

        phone_number = st.text_input("Phone Number")

        user_id = st.text_input("Create User ID")

        password = st.text_input(
            "Create Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button("Register"):

            if not full_name:
                st.warning("Enter Full Name")

            elif not phone_number.isdigit() or len(phone_number) != 10:
                st.warning("Phone number must contain 10 digits")

            elif password != confirm_password:
                st.warning("Passwords do not match")

            else:

                status, msg = register_user(
                    full_name.upper(),
                    address.upper(),
                    phone_number,
                    user_id,
                    password
                )

                if status:
                    st.success(msg)
                else:
                    st.error(msg)
