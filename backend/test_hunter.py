from app.services.hunter_client import find_contacts

contacts = find_contacts("stripe.com")
for c in contacts:
    print(c["first_name"], c["last_name"], "-", c["title"], "-", c["email"])