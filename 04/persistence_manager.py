""" 
- persisting pages
• in files, not in DB2
• advice: one file per page
page structure: [PageID, LSN, Data]
• PageID: Page identifier
• LSN: Log Sequence Number
• Data: user data
buffer: delayed writes
• persisting data of commited transactions, when there are more than five
pages in the buffer (No-Force)
• check for a „full“ buffer after every write access
• refreshing pages in the buffer is possible
• no dirty pages are persisted (No-Steal)
• user data are overwritten directly (Non-Atomic)
modifying operations are logged immediately
requirement: support of crash recovery

buffer can be implemented with a hash table
correspondence between
transactions and datasets has to be ad
no checkpointing is required
allow concurrent requests from clients to user data
perform deferred writes for modified data

ONLY 1 persistence manager is allowed -> Singleton pattern

Logging:
physical state logging
granulate: Page
new states (after-images) of modified objects are written
to the log file
record types
• BOT and commit record
• modification records (after-images)
structure of log entries: [LSN, TAID, PageID, Redo]
• LSN: Log Sequence Number (monotonically ascending)
• TAID: transaction ID
• PageID: Page ID
• Redo: information required for redo
 """

""" 
• beginTransaction(): starts a new transaction. The persistence manager creates a unique transaction
ID and returns it to the client.
• commit(int taid): commits the transaction specified by the given transaction ID.
• write(int taid, int pageid, String data): writes the given data with the given page ID on behalf
of the given transaction to the buffer. If the given page already exists, its content is replaced completely
by the given data.

log file: log
pages: pages/10-59 for up to 5 transactions

 """
from threading import Lock
import os

class PManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(PManager, cls).__new__(cls)
                    cls._instance.init()
        return cls._instance

    def init(self):
        self.buffer = {}
        self.log_file = '04/log'
        self.page_dir = '04/pages'
        os.makedirs(self.page_dir, exist_ok=True)
        self.transaction_id_counter = 0
        self.lsn_counter = 0
        self.transactions = {}  # Maps transaction ID to its state

    def begin_transaction(self):
        self.transaction_id_counter += 1
        taid = self.transaction_id_counter
        self.transactions[taid] = 'active'
        return taid

    def commit(self, taid):
        if taid in self.transactions and self.transactions[taid] == 'active':
            self.lsn_counter += 1
            self.transactions[taid] = 'committed'
            self._flush_buffer()
            self._log_commit(taid, self.lsn_counter)
            return True
        return False
    
    def write(self, taid, pageid, data):
        if taid not in self.transactions or self.transactions[taid] != 'active':
            raise Exception("Transaction not active")
        self.lsn_counter += 1
        self.buffer[pageid] = (self.lsn_counter, data)
        # Track which transaction wrote this page
        if not hasattr(self, 'page_to_taid'):
            self.page_to_taid = {}
        self.page_to_taid[pageid] = taid
        self._log_write(taid, pageid, data, self.lsn_counter)
        if len(self.buffer) > 5:
            self._flush_buffer()
    
    def _flush_buffer(self):
        to_remove = []
        for pageid, (lsn, data) in list(self.buffer.items()):
            # Find the transaction that last wrote this page
            # You may need to track which transaction wrote each page in the buffer!
            # For now, let's assume you add a mapping: self.page_to_taid[pageid] = taid in write()
            taid = self.page_to_taid.get(pageid)
            if taid and self.transactions.get(taid) == 'committed':
                page_path = os.path.join(self.page_dir, str(pageid))
                file_content = f"{pageid},{lsn},{data}"
                with open(page_path, 'w') as f:
                    f.write(file_content)
                to_remove.append(pageid)
        # Remove only flushed pages from buffer
        for pageid in to_remove:
            self.buffer.pop(pageid, None)
            self.page_to_taid.pop(pageid, None)

    
    def _log_commit(self, taid, lsn):
        with open(self.log_file, 'a') as f:
            f.write(f"{lsn}, {taid}, EOT\n")
    
    def _log_write(self, taid, pageid, data, lsn):
        with open(self.log_file, 'a') as f:
            # Log entry: [LSN, TAID, PageID, Redo] where Redo is the new data
            f.write(f"{lsn}, {taid}, {pageid}, {data}\n")
        
    def get_page(self, pageid):
        page_path = os.path.join(self.page_dir, str(pageid))
        if os.path.exists(page_path):
            with open(page_path, 'r') as f:
                line = f.readline().strip()
                # Assuming format "PageID,LSN,Data"
                parts = line.split(',', 2) 
                if len(parts) == 3:
                    # pid_from_file, lsn_from_file, data_content = parts
                    # Add validation if needed, e.g., assert str(pageid) == pid_from_file
                    return parts[2] # Return data
        return None
    
    def get_transaction_state(self, taid):
        return self.transactions.get(taid, 'unknown')
    
    def get_buffer(self):
        return self.buffer.copy()
    
    def get_log(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                return f.readlines()
        return []
    
    def clear_log(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
    
    def clear_pages(self):
        for filename in os.listdir(self.page_dir):
            file_path = os.path.join(self.page_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    def clear_buffer(self):
        self.buffer.clear()
    
    def clear_transactions(self):
        self.transactions.clear()
        self.transaction_id_counter = 0
        self.lsn_counter = 0
    
    def reset(self):
        self.clear_log()
        self.clear_pages()
        self.clear_buffer()
        self.clear_transactions()
        self.init()
    