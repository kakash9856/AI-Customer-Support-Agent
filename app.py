
import pandas as pd
import streamlit as st

from agents.support_agent import run_support_agent

from database.auth_db import (
    register_user,
    login_user
)

from database.ticket_db import (
    create_ticket,
    get_all_tickets,
    get_customer_tickets,
    search_ticket,
    update_ticket_status
)


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Customer Support Agent",
    page_icon="🤖",
    layout="wide"
)


# ---------------- CUSTOM CSS ----------------

with open("style.css", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )


# ---------------- SESSION STATE ----------------

if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_tickets" not in st.session_state:
    st.session_state.show_tickets = False


# ---------------- AUTHENTICATION ----------------

if st.session_state.user is None:

    with st.container(key="auth_page"):

        st.title("🤖 AI Support Hub")
        st.caption("Your intelligent customer support assistant")

        st.divider()

        login_tab, register_tab = st.tabs(
            ["🔐 Login", "✨ Create Account"]
        )

        # -------- LOGIN --------

        with login_tab:

            st.subheader("Welcome Back!")
            st.write("Sign in to continue to your account.")

            login_email = st.text_input(
                "Email Address",
                placeholder="Enter your email",
                key="login_email"
            )

            login_password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )

            if st.button(
                "Login →",
                key="login_button",
                use_container_width=True
            ):

                if not login_email.strip() or not login_password:
                    st.warning("Please enter email and password.")

                else:
                    user = login_user(
                        login_email.strip(),
                        login_password
                    )

                    if user:
                        st.session_state.user = user
                        st.session_state.messages = []
                        st.session_state.show_tickets = False

                        st.success("Login successful!")
                        st.rerun()

                    else:
                        st.error("Invalid email or password.")

        # -------- REGISTER --------

        with register_tab:

            st.subheader("Create Your Account")
            st.write("Join us for smarter customer support.")

            reg_name = st.text_input(
                "Full Name",
                placeholder="Enter your full name",
                key="reg_name"
            )

            reg_email = st.text_input(
                "Email Address",
                placeholder="Enter your email",
                key="reg_email"
            )

            reg_password = st.text_input(
                "Create Password",
                type="password",
                placeholder="Minimum 8 characters",
                key="reg_password"
            )

            if st.button(
                "Create Account →",
                key="register_button",
                use_container_width=True
            ):

                if (
                    not reg_name.strip()
                    or not reg_email.strip()
                    or not reg_password
                ):
                    st.warning("Please fill in all fields.")

                elif len(reg_password) < 8:
                    st.warning(
                        "Password must be at least 8 characters."
                    )

                elif "@" not in reg_email or "." not in reg_email:
                    st.warning("Please enter a valid email address.")

                else:
                    success, message = register_user(
                        reg_name.strip(),
                        reg_email.strip(),
                        reg_password
                    )

                    if success:
                        st.success(message)
                        st.info(
                            "Now open Login tab and sign in."
                        )

                    else:
                        st.error(message)

    st.stop()


# ---------------- LOGGED-IN USER ----------------

user = st.session_state.user
is_admin = user.get("role") == "admin"

st.title("🤖 AI Customer Support Agent")
st.caption("Powered by Gemini + RAG + ChromaDB + LangGraph")

if is_admin:
    st.success("🛠️ Admin Dashboard")
else:
    st.info("👤 Customer Dashboard")


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.success(f"Welcome, {user['name']}!")
    st.write("Role:", user.get("role", "customer").title())

    if st.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.user = None
        st.session_state.messages = []
        st.session_state.show_tickets = False

        if "search_result" in st.session_state:
            del st.session_state.search_result

        st.rerun()

    st.divider()
    st.header("Support Options")

    if st.button(
        "Clear Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    # -------- CUSTOMER TICKET CREATION --------

    if not is_admin:

        st.divider()
        st.subheader("🎫 Create Support Ticket")

        customer_name = st.text_input(
            "Your Name",
            value=user["name"],
            key="manual_customer_name"
        )

        customer_email = st.text_input(
            "Your Email",
            value=user["email"],
            key="manual_customer_email"
        )

        issue = st.text_area(
            "Describe Your Issue",
            key="manual_issue"
        )

        if st.button(
            "Create Ticket",
            use_container_width=True
        ):

            if issue.strip():

                try:
                    ticket_id = create_ticket(
                        issue=issue.strip(),
                        customer_name=customer_name.strip(),
                        customer_email=customer_email.strip(),
                        user_id=user["id"]
                    )

                    st.success(
                        f"Ticket created! ID: {ticket_id}"
                    )
                    st.rerun()

                except Exception as e:
                    st.error(f"Ticket creation failed: {e}")

            else:
                st.warning("Please describe your issue.")

    # -------- ADMIN CONTROLS --------

    if is_admin:

        st.divider()
        st.subheader("🛠️ Admin Ticket Management")

        if st.button(
            "View All Tickets",
            use_container_width=True
        ):
            st.session_state.show_tickets = True

        search_id = st.text_input(
            "Search Ticket ID",
            key="admin_search_id"
        )

        if st.button(
            "Search Ticket",
            use_container_width=True
        ):

            if search_id.strip():

                try:
                    ticket = search_ticket(
                        search_id.strip().upper(),
                        user["id"]
                    )

                    if ticket:
                        st.session_state.search_result = ticket
                    else:
                        st.session_state.search_result = "Not Found"

                except PermissionError:
                    st.error("Admin authorization failed.")

            else:
                st.warning("Enter a Ticket ID.")


# ---------------- ADMIN DASHBOARD ----------------

if is_admin:

    st.header("📊 Ticket Analytics Dashboard")

    try:
        tickets = get_all_tickets(user["id"])

    except PermissionError:
        st.error("You are not authorized to view all tickets.")
        st.stop()

    if tickets:

        df = pd.DataFrame(
            tickets,
            columns=[
                "Ticket ID",
                "Customer Name",
                "Customer Email",
                "Issue",
                "Status",
                "Created At",
                "User ID"
            ]
        )

        total_tickets = len(df)
        open_tickets = len(df[df["Status"] == "Open"])
        in_progress = len(df[df["Status"] == "In Progress"])
        resolved_tickets = len(df[df["Status"] == "Resolved"])

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Tickets", total_tickets)
        col2.metric("Open Tickets", open_tickets)
        col3.metric("In Progress", in_progress)
        col4.metric("Resolved", resolved_tickets)

        st.subheader("📈 Daily Ticket Trends")

        df["Created At"] = pd.to_datetime(df["Created At"])

        daily_tickets = (
            df.groupby(df["Created At"].dt.date)
            .size()
            .reset_index(name="Ticket Count")
        )

        daily_tickets.columns = ["Date", "Ticket Count"]

        st.bar_chart(
            daily_tickets,
            x="Date",
            y="Ticket Count"
        )

        st.subheader("📌 Ticket Status Distribution")

        status_counts = (
            df["Status"]
            .value_counts()
            .reset_index()
        )

        status_counts.columns = ["Status", "Count"]

        st.bar_chart(
            status_counts,
            x="Status",
            y="Count"
        )

    else:
        st.info("No tickets available yet.")

    # -------- ADMIN: ALL TICKETS --------

    if st.session_state.show_tickets:

        st.divider()
        st.subheader("📋 All Support Tickets")

        if tickets:

            for ticket in tickets:

                with st.expander(
                    f"{ticket[0]} - {ticket[4]}"
                ):

                    st.write("Customer:", ticket[1])
                    st.write("Email:", ticket[2])
                    st.write("Issue:", ticket[3])
                    st.write("Created At:", ticket[5])
                    st.write("User ID:", ticket[6])

                    statuses = [
                        "Open",
                        "In Progress",
                        "Resolved"
                    ]

                    new_status = st.selectbox(
                        "Update Status",
                        statuses,
                        index=statuses.index(ticket[4]),
                        key=f"status_{ticket[0]}"
                    )

                    if st.button(
                        "Save Status",
                        key=f"save_{ticket[0]}"
                    ):

                        try:
                            updated = update_ticket_status(
                                ticket[0],
                                new_status,
                                user["id"]
                            )

                            if updated:
                                st.success(
                                    "Ticket status updated!"
                                )
                                st.rerun()

                            else:
                                st.error(
                                    "Unable to update ticket."
                                )

                        except PermissionError:
                            st.error(
                                "Only admins can update ticket status."
                            )

        else:
            st.info("No tickets found.")

    # -------- ADMIN: SEARCH RESULT --------

    if "search_result" in st.session_state:

        result = st.session_state.search_result

        st.divider()
        st.subheader("🔎 Ticket Search Result")

        if result == "Not Found":
            st.warning("Ticket not found.")

        else:
            st.write("Ticket ID:", result[0])
            st.write("Customer:", result[1])
            st.write("Email:", result[2])
            st.write("Issue:", result[3])
            st.write("Status:", result[4])
            st.write("Created At:", result[5])


# ---------------- CUSTOMER TICKET HISTORY ----------------

if not is_admin:

    st.header("🎫 My Support Tickets")

    try:
        my_tickets = get_customer_tickets(
            user["id"],
            user["id"]
        )

        if my_tickets:

            for ticket in my_tickets:

                with st.expander(
                    f"{ticket[0]} - {ticket[4]}"
                ):

                    st.write("Ticket ID:", ticket[0])
                    st.write("Customer:", ticket[1])
                    st.write("Email:", ticket[2])
                    st.write("Issue:", ticket[3])
                    st.write("Status:", ticket[4])
                    st.write("Created At:", ticket[5])

        else:
            st.info(
                "You have not created any support tickets yet."
            )

    except PermissionError:
        st.error("Unable to access your tickets.")


# ---------------- CHAT HISTORY ----------------

st.divider()
st.header("💬 Customer Support Chat")

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------- CUSTOMER INPUT ----------------

user_input = st.chat_input(
    "How can I help you today?"
)

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        with st.spinner("Finding information..."):

            try:
                chat_history = st.session_state.messages[:-1]

                result = run_support_agent(
                    question=user_input,
                    chat_history=chat_history,
                    customer_name=user["name"],
                    customer_email=user["email"],
                    user_id=user["id"]
                )

                answer = result["answer"]
                st.markdown(answer)

            except Exception as e:

                answer = (
                    "Sorry, something went wrong. "
                    "Please try again."
                )

                st.error(f"Error: {e}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })
