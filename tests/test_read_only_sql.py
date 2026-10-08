"""Basic SQL safety tests. Run: python -m unittest discover -s tests"""
import sqlite3
import tempfile
import unittest
from pathlib import Path

class SQLSafetyTest(unittest.TestCase):
    def setUp(self):
        # Isolate the product loader dependencies for this smoke test.
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "data.db"
        with sqlite3.connect(self.db) as conn:
            conn.execute("CREATE TABLE products (product_name TEXT)")
            conn.execute("INSERT INTO products VALUES ('shirt')")

    def tearDown(self):
        self.temp.cleanup()

    def test_sql_readonly_guards_are_present(self):
        source = (Path(__file__).resolve().parents[1] / "shoppinggpt/tool/product_search.py").read_text()
        self.assertIn('mode=ro', source)
        self.assertIn('query_only=ON', source)
        self.assertIn('Only SELECT queries are allowed', source)

    def test_sqlite_readonly_configuration(self):
        conn = sqlite3.connect(f"file:{self.db}?mode=ro", uri=True)
        conn.execute("PRAGMA query_only=ON")
        self.assertEqual(conn.execute("SELECT count(*) FROM products").fetchone()[0], 1)
        with self.assertRaises(sqlite3.OperationalError):
            conn.execute("DELETE FROM products")
        conn.close()

if __name__ == '__main__':
    unittest.main()
