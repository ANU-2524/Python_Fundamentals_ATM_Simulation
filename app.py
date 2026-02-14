import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt
# PAGE CONFIG....
st.set_page_config(
    page_title="ATM Simulation",
    layout="wide"
)

# GLOBAL STYLES ...
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}
.main {
    background-color: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
}
.card {
    background: rgba(255, 255, 255, 0.08);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}
.big-font {
    font-size: 28px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Default CONSTANTS...
SAVED_PIN = 3344
MAX_ATTEMPTS = 5
DAILY_LIMIT = 20000

# SESSION STATE INIT...
if "auth" not in st.session_state:
    st.session_state.auth = False

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "balance" not in st.session_state:
    st.session_state.balance = 0

if "withdrawn_today" not in st.session_state:
    st.session_state.withdrawn_today = 0

if "transactions" not in st.session_state:
    st.session_state.transactions = []

if "page" not in st.session_state:
    st.session_state.page = "Home"

if not st.session_state.auth:

    st.title("Secure Login")

    if st.session_state.attempts >= MAX_ATTEMPTS:
        st.error("Bro ! Account Locked. Too many failed attempts.")
        st.stop()

    pin = st.text_input("Enter 4-Digit PIN", type="password")

    if st.button("Login Securely"):
        if pin.isdigit() and int(pin) == SAVED_PIN:
            st.session_state.auth = True
            st.success("Authentication Successful")
            st.rerun()
        else:
            st.session_state.attempts += 1
            st.error(
                f"Incorrect PIN | Attempts left: {MAX_ATTEMPTS - st.session_state.attempts}"
            )

else:

    st.title("💎ATM Dashboard")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="card">
            <p>Total Balance</p>
            <p class="big-font">₹ {st.session_state.balance}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <p>Withdrawn Today</p>
            <p class="big-font">₹ {st.session_state.withdrawn_today}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card">
            <p>Remaining Daily Limit</p>
            <p class="big-font">₹ {DAILY_LIMIT - st.session_state.withdrawn_today}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    menu_options = ["Home", "Deposit", "Withdraw", "Transactions", "Logout"]

    selected = st.sidebar.radio(
        "Navigation",
        menu_options,
        index=menu_options.index(st.session_state.page)
    )

    st.session_state.page = selected
    if st.session_state.page == "Home":

        st.subheader("Balance Overview")

        if st.session_state.transactions:
            df = pd.DataFrame(st.session_state.transactions)
            df = df.sort_values("Time")
            df["Amount"] = df["Amount"].astype(int)
            df["Balance"] = df["Amount"].cumsum()
            df["Time"] =  pd.to_datetime(df["Time"])
            chart = alt.Chart(df).mark_line(point=True).encode(
                x = alt.X("Time:T" , title="Time") , 
                y = alt.Y("Balance:Q" , title="Balance (₹)") , 
                tooltip=['Time' , 'Balance']   ).properties(height=400).interactive()
            
            st.altair_chart(chart , use_container_width=True)
        else:
            st.info("No transactions yet.")

    elif st.session_state.page == "Deposit":

        st.subheader("Deposit Funds")

        amount = st.number_input("Enter Amount", min_value=1, step=1)

        if st.button("Confirm Deposit"):
            st.session_state.balance += amount
            st.session_state.transactions.append({
                "Type": "Deposit",
                "Amount": amount,
                "Time": datetime.now()
            })
            st.success("Deposit Successful , yeyyy !")
            st.rerun()

# WITHDRAW...
    elif st.session_state.page == "Withdraw":

        st.subheader("Withdraw Funds")

        amount = st.number_input("Enter Amount", min_value=1, step=1)

        if st.button("Confirm Withdrawal"):

            if amount > st.session_state.balance:
                st.error("Insufficient Balance")

            elif st.session_state.withdrawn_today + amount > DAILY_LIMIT:
                st.error("Daily Limit Exceeded")

            else:
                st.session_state.balance -= amount
                st.session_state.withdrawn_today += amount

                st.session_state.transactions.append({
                    "Type": "Withdraw",
                    "Amount": -amount,
                    "Time": datetime.now()
                })

                st.success("Withdrawal Successful")
                st.rerun()
# TRANSACTIONS...
    elif st.session_state.page == "Transactions":

        st.subheader("Transaction History")

        if st.session_state.transactions:
            df = pd.DataFrame(st.session_state.transactions)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No transactions yet.")

# LOGOUT...
    elif st.session_state.page == "Logout":

        st.session_state.auth = False
        st.session_state.attempts = 0
        st.session_state.page = "Home"

        st.success("Logged out successfully !")
        st.rerun()
