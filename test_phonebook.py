import phonebook
import web, unittest, json

# Override phonebook DB with our test DB
phonebook.db = web.database(dbn="sqlite", db="test_phonebook.db")
db = phonebook.db

class TestPhonebook(unittest.TestCase):
    
    def setUp(self):
        # Reset database per test
        db.query('DELETE FROM phonebook')

    
    def test_create(self):
        '''Test that a POST request with phonebook data results in the entry being added to the phonebook'''
        
        td1 = '{"surname":"Mouse",\
                 "firstname":"Mickey",\
                 "number":"01234567789"}'
        
        response = phonebook.app.request("/", method='POST', data=td1)
        # Simple check; did we add one row
        num_rows = db.query("SELECT COUNT(*) AS entries FROM phonebook")[0].entries
        self.assertEqual(num_rows, 1)

        td2 = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"02045679920",\
                 "address":"12 New Road, Disneyland"}'
        
        response = phonebook.app.request("/", method='POST', data=td2)
        # Check HTTP response
        self.assertEqual(response.status, "201 Created")

        new_num_rows = db.query("SELECT COUNT(*) AS entries FROM phonebook")[0].entries

        # assert 2 mice, one mickey, one minnie, one address,
        mickey = db.query('''SELECT firstname, surname, number, address FROM phonebook
                            WHERE surname = "Mouse" AND firstname = "Mickey"''')
        mickey = mickey[0]
        self.assertEqual(mickey.firstname, "Mickey")
        self.assertEqual(mickey.surname, "Mouse")
        self.assertEqual(mickey.number, "01234567789")
        self.assertEqual(mickey.address, None)

        minnie = db.query('''SELECT firstname, surname, number, address FROM phonebook
                            WHERE surname = "Mouse" AND firstname = "Minnie"''')
        minnie = minnie[0]
        self.assertEqual(minnie.firstname, "Minnie")
        self.assertEqual(minnie.surname, "Mouse")
        self.assertEqual(minnie.number, "02045679920")
        self.assertEqual(minnie.address, "12 New Road, Disneyland")

    def test_create_missing_fields(self):
        '''Test that errors are thrown and appropriate HTTP status code
        is returned when a required attribute is missing in POST (create) request.
        Test that a missing address attribute (optional) is accepted and entry is created.'''
        
        no_name_data = '{"firstname":"Minnie",\
                 "number":"02045679920",\
                 "address":"12 New Road, Disneyland"}'
        
        response = phonebook.app.request("/", method='POST', data=no_name_data)

        # Check appropriate response status
        self.assertEqual(response.status, "400 Bad Request")

        # Check nothing's been added to the database
        num_rows = db.query("SELECT COUNT(*) AS entries FROM phonebook")[0].entries
        self.assertEqual(num_rows, 0)

        no_num_data = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "address":"12 New Road, Disneyland"}'

        response = phonebook.app.request("/", method='POST', data=no_num_data)
        self.assertEqual(response.status, "400 Bad Request")
        num_rows = db.query("SELECT COUNT(*) AS entries FROM phonebook")[0].entries
        self.assertEqual(num_rows, 0)

        no_addr_data = '{"surname":"Mouse",\
                 "firstname":"Mickey",\
                 "number":"01234567789"}'
        
        response = phonebook.app.request("/", method='POST', data=no_addr_data)
        # Check 1 row added
        num_rows = db.query("SELECT COUNT(*) AS entries FROM phonebook")[0].entries
        self.assertEqual(num_rows, 1)

    def test_list_all_empty(self):
        '''Test the response for an empty phonebook'''
        
        response = phonebook.app.request("/", method='GET')
        
        # Fails if invalid json
        json_resp = self.json_data(response.data)

        self.assertEqual(len(json_resp), 0)

    def test_list_all(self):
        '''Test that all entries are returned'''
        
        data = ['{"surname":"Mouse","firstname":"Mickey","number":"01234567789"}',
                '{"surname":"Mouse","firstname":"Minnie","number":"02045679920","address":"12 New Road, Disneyland"}',
                '{"surname":"Duck","firstname":"Donald","number":"028384752","address":"123a Main Street, Disneyland"}',
                '{"surname":"Duck","firstname":"Daisy","number":"028384752","address":"123a Main Street, Disneyland"}']

        # add data to phonebook
        for entry in data:
            response = phonebook.app.request("/", method='POST', data=entry)

        # Check they've been added to database
        entries = db.query("SELECT * FROM phonebook")
        self.assertEqual(len(list(entries)), 4)

        # Test response
        response = phonebook.app.request("/", method='GET')
        self.assertEqual(response.status, "200 OK")

        # Fails if invalid json
        json_resp = self.json_data(response.data)

        self.assertEqual(len(json_resp), 4)
        

## Utility methods ##
#####################

    def json_data(self, response_data):
        try:
            json_resp = json.loads(response_data)
            return json_resp
        except ValueError:
            # not valid json
            self.fail("Received invalid JSON response")
       
        

if __name__ == '__main__':
    unittest.main()