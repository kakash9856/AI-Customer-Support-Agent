from database.ticket_db import create_ticket

ticket = create_ticket(
    issue="My order has not been delivered."
)

print("Ticket created successfully!")
print("Ticket ID:", ticket)