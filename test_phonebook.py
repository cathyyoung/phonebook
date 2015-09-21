import phonebook
import web
import unittest

# Override phonebook DB with our test DB
phonebook.db = web.database(dbn="sqlite", db="test_phonebook.db")
db = phonebook.db

class TestPhonebook(unittest.TestCase):
    
    def setUp(self):
        # Reset database per test
        db.query('DELETE FROM phonebook')

    
    def test_add_no_address(self):
        num_rows = db.query("SELECT COUNT(*) AS entries FROM phonebook")[0].entries
        
        response = phonebook.app.request("/",
                                         method='POST',
                                         data='{"surname":"Mouse",\
                                         "firstname":"Mickey",\
                                         "number":"01234567789"}')
        # Simple check; did we add one row
        new_num_rows = db.query("SELECT COUNT(*) AS entries FROM phonebook")[0].entries
        self.assertEqual(new_num_rows, num_rows+1)
        

if __name__ == '__main__':
    unittest.main()