"""
client calss that can be started in several instances in parallel, accessing the singleton persistence manager.
The clients repeatedly execute transactions on the persistence manager according to the following scheme:
beginTransaction() write() write() ... commit()
For more realistic behavior, every operation is followed by a brief pause. The number of writes in a transaction
may vary.
In order to get along without locks, the clients do not access the same pages, i.e. Client 1 accesses pages
10..19, Client 2 accesses pages 20..29 and so forth. More than one page may be modified by one transaction.
The user data may consist of simple strings.

"""

import time
import random
from persistence_manager import PManager
from threading import Thread

class Client:
    def __init__(self, client_id):
        self.client_id = client_id
        self.pmanager = PManager()

    def run(self):
        taid = self.pmanager.begin_transaction()
        print(f"Client {self.client_id} started transaction {taid}")
        num_writes = random.randint(1, 10)  # Number of writes can be randomized or fixed
        for i in range(num_writes):
            pageid = random.randint(10, 19) + (self.client_id * 10)  # Ensure unique page IDs for each client
            data = f"data_from_client_{self.client_id+1}_write_{i+1}"
            self.pmanager.write(taid, pageid, data)
            print(f"Client {self.client_id} wrote to page {pageid}: {data}")
            time.sleep(random.uniform(0.1, 0.5))  # Simulate brief pause after each write
        if self.pmanager.commit(taid):
            print(f"Client {self.client_id} committed transaction {taid}")
        else:
            print(f"Client {self.client_id} failed to commit transaction {taid}")

def start_clients(num_clients):
    threads = []
    for i in range(num_clients):
        client = Client(i)
        thread = Thread(target=client.run)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    pm = PManager()
    pm.reset()  # Reset the persistence manager before starting clients
    num_clients = 5
    start_clients(num_clients)

