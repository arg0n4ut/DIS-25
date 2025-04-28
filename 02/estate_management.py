import psycopg
import getpass

DB_DSN = "dbname=dis-2025 user=vsisp26 password=2BpktY2O host=vsisdb.informatik.uni-hamburg.de port=5432"
ADMIN_PASS = "supersecret"  # hard-coded admin


def connect_db():
    return psycopg.connect(DB_DSN)

def admin_login():
    return getpass.getpass("Enter admin password: ") == ADMIN_PASS

# Agent management
def create_agent(conn):
    name, address = input("Agent name: "), input("Agent address: ")
    login, pw = input("Login: "), getpass.getpass("Password: ")
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO estate_agents (name,address,login,password) VALUES (%s,%s,%s,%s)",
            (name,address,login,pw)
        )
    conn.commit(); print("Agent created.")

def list_agents(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT name,address,login FROM estate_agents")
        for row in cur: print(row)

def delete_agent(conn):
    login = input("Login of agent to delete: ")
    with conn.cursor() as cur:
        cur.execute("DELETE FROM estate_agents WHERE login=%s", (login,))
    conn.commit(); print("Deleted agent.")

def agent_management(conn):
    if not admin_login(): print("Invalid admin password."); return
    while True:
        print("[1] Create agent [2] List agents [3] Delete agent [0] Back")
        c = input("> ")
        if c=='1': create_agent(conn)
        elif c=='2': list_agents(conn)
        elif c=='3': delete_agent(conn)
        elif c=='0': break

# Agent login
def agent_login(conn):
    login = input("Login: ")
    pw = getpass.getpass("Password: ")
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM estate_agents WHERE login=%s AND password=%s", (login,pw))
        return cur.fetchone() is not None

# Estate management with subtype support
def create_estate(conn):
    # common fields
    id = input("ID: ")
    city = input("City: ")
    postal_code = input("Postal code: ")
    street = input("Street: ")
    street_number = input("Street number: ")
    square_area = input("Square area: ")
    # insert base
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO estates (id,city,postal_code,street,street_number,square_area) VALUES (%s,%s,%s,%s,%s,%s)",
            (id,city,postal_code,street,street_number,square_area)
        )
    # subtype
    kind = input("Type (house/apartment): ").lower()
    with conn.cursor() as cur:
        if kind == 'house':
            floors = input("Floors: ")
            price = input("Price: ")
            garden = input("Garden (true/false): ")
            cur.execute(
                "INSERT INTO houses (id,floors,price,garden) VALUES (%s,%s,%s,%s)",
                (id,floors,price,garden=='true')
            )
        else:
            floor = input("Apartment floor: ")
            rent = input("Rent: ")
            rooms = input("Rooms: ")
            balcony = input("Balcony (true/false): ")
            kitchen = input("Kitchen (true/false): ")
            cur.execute(
                "INSERT INTO apartments (id,floor,rent,rooms,balcony,kitchen) VALUES (%s,%s,%s,%s,%s,%s)",
                (id,floor,rent,rooms,balcony=='true',kitchen=='true')
            )
    conn.commit(); print("Estate created.")

def list_estates(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM estates")
        for e in cur: print(e)

def delete_estate(conn):
    eid = input("Estate id to delete: ")
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM houses WHERE id=%s", (eid,))
        if cur.fetchone(): cur.execute("DELETE FROM houses WHERE id=%s", (eid,))
        else: cur.execute("DELETE FROM apartments WHERE id=%s", (eid,))
        cur.execute("DELETE FROM estates WHERE id=%s", (eid,))
    conn.commit(); print("Estate deleted.")

def update_estate(conn):
    eid = input("Estate id: ")
    # update base
    city = input("City: ")
    postal_code = input("Postal code: ")
    street = input("Street: ")
    street_number = input("Street number: ")
    square_area = input("Square area: ")
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE estates SET city=%s,postal_code=%s,street=%s,street_number=%s,square_area=%s WHERE id=%s",
            (city,postal_code,street,street_number,square_area,eid)
        )
        cur.execute("SELECT 1 FROM houses WHERE id=%s", (eid,))
        if cur.fetchone():
            floors = input("Floors: ")
            price = input("Price: ")
            garden = input("Garden (true/false): ")
            cur.execute(
                "UPDATE houses SET floors=%s,price=%s,garden=%s WHERE id=%s",
                (floors,price,garden=='true',eid)
            )
        else:
            floor = input("Apartment floor: ")
            rent = input("Rent: ")
            rooms = input("Rooms: ")
            balcony = input("Balcony (true/false): ")
            kitchen = input("Kitchen (true/false): ")
            cur.execute(
                "UPDATE apartments SET floor=%s,rent=%s,rooms=%s,balcony=%s,kitchen=%s WHERE id=%s",
                (floor,rent,rooms,balcony=='true',kitchen=='true',eid)
            )
    conn.commit(); print("Estate updated.")

def estate_management(conn):
    if not agent_login(conn): print("Login failed."); return
    while True:
        print("[1] Create estate [2] List [3] Update [4] Delete [0] Back")
        c=input("> ")
        if c=='1': create_estate(conn)
        elif c=='2': list_estates(conn)
        elif c=='3': update_estate(conn)
        elif c=='4': delete_estate(conn)
        elif c=='0': break

# Contract management
def insert_person(conn):
    fn, name, addr = input("First name: "), input("Name: "), input("Address: ")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO person (first_name,name,address) VALUES (%s,%s,%s)", (fn,name,addr))
    conn.commit(); print("Person added.")

def sign_contract(conn):
    num,date,place = input("Contract number: "), input("Date (YYYY-MM-DD): "), input("Place: ")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO contracts (number,date,place) VALUES (%s,%s,%s)", (num,date,place))
    typ = input("Type (tenancy/purchase): ")
    with conn.cursor() as cur:
        if typ=='tenancy':
            sd,dur,ac = input("Start date: "), input("Duration (months): "), input("Additional costs: ")
            cur.execute("INSERT INTO tenancy_contracts (number,start_date,duration,additional_costs) VALUES (%s,%s,%s,%s)", (num,sd,dur,ac))
        else:
            inst,rate = input("# installments: "), input("Interest rate: ")
            cur.execute("INSERT INTO purchase_contracts (number,number_installments,interest_rate) VALUES (%s,%s,%s)", (num,inst,rate))
    conn.commit(); print("Contract signed.")

def list_contracts(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM contracts")
        for r in cur: print(r)

def contract_management(conn):
    while True:
        print("[1] Insert person [2] Sign contract [3] List contracts [0] Back")
        c=input("> ")
        if c=='1': insert_person(conn)
        elif c=='2': sign_contract(conn)
        elif c=='3': list_contracts(conn)
        elif c=='0': break

def main():
    conn = connect_db()
    while True:
        print("Modes: [1] Agents [2] Estates [3] Contracts [0] Exit")
        m = input("> ")
        if m=='1': agent_management(conn)
        elif m=='2': estate_management(conn)
        elif m=='3': contract_management(conn)
        elif m=='0': break
    conn.close()

if __name__ == '__main__':
    main()
