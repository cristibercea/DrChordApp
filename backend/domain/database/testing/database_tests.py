import logging
import asyncio
from backend.domain.database.DrChordDatabase import DrChordDatabase

def run():
    try:
        db = DrChordDatabase("../../../database.ini")
        db.create()
        conn = asyncio.run(db.get_connection())
        print("all ok") if conn is not None and not conn.is_closed() else print("connection failed")
        db.delete()
    except Exception as e: print(e)

logging.basicConfig(filename="target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')
run()