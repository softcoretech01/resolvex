import sys
sys.path.append('.')
from db import execute_query

rows = execute_query("SELECT ticket_code, attachment FROM ticket_master WHERE attachment IS NOT NULL AND attachment != ''", fetch=True)
for r in rows:
    print(r)
