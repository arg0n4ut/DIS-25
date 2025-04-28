import psycopg
import getpass

DB_DSN = "dbname=dis-2025 user=vsisp26 password=2BpktY2O host=vsisdb.informatik.uni-hamburg.de port=5432"
ADMIN_PASS = "supersecret"  # hard-coded admin


def connect_db():
    return psycopg.connect(DB_DSN)


def admin_login():
    pw = getpass.getpass("Enter admin password: ")
    return pw == ADMIN_PASS


def create_agent(conn):
    name = input("Agent name: ")
    address = input("Agent address: ")
    login = input("Login: ")
    pw = getpass.getpass("Password: ")
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO estate_agents (name, address, login, password) VALUES (%s,%s,%s,%s)",
            (name, address, login, pw)
        )
        conn.commit()
        print("Agent created.")


def list_agents(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT name, address, login FROM estate_agents")
        for row in cur:
            print(row)


def delete_agent(conn):
    login = input("Login of agent to delete: ")
    with conn.cursor() as cur:
        cur.execute("DELETE FROM estate_agents WHERE login=%s", (login,))
        conn.commit()
        print("Deleted.")


def agent_management(conn):
    if not admin_login():
        print("Invalid admin password.")
        return
    while True:
        print("[1] Create agent [2] List agents [3] Delete agent [0] Back")
        c = input("> ")
        if c == '1': create_agent(conn)
        elif c == '2': list_agents(conn)
        elif c == '3': delete_agent(conn)
        elif c == '0': break


def agent_login(conn):
    login = input("Login: ")
    pw = getpass.getpass("Password: ")
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM estate_agents WHERE login=%s AND password=%s",
            (login, pw)
        )
        return cur.fetchone() is not None


def create_estate(conn):
    cols = ["id","city","postal_code","street","street_number","square_area"]
    vals = [input(f"{c}: ") for c in cols]
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO estates ({','.join(cols)}) VALUES (%s,%s,%s,%s,%s,%s)",
            vals
        )
        conn.commit()
        print("Estate added.")


def list_estates(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM estates")
        for e in cur: print(e)


def delete_estate(conn):
    eid = input("Estate id to delete: ")
    with conn.cursor() as cur:
        cur.execute("DELETE FROM estates WHERE id=%s", (eid,))
        conn.commit()
        print("Deleted.")


def update_estate(conn):
    eid = input("Estate id: ")
    field = input("Field to update: ")
    val = input("New value: ")
    with conn.cursor() as cur:
        cur.execute(f"UPDATE estates SET {field}=%s WHERE id=%s", (val, eid))
        conn.commit()
        print("Updated.")


def estate_management(conn):
    if not agent_login(conn):
        print("Login failed.")
        return
    while True:
        print("[1] Create estate [2] List [3] Update [4] Delete [0] Back")
        c = input("> ")
        if c=='1': create_estate(conn)
        elif c=='2': list_estates(conn)
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
    # simple: create base contract
    num = input("Contract number: ")
    date = input("Date (YYYY-MM-DD): ")
    place = input("Place: ")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO contracts (number,date,place) VALUES (%s,%s,%s)", (num,date,place))
        conn.commit()
    typ = input("Type (tenancy/purchase): ")
    if typ=="tenancy":
        sd = input("Start date: ")
        dur = input("Duration (months): ")
        ac = input("Additional costs: ")
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tenancy_contracts (number,start_date,duration,additional_costs) VALUES (%s,%s,%s,%s)",
                (num,sd,dur,ac)
            )
            conn.commit()
    else:
        inst = input("# installments: ")
        rate = input("Interest rate: ")
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO purchase_contracts (number,number_installments,interest_rate) VALUES (%s,%s,%s)",
                (num,inst,rate)
            )
            conn.commit()
    print("Contract signed.")


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

