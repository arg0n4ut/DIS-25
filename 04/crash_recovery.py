""" 
a record in the DB is either
• up-to-date
• or stale (noforce)  redo
analysis phase
• read the entire log sequentially
• determine winner TAs
redo phase
• read the entire log sequentially
• selective redo (redo winners)
recovery progress is logged by updating the LSNs of the
completed redo steps in the corresponding pages

- redo is only required, if
page LSN < LSN of redo log record
- page LSN is updated on redo (grows monotonically)
if LSN(LS) > LSN(Page) then
redo (modification from LS);
LSN(Page) := LSN(LS);
end;


"""

import os

class Recovery:
    def __init__(self):
        self.winner_taid = set()

    def analyze_log(self):
        with open('04/log', 'r') as f:
            lines = f.readlines()
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) < 3:
                continue
            lsn = int(parts[0])
            taid = int(parts[1])
            if parts[2].strip() == 'EOT':
                self.winner_taid.add(taid)
        print(f"Winner TAs: {self.winner_taid}")

        
    def redo(self):
        with open('04/log', 'r') as f:
            lines = f.readlines()
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) < 4:
                continue
            lsn = int(parts[0])
            taid = int(parts[1])
            pageid = int(parts[2])
            data = parts[3]
            if taid in self.winner_taid:
                page_path = f'04/pages/{pageid}'
                if os.path.exists(page_path):
                    with open(page_path, 'r+') as page_file:
                        page_data = page_file.readline().strip()
                        page_parts = page_data.split(',', 2)
                        if len(page_parts) == 3:
                            page_lsn = int(page_parts[1])
                            if lsn > page_lsn:
                                # redo:
                                page_file.seek(0)
                                page_file.write(f"{pageid},{lsn},{data}\n")
                                print(f"Redone TA {taid} on page {pageid} with data: {data}\n")
                else:
                    # if page doesnt exist, create it:
                    with open(page_path, 'w') as page_file:
                        page_file.write(f"{pageid},{lsn},{data}\n")
                        print(f"Created page {pageid} with data: {data}")
                    print(f"Redone TA {taid} on new page {pageid} with data: {data}\n")
                    

    def recover(self):
        self.analyze_log()
        self.redo()

if __name__ == "__main__":
    recovery = Recovery()
    recovery.recover()