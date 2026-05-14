import logging, asyncio
from unittest import TestCase
from backend.domain.database.DrChordDatabase import DrChordDatabase

class TestDrChordDatabase(TestCase):
    def test(self):
        try:
            db = DrChordDatabase("../../../database.ini")
            db.create()
            conn = asyncio.run(db.get_connection())
            if conn is None or conn.is_closed(): self.fail()
            db.delete()
            logging.info("DrChordDatabase test success")
        except Exception as e: print(e)

logging.basicConfig(filename="target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')