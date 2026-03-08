import logging

from backend.domain.database.DrChordDatabase import DrChordDatabase

def run():
    try:
        db = DrChordDatabase("../../../database.ini")
        db.create()
        print("all ok") if db.get_connection() is not None else print("connection failed")
        db.delete()
    except Exception as e: print(e)

logging.basicConfig(filename="target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')
run()