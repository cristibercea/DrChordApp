import logging
from unittest import IsolatedAsyncioTestCase
from backend.domain.database.DrChordDatabase import DrChordDatabase

logging.basicConfig(filename="domain/database/testing/target/backend.log",
                    level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    filemode='w')

class TestDrChordDatabase(IsolatedAsyncioTestCase):
    def setUp(self):
        # System Under Test
        self.db = DrChordDatabase("app.ini")

    async def asyncTearDown(self):
        try:
            conn = await self.db.get_connection()
            if conn and not conn.is_closed(): await conn.close()
            # self.db.delete()  # erases database!!!!!
        except Exception as e:
            logging.error(f"Error closing connection in teardown: {e}")

    async def test_drchord_database(self):
        try:
            # Arrange
            self.db.create()

            # Act
            conn = await self.db.get_connection()

            # Assert
            if conn is None or conn.is_closed(): self.fail("Connection is None or closed")
            self.assertTrue(True)
            logging.info("DrChordDatabase test success")
        except Exception as e:
            logging.error(e)
            self.fail(f"Test failed: {e}")
