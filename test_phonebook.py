import phonebook
import web, unittest, json

# Override phonebook DB with our test DB
phonebook.db = web.database(dbn="sqlite", db="test_phonebook.db")
db = phonebook.db

class TestPhonebook(unittest.TestCase):
    
    def tearDown(self):
        '''Clear data from the db at end of each test'''
        db.query('DELETE FROM phonebook')

#############################
##      Create (POST)      ##
#############################
    
    def test_create(self):
        '''Test that a POST request with phonebook data results in the entry being added to the phonebook'''
        
        td1 = '{"surname":"Mouse",\
                 "firstname":"Mickey",\
                 "number":"01234567789"}'
        
        response = phonebook.app.request("/", method='POST', data=td1)
        # Simple check; did we add one row
        num_rows = db.query("SELECT COUNT(*) AS entries FROM phonebook")[0].entries
        self.assertEqual(num_rows, 1)

        # check a URI for the new entity was returned
        # This method fails the test if no Location header is found in the response 
        self.assertRegexpMatches(self.get_loc(response), '/\d+')

        td2 = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"02045679920",\
                 "address":"12 New Road, Disneyland"}'
        
        response = phonebook.app.request("/", method='POST', data=td2)
        # Check HTTP response
        self.assertEqual(response.status, "201 Created")

        new_num_rows = db.query("SELECT COUNT(*) AS entries FROM phonebook")[0].entries

        mickey = db.where('phonebook',surname='Mouse',firstname='Mickey')
        mickey = mickey[0]
        self.assertEqual(mickey.firstname, "Mickey")
        self.assertEqual(mickey.surname, "Mouse")
        self.assertEqual(mickey.number, "01234567789")
        self.assertEqual(mickey.address, None)

        minnie = db.where('phonebook',surname='Mouse',firstname='Minnie')
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

        # No database rows added
        num_rows = db.query("SELECT COUNT(*) AS entries FROM phonebook")[0].entries
        self.assertEqual(num_rows, 0)

        no_addr_data = '{"surname":"Mouse",\
                 "firstname":"Mickey",\
                 "number":"01234567789"}'
        
        response = phonebook.app.request("/", method='POST', data=no_addr_data)
        self.assertEqual(response.status, "201 Created")        
        
        # Check 1 row added
        num_rows = db.query("SELECT COUNT(*) AS entries FROM phonebook")[0].entries
        self.assertEqual(num_rows, 1)

        empty_addr_data = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"01234567789",\
                 "address":""}'
        response = phonebook.app.request("/", method='POST', data=empty_addr_data)
        self.assertEqual(response.status, "201 Created")
        
        # Check 1 row added
        new_num_rows = db.query("SELECT COUNT(*) AS entries FROM phonebook")[0].entries
        self.assertEqual(new_num_rows, num_rows+1)

    def test_create_bad_data(self):
        '''Test attempt to create with invalid POST data'''

        # unrecognised field
        post_data = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"02045679920",\
                 "address":"12 New Road, Disneyland",\
                 "invalid_field": "Will not be recognized"}'
        response = phonebook.app.request("/", method='POST', data=post_data)
        self.assertEqual(response.status, "400 Bad Request")
        self.assertEqual(response.data, phonebook.response_strings['unrecognized_field'])

    def test_create_malformed_data(self):
        '''Test malformed POST data, e.g. non-numeric phone number'''
        
        post_data = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"NaN",\
                 "address":"12 New Road, Disneyland"}'
        response = phonebook.app.request("/", method='POST', data=post_data)
        self.assertEqual(response.status, "400 Bad Request")
        self.assertEqual(response.data, phonebook.response_strings['invalid_number'])


    def test_create_invalid_json(self):
        '''Test that 400 Bad request is returned without valid json in the POST request'''
        response = phonebook.app.request("/", method='POST', data=None)
        self.assertEqual(response.status, "400 Bad Request")
        self.assertEqual(response.data, phonebook.response_strings['invalid_json'])

        response = phonebook.app.request("/", method='POST', data="It's expecting JSON really")
        self.assertEqual(response.status, "400 Bad Request")
        self.assertEqual(response.data, phonebook.response_strings['invalid_json'])


#############################
##      List (GET)         ##
#############################
        

    def test_list_all_empty(self):
        '''Test the response for an empty phonebook'''
        
        response = phonebook.app.request("/", method='GET')
        
        # Fails if invalid json is returned
        json_resp = self.json_data(response.data)
        # Return empty json object
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

#############################
##      Update (PUT)       ##
#############################
        
    def test_update(self):
        '''Add a full entry to the phonebook, then update it with new number and address'''
        
        original = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"02045679920",\
                 "address":"12 New Road, Disneyland"}'
        # Add original entry
        response = phonebook.app.request("/", method='POST', data=original)

        # The 201 Created response returns the URI of the entry resource
        update_uri = self.get_loc(response)

        update = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"11111034",\
                 "address":"13 Other Road, Disneyland"}'
        # Make update request with new number and address
        response = phonebook.app.request(update_uri, method='PUT', data=update)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.data, phonebook.response_strings['update_success'])

        minnie = db.where('phonebook',surname='Mouse',firstname='Minnie')
        minnie = list(minnie)
        # Still only one matching row
        self.assertEqual(len(minnie), 1)
        
        minnie = minnie[0]
        # With new number and address
        self.assertEqual(minnie.number, "11111034")
        self.assertEqual(minnie.address, "13 Other Road, Disneyland")

    def test_update_no_resource_found(self):
        '''Test attempt to update a non-existent resource'''

        update = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "address":"13 Other Road, Disneyland"}'
        # Make update request to add address
        response = phonebook.app.request("/10", method='PUT', data=update)
        self.assertEqual(response.status, "404 Not Found")


    def test_update_add_address(self):
        '''Test create an entry without an address, then add the address via update'''
        
        original = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"02045679920"}'
        # Add original entry
        response = phonebook.app.request("/", method='POST', data=original)

        update_uri = self.get_loc(response)

        update = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "address":"13 Other Road, Disneyland"}'
        # Make update request to add address
        response = phonebook.app.request(update_uri, method='PUT', data=update)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.data, phonebook.response_strings['update_success'])

        minnie = db.where('phonebook',surname='Mouse',firstname='Minnie')
        minnie = minnie[0]
        # With new address
        self.assertEqual(minnie.address, "13 Other Road, Disneyland")


    def test_update_remove_address(self):
        '''Test create an entry with an address, then remove the address via update'''
        
        original = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"02045679920",\
                 "address":"13 Other Road, Disneyland"}'
        # Add original entry
        response = phonebook.app.request("/", method='POST', data=original)
        update_uri = self.get_loc(response)

        update = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "address":""}'
        # Make update request to remove address
        response = phonebook.app.request(update_uri, method='PUT', data=update)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.data, phonebook.response_strings['update_success'])
        

        minnie = db.where('phonebook',surname='Mouse',firstname='Minnie')
        minnie = list(minnie)
        # Still one result
        self.assertEqual(len(minnie), 1)
        minnie = minnie[0]
        
        # Having removed the address
        self.assertEqual(minnie.address, '')


    def test_update_no_blank_number(self):
        '''Test that you cannot pass an empty string number to remove it from the entry'''
        
        original = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"02045679920",\
                 "address":"13 Other Road, Disneyland"}'
        # Add original entry
        response = phonebook.app.request("/", method='POST', data=original)
        update_uri = self.get_loc(response)

        update = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":""}'
        # Make update request to remove number
        response = phonebook.app.request(update_uri, method='PUT', data=update)
        self.assertEqual(response.status, "400 Bad Request")
        self.assertEqual(response.data, phonebook.response_strings['invalid_number'])

        minnie = db.where('phonebook',surname='Mouse',firstname='Minnie')
        minnie = list(minnie)[0]
        # Hasn't updated the number to remove it
        self.assertEqual(minnie.number, "02045679920")


    def test_update_firstname(self):
        '''Test to update firstname'''
        
        original = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"02045679920",\
                 "address":"12 New Road, Disneyland"}'
        # Add original entry
        response = phonebook.app.request("/", method='POST', data=original)
        update_uri = self.get_loc(response)

        update = '{"firstname":"Minerva"}'
        # Make update request with new number and address
        response = phonebook.app.request(update_uri, method='PUT', data=update)

        minerva = db.where('phonebook',id=update_uri[1:])
        minerva = minerva[0]
        # With new firstname
        self.assertEqual(minerva.firstname, "Minerva")
        


    def test_update_no_surname(self):
        '''Test to show that surname (and firstname) is required for update'''
        
        original = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"02045679920",\
                 "address":"12 New Road, Disneyland"}'
        # Add original entry
        response = phonebook.app.request("/", method='POST', data=original)
        update_uri = self.get_loc(response)

        update = '{"surname":"Duck"}'
        # Make update request with new number and address
        response = phonebook.app.request(update_uri, method='PUT', data=update)

        minnie = db.where('phonebook',id=update_uri[1:])
        minnie = minnie[0]
        # With new surname
        self.assertEqual(minnie.surname, "Duck")


    def test_update_one_field_required(self):
        '''Test that at least one field is present in update'''

        original = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"02045679920",\
                 "address":"12 New Road, Disneyland"}'
        # Add original entry
        response = phonebook.app.request("/", method='POST', data=original)
        update_uri = self.get_loc(response)

        update = '{}'
        # Make update request with new number and address
        response = phonebook.app.request(update_uri, method='PUT', data=update)
        self.assertEqual(response.status, "400 Bad Request")
        self.assertEqual(response.data, phonebook.response_strings['update_fields'])


    def test_update_invalid_json(self):
        '''Test that 400 Bad request is returned without valid json in the PUT request'''

        original = '{"surname":"Mouse",\
                 "firstname":"Minnie",\
                 "number":"02045679920",\
                 "address":"12 New Road, Disneyland"}'
        # Add original entry
        response = phonebook.app.request("/", method='POST', data=original)
        update_uri = self.get_loc(response)
        
        response = phonebook.app.request(update_uri, method='PUT', data=None)
        self.assertEqual(response.status, "400 Bad Request")
        self.assertEqual(response.data, phonebook.response_strings['invalid_json'])

        response = phonebook.app.request(update_uri, method='PUT', data="It's expecting JSON really")
        self.assertEqual(response.status, "400 Bad Request")
        self.assertEqual(response.data, phonebook.response_strings['invalid_json'])
        

## Utility methods ##
#####################

    def json_data(self, response_data):
        try:
            json_resp = json.loads(response_data)
            return json_resp
        except ValueError:
            # not valid json
            self.fail("Received invalid JSON response")

    def get_loc(self, response):
        if not 'Location' in response.headers.keys():
            self.fail('No Location header found in response headers')
        return response.headers['Location']
       
        

if __name__ == '__main__':
    unittest.main()