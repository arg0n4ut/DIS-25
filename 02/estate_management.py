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
            (name, address, login, pw)
        )
    conn.commit(); print("Agent created.")

def list_agents(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT name,address,login FROM estate_agents")
        for r in cur: print(r)

def delete_agent(conn):
    login = input("Login to delete: ")
    with conn.cursor() as cur:
        cur.execute("DELETE FROM estate_agents WHERE login=%s", (login,))
    conn.commit(); print("Deleted.")

def agent_management(conn):
    if not admin_login(): print("Invalid admin password."); return
    while True:
        print("[1] Create agent [2] List agents [3] Delete agent [0] Back")
        c = input("> ")
        if c=='1': create_agent(conn)
        elif c=='2': list_agents(conn)
        elif c=='3': delete_agent(conn)
        elif c=='0': break

# Agent login returns agent identity
def agent_login(conn):
    login = input("Login: ")
    pw = getpass.getpass("Password: ")
    with conn.cursor() as cur:
        cur.execute(
            "SELECT name,address FROM estate_agents WHERE login=%s AND password=%s",
            (login, pw)
        )
        row = cur.fetchone()
    if row: print("Login successful."); return row
    else: print("Login failed."); return None

# Estate management
def create_estate(conn, agent):
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

def list_estates(conn, agent):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT e.id,e.city,e.postal_code,e.street,e.street_number,e.square_area,"
            "h.floors,h.price,h.garden,a.floor,a.rent,a.rooms,a.balcony,a.kitchen "
            "FROM estates e "
            "JOIN manages m ON e.id=m.id AND m.name=%s AND m.address=%s "
            "LEFT JOIN houses h ON e.id=h.id "
            "LEFT JOIN apartments a ON e.id=a.id", (agent[0], agent[1])
        )
        for r in cur:
            eid,city,pc,st,stn,area,floors,price,garden,afloor,rent,rooms,balcony,kitchen = r
            base = f"ID={eid} {city} {pc} {st} {stn} {area}sqm"
            if floors is not None:
                print(base+f" | House: floors={floors}, price={price}, garden={garden}")
            else:
                print(base+f" | Apt: floor={afloor}, rent={rent}, rooms={rooms}, balcony={balcony}, kitchen={kitchen}")

def delete_estate(conn):
    eid = input("Estate id to delete: ")
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM houses WHERE id=%s",(eid,))
        if cur.fetchone(): cur.execute("DELETE FROM houses WHERE id=%s",(eid,))
        else: cur.execute("DELETE FROM apartments WHERE id=%s",(eid,))
        cur.execute("DELETE FROM manages WHERE id=%s",(eid,))
        cur.execute("DELETE FROM estates WHERE id=%s",(eid,))
    conn.commit(); print("Estate deleted.")

def update_estate(conn):
    eid = input("Estate id: ")
    city,pc,st,stn,area = input("City: "),input("Postal code: "),input("Street: "),input("Street number: "),input("Square area: ")
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE estates SET city=%s,postal_code=%s,street=%s,street_number=%s,square_area=%s WHERE id=%s",
            (city,pc,st,stn,area,eid)
        )
        cur.execute("SELECT 1 FROM houses WHERE id=%s",(eid,))
        if cur.fetchone():
            floors,price,garden = input("Floors: "),input("Price: "),input("Garden (true/false): ")
            cur.execute(
                "UPDATE houses SET floors=%s,price=%s,garden=%s WHERE id=%s",
                (floors,price,garden=='true',eid)
            )
        else:
            afloor,rent,rooms,balcony,kitchen = input("Floor: "),input("Rent: "),input("Rooms: "),input("Balcony (true/false): "),input("Kitchen (true/false): ")
            cur.execute(
                "UPDATE apartments SET floor=%s,rent=%s,rooms=%s,balcony=%s,kitchen=%s WHERE id=%s",
                (afloor,rent,rooms,balcony=='true',kitchen=='true',eid)
            )
    conn.commit(); print("Estate updated.")

def estate_management(conn):
    agent = agent_login(conn)
    if not agent: return
    while True:
        print("[1] Create [2] List [3] Update [4] Delete [0] Back")
        c=input("> ")
        if c=='1': create_estate(conn,agent)
        elif c=='2': list_estates(conn,agent)
        elif c=='3': update_estate(conn)
        elif c=='4': delete_estate(conn)
        elif c=='0': break

def insert_person(conn):
     fn, name, addr = input("First name: "), input("Name: "), input("Address: ")
     with conn.cursor() as cur:
         cur.execute(
             "INSERT INTO person (first_name,name,address) VALUES (%s,%s,%s)",
             (fn,name,addr)
         )
     conn.commit(); print("Person added.")

def sign_contract(conn):
    # create base contract
    num = input("Contract number: ")
    date = input("Date (YYYY-MM-DD): ")
    place = input("Place: ")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO contracts (number,date,place) VALUES (%s,%s,%s)", (num, date, place))
    conn.commit()
    typ = input("Type (tenancy/purchase): ")
    if typ == "tenancy":
        sd = input("Start date (YYYY-MM-DD): ")
        dur = input("Duration (months): ")
        ac = input("Additional costs: ")
        eid = input("Estate ID: ")
        fn = input("Renter's First Name: ")
        ln = input("Renter's Last Name: ")
        addr = input("Renter's Address: ")
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tenancy_contracts (number,start_date,duration,additional_costs) VALUES (%s,%s,%s,%s)",
                (num, sd, dur, ac)
            )
            cur.execute(
                "INSERT INTO rents (number,id,first_name,name,address) VALUES (%s,%s,%s,%s,%s)",
                (num, eid, fn, ln, addr)
            )
        conn.commit()
        print("Tenancy contract created.")
    else:
        inst = input("# installments: ")
        rate = input("Interest rate: ")
        eid = input("Estate ID: ")
        fn = input("Buyer's First Name: ")
        ln = input("Buyer's Last Name: ")
        addr = input("Buyer's Address: ")
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO purchase_contracts (number,number_installments,interest_rate) VALUES (%s,%s,%s)",
                (num, inst, rate)
            )
            cur.execute(
                "INSERT INTO sells (id,first_name,name,address,number) VALUES (%s,%s,%s,%s,%s)",
                (eid, fn, ln, addr, num)
            )
        conn.commit()
        print("Purchase contract created.")

# Contract management now requires agent_login and filters by manages
def list_contracts(conn, agent):
    with conn.cursor() as cur:
        # Tenancy contracts for estates managed by agent
        cur.execute(
            "SELECT c.number,c.date,c.place,t.start_date,t.duration,t.additional_costs,p.first_name,p.name,p.address,r.id "
            "FROM contracts c "
            "JOIN tenancy_contracts t ON c.number=t.number "
            "JOIN rents r ON t.number=r.number "
            "JOIN person p ON r.first_name=p.first_name AND r.name=p.name AND r.address=p.address "
            "JOIN manages m ON r.id=m.id AND m.name=%s AND m.address=%s;",
            (agent[0],agent[1])
        )
        print("-- Tenancy Contracts --")
        for num,date,place,sd,dur,ac,fn,ln,addr,eid in cur:
            print(f"#{num} {date} at {place} | Tenancy start={sd}, dur={dur}mo, add_costs={ac} | {fn} {ln} @{addr} | Estate ID={eid}")
        # Purchase contracts
        cur.execute(
            "SELECT c.number,c.date,c.place,pc.number_installments,pc.interest_rate,s.first_name,s.name,s.address,s.id "
            "FROM contracts c "
            "JOIN purchase_contracts pc ON c.number=pc.number "
            "JOIN sells s ON c.number=s.number "
            "JOIN manages m ON s.id=m.id AND m.name=%s AND m.address=%s;",
            (agent[0],agent[1])
        )
        print("-- Purchase Contracts --")
        for num,date,place,ni,ir,fn,ln,addr,eid in cur:
            print(f"#{num} {date} at {place} | Purchase inst={ni}, rate={ir} | {fn} {ln} @{addr} | Estate ID={eid}")

def contract_management(conn):
    agent = agent_login(conn)
    if not agent: return
    while True:
        print("[1] Insert person [2] Sign contract [3] List contracts [0] Back")
        c=input("> ")
        if c=='1': insert_person(conn)
        elif c=='2': sign_contract(conn)
        elif c=='3': list_contracts(conn,agent)
        elif c=='0': break

def main():
    conn = connect_db()
    while True:
        print("Modes:[1]Agents [2]Estates [3]Contracts [0]Exit")
        m=input("> ")
        if m=='1': agent_management(conn)
        elif m=='2': estate_management(conn)
        elif m=='3': contract_management(conn)
        elif m=='0': break
    conn.close()

if __name__=='__main__': main()
