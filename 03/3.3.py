import psycopg
from time import sleep

db_dsn = ""
with open("login.txt", "r") as file:
    db_dsn = file.readline().strip()

def init_t1_t2():
    sleep(4)
    t1 = psycopg.connect(db_dsn)
    t2 = psycopg.connect(db_dsn)

    # set autocommit to False
    t1.autocommit = False
    t2.autocommit = False
    return t1, t2

def execute_schedule_1():
    print("===== S1 =====")
    # S1 = r1x w2x c2 w1x r1x c1
    # r1x
    t1_cursor = t1.cursor()
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    print("T1 reads:", t1_cursor.fetchall())
    # w2x
    t2_cursor = t2.cursor()
    t2_cursor.execute("UPDATE sheet3 SET name = 'X2' WHERE id = 0")
    # c2
    t2.commit()
    # w1x
    t1_cursor.execute("UPDATE sheet3 SET name = 'X1' WHERE id = 0")
    # r1x
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    # c1
    t1.commit()
    # print the table state
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    print("-> S1 value:", t1_cursor.fetchall())
    t1.close()
    t2.close()

def execute_schedule_2():

    print("\n===== S2 =====")
    # S2 = r1x w2x c2 r1x c1
    # r1x
    t1_cursor = t1.cursor()
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    print("T1 reads:", t1_cursor.fetchall())
    # w2x
    t2_cursor = t2.cursor()
    t2_cursor.execute("UPDATE sheet3 SET name = 'X2' WHERE id = 0")
    # c2
    t2.commit()
    # r1x
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    # c1
    t1.commit()
    # print the table state
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    print("-> S2 value:", t1_cursor.fetchall())
    t1.close()
    t2.close()

def execute_schedule_3():

    print("\n===== S3 =====")
    # S3 = r2x w1x w1y c1 r2y w2x w2y c2
    # r2x
    t2_cursor = t2.cursor()
    t2_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    print("T2 reads:", t2_cursor.fetchall())
    # w1x  
    t1_cursor = t1.cursor()
    t1_cursor.execute("UPDATE sheet3 SET name = 'X1' WHERE id = 0")
    # w1y
    t1_cursor.execute("UPDATE sheet3 SET name = 'Y1' WHERE id = 1")
    # c1
    t1.commit()
    # r2y
    t2_cursor.execute("SELECT name FROM sheet3 WHERE id = 1")
    print("T2 reads:", t2_cursor.fetchall())
    # w2x
    t2_cursor.execute("UPDATE sheet3 SET name = 'X2' WHERE id = 0")
    # w2y
    t2_cursor.execute("UPDATE sheet3 SET name = 'Y2' WHERE id = 1")
    # c2
    t2.commit()
    # print the table state
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0 OR id = 1")
    print("-> S3 value:", t1_cursor.fetchall())
    t1.close()
    t2.close()

# set RC isolation level
t1, t2 = init_t1_t2()
# set transaction isolation level to read committed
t1.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
t2.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
execute_schedule_1()
t1, t2 = init_t1_t2()
t1.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
t2.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
execute_schedule_2()
t1, t2 = init_t1_t2()
t1.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
t2.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
execute_schedule_3()

t1, t2 = init_t1_t2()
print("\nb) Transactions set to serializable")
# set transaction isolation level to serializable
t1.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
t2.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
try:
    execute_schedule_1()
except psycopg.errors.SerializationFailure as e:
    print("Transaction failed:", e)

t1, t2 = init_t1_t2()
t1.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
t2.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
try:
    execute_schedule_2()
except psycopg.errors.SerializationFailure as e:
    print("Transaction failed:", e)

t1, t2 = init_t1_t2()
t1.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
t2.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
try:
    execute_schedule_3()
except psycopg.errors.SerializationFailure as e:
    print("Transaction failed:", e)

print("\nc) RX Locking")

def read_lock(i):
    return f"SELECT * FROM sheet3 WHERE id = {i} FOR SHARE"

def write_lock(i):
    return f"SELECT * FROM sheet3 WHERE id = {i} FOR UPDATE"

def execute_schedule_1_with_locks():
    print("===== S1 with manual row locking =====")
    # S1 = r1x w2x c2 w1x r1x c1
    # r1x
    t1_cursor = t1.cursor()
    t1_cursor.execute(read_lock(0)) # Acquire shared lock
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    print("T1 reads:", t1_cursor.fetchall())
    # w2x
    t2_cursor = t2.cursor()
    t2_cursor.execute(write_lock(0))
    t2_cursor.execute("UPDATE sheet3 SET name = 'X2' WHERE id = 0")
    # c2
    t2.commit()
    # w1x
    t1_cursor.execute(write_lock(0))
    t1_cursor.execute("UPDATE sheet3 SET name = 'X1' WHERE id = 0")
    # r1x
    t1_cursor.execute(read_lock(0))
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    # c1
    t1.commit()
    # print the table state
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    print("-> S1 value:", t1_cursor.fetchall())
    t1.close()
    t2.close()

def execute_schedule_2_with_locks():
    print("\n===== S2 with manual row locking =====")
    # S2 = r1x w2x c2 r1x c1
    # r1x
    t1_cursor = t1.cursor()
    t1_cursor.execute(read_lock(0)) # Acquire shared lock
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    print("T1 reads:", t1_cursor.fetchall())
    # w2x
    t2_cursor = t2.cursor()
    t2_cursor.execute(write_lock(0))
    t2_cursor.execute("UPDATE sheet3 SET name = 'X2' WHERE id = 0")
    # c2
    t2.commit()
    # r1x
    t1_cursor.execute(read_lock(0))
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    # c1
    t1.commit()
    # print the table state
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    print("-> S2 value:", t1_cursor.fetchall())
    t1.close()
    t2.close()

def execute_schedule_3_with_locks():
    print("\n===== S3 with manual row locking =====")
    # S3 = r2x w1x w1y c1 r2y w2x w2y c2
    # r2x
    t2_cursor = t2.cursor()
    t2_cursor.execute(read_lock(0)) # Acquire shared lock
    t2_cursor.execute("SELECT name FROM sheet3 WHERE id = 0")
    print("T2 reads:", t2_cursor.fetchall())
    # w1x
    t1_cursor = t1.cursor()
    t1_cursor.execute(write_lock(0))
    t1_cursor.execute("UPDATE sheet3 SET name = 'X1' WHERE id = 0")
    # w1y
    t1_cursor.execute(write_lock(1))
    t1_cursor.execute("UPDATE sheet3 SET name = 'Y1' WHERE id = 1")
    # c1
    t1.commit()
    # r2y
    t2_cursor.execute(read_lock(1))
    t2_cursor.execute("SELECT name FROM sheet3 WHERE id = 1")
    print("T2 reads:", t2_cursor.fetchall())
    # w2x
    t2_cursor.execute(write_lock(0))
    t2_cursor.execute("UPDATE sheet3 SET name = 'X2' WHERE id = 0")
    # w2y
    t2_cursor.execute(write_lock(1))
    t2_cursor.execute("UPDATE sheet3 SET name = 'Y2' WHERE id = 1")
    # c2
    t2.commit()
    # print the table state
    t1_cursor.execute("SELECT name FROM sheet3 WHERE id = 0 OR id = 1")
    print("-> S3 value:", t1_cursor.fetchall())
    t1.close()
    t2.close()

t1, t2 = init_t1_t2()
t1.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
t2.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
try:
    execute_schedule_1_with_locks()
except psycopg.errors.SerializationFailure as e:
    print("Transaction failed:", e)

t1, t2 = init_t1_t2()
t1.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
t2.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
try:
    execute_schedule_2_with_locks()
except psycopg.errors.SerializationFailure as e:
    print("Transaction failed:", e)

t1, t2 = init_t1_t2()
t1.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
t2.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
try:
    execute_schedule_3_with_locks()
except psycopg.errors.SerializationFailure as e:
    print("Transaction failed:", e)
