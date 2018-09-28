#!/usr/bin/env python3

import re
import sqlite3 as sqlite
from code import interact


db_name = "ctrack.db"
db = sqlite.connect(db_name)
cursor = db.cursor()
cursor.execute("SELECT DISTINCT developer FROM changesets")
#res = cursor.fetchall()
#users = [r[0] for r in res]

for u in cursor.fetchall():
    cursor.execute("INSERT INTO developers(release_name) VALUES (?)", u)

db.commit()

#interact(local=locals())
