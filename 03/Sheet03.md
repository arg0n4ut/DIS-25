## 3.1 Isolation Levels
### a)
Current isolation level: Read Committed

PostgreSQL supported isolation levels:\
(read uncommitted)\
read committed\
repeatable read\
serializable

### b)
| id | name |
| :--- | :--- |
| 1 | Albert |
| 2 | Beate |
| 3 | Chris |
| 4 | Dora |
| 5 | Emil |


### c)
```sql
SELECT relation::regclass, mode, granted
FROM pg_locks
where relation::regclass = 'sheet3'::regclass
```

Locks held:
| relation | mode | granted |
| :--- | :--- | :--- |
| sheet3 | AccessShareLock | true |


From PSQL documentation:
- AccessShareLock: The SELECT command acquires a lock of this mode on referenced tables. In general, any query that only reads a table and does not modify it will acquire this lock mode.

<!-- - RowExclusiveLock: Conflicts with the SHARE, SHARE ROW EXCLUSIVE, EXCLUSIVE, and ACCESS EXCLUSIVE lock modes.
The commands UPDATE, DELETE, INSERT, and MERGE acquire this lock mode on the target table (in addition to ACCESS SHARE locks on any other referenced tables). In general, this lock mode will be acquired by any command that modifies data in a table. -->

### d)
isolation level: Serializable

Locks held:
| relation | mode | granted |
| :--- | :--- | :--- |
| sheet3 | AccessShareLock | true |
| sheet3 | SIReadLock | true |

## 3.2 Lock Conflicts
### a)
connection 1 (manual commit, RC):
```sql
select name from sheet3 where id>3
```
| id | name |
| :--- | :--- |
| 4 | Dora |
| 5 | Emil |
| 6 | Frida |

connection 2 (automatic commit, RC):
```sql
INSERT INTO vsisp26.sheet3 (id, name)
VALUES (7, 'Gerald');
```
nothing happens

connection 1 (manual commit, RC):
```sql
select name from sheet3 where id>3
```
| id | name |
| :--- | :--- |
| 4 | Dora |
| 5 | Emil |
| 6 | Frida |
| 7 | Gerald |

### b)
| relation | mode | granted |
| :--- | :--- | :--- |
| sheet3 | AccessShareLock | true |

```sql
INSERT INTO vsisp26.sheet3 (id, name)
VALUES (8, 'Hanna');

```
nothing happens

connection 1 (manual commit, RC):
```sql
select name from sheet3 where id>3
```
| id | name |
| :--- | :--- |
| 4 | Dora |
| 5 | Emil |
| 6 | Frida |
| 7 | Gerald |

--> new value hasn't appeared

New connection sees:
| id | name |
| :--- | :--- |
| 1 | Albert |
| 2 | Beate |
| 3 | Chris |
| 4 | Dora |
| 5 | Emil |
| 6 | Frida |
| 7 | Gerald |
| 8 | Hanna |

If PSQL would use a lock-based scheduler like 2PL, the new connection would have to wait for the first connection to finish before it could see the new value.

### c)
Connection 1 (manual commit, RR):
```sql
UPDATE vsisp26.sheet3
SET name = 'Albert update'
WHERE id = 1
```
Connection 2 (automatic commit, RC):
```sql
UPDATE vsisp26.sheet3
SET name = 'Beate update'
WHERE id = 2
```
--> good

Connection 2 (automatic commit, RC):
```sql
UPDATE vsisp26.sheet3
SET name = 'Albert update 2'
WHERE id = 1
```
--> waiting... nothing happening

as soon as connection 1 commits, connection 2 auto-commits:
| id | name |
| :--- | :--- |
| 1 | Albert update 2 |
| 2 | Beate update |
| 3 | Chris |
| 4 | Dora |
| 5 | Emil |
| 6 | Frida |
| 7 | Gerald |
| 8 | Hanna |


Yes, the isolation level matters.\
If we set the 2nd connection to RR, after commiting the 1st connection we get the error:
```
[40001] ERROR: could not serialize access due to concurrent update
```
Only 1st connection changes persist:
| id | name |
| :--- | :--- |
| 1 | Albert update |
| 2 | Beate update |
| 3 | Chris |
| 4 | Dora |
| 5 | Emil |
| 6 | Frida |
| 7 | Gerald |
| 8 | Hanna |

### d)


connection 1,2 (manual commit, RC):

C1:
```sql
UPDATE vsisp26.sheet3
SET name = 'Albert update 1 '
WHERE id = 1
```
C2:
```sql
UPDATE vsisp26.sheet3
SET name = 'Beate update 2'
WHERE id = 2
```
C1:
```sql
UPDATE vsisp26.sheet3
SET name = 'Beate update 1'
WHERE id = 2
```
C2:
```sql
UPDATE vsisp26.sheet3
SET name = 'Albert update 2'
WHERE id = 1
```
```
[40P01] ERROR: deadlock detected Detail: Process 44145 waits for ShareLock on transaction 3497005; blocked by process 43912. Process 43912 waits for ShareLock on transaction 3497006; blocked by process 44145. Hint: See server log for query details. Where: while updating tuple (0,17) in relation "sheet3"
```

## 3.3 Sheduling
```
===== S1 =====
T1 reads: [('X2',)]
-> S1 value: [('X1',)]

===== S2 =====
T1 reads: [('X1',)]
-> S2 value: [('X2',)]

===== S3 =====
T2 reads: [('X2',)]
T2 reads: [('Y1',)]
-> S3 value: [('X2',), ('Y2',)]

b) Transactions set to serializable
===== S1 =====
T1 reads: [('X2',)]
Transaction failed: could not serialize access due to concurrent update

===== S2 =====
T1 reads: [('X2',)]
-> S2 value: [('X2',)]

===== S3 =====
T2 reads: [('X2',)]
T2 reads: [('Y2',)]
Transaction failed: could not serialize access due to concurrent update

c) RX Locking
===== S1 with manual row locking =====
T1 reads: [('X1',)]
Traceback (most recent call last):
  File "c:\Users\ikour\IASON\UNI\DIS\DIS-25\03\3.3.py", line 236, in <module>
    execute_schedule_1_with_locks()
  File "c:\Users\ikour\IASON\UNI\DIS\DIS-25\03\3.3.py", line 154, in execute_schedule_1_with_locks
    t2_cursor.execute(write_lock(0)) # Waits if lock is held
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===== S2 with manual row locking =====
T1 reads: [('X1',)]
Traceback (most recent call last):
  File "c:\Users\ikour\IASON\UNI\DIS\DIS-25\03\3.3.py", line 244, in <module>
    execute_schedule_2_with_locks()
  File "c:\Users\ikour\IASON\UNI\DIS\DIS-25\03\3.3.py", line 182, in execute_schedule_2_with_locks
    t2_cursor.execute(write_lock(0)) # Waits if lock is held
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===== S3 with manual row locking =====
T2 reads: [('X1',)]
Traceback (most recent call last):
  File "c:\Users\ikour\IASON\UNI\DIS\DIS-25\03\3.3.py", line 252, in <module>
    execute_schedule_3_with_locks()
  File "c:\Users\ikour\IASON\UNI\DIS\DIS-25\03\3.3.py", line 207, in execute_schedule_3_with_locks
    t1_cursor.execute(write_lock(0))
```