import web, json, re

db = web.database(dbn="sqlite", db="phonebook.db")

urls = ("/", "Phonebook")
app = web.application(urls, globals())

class Phonebook:
    
    def GET(self):
        results = []
        q = db.query("SELECT firstname, surname, number, address FROM phonebook")
        for row in q:
            results.append({'firstname':row.firstname,
                            'surname':row.surname,
                            'number':row.number,
                            'address':row.address})
        json_response = json.dumps(results)
        return json_response

    def POST(self):
        required_attrs = ['firstname','surname','number']
        optional_attrs = ['address']
        all_attrs = required_attrs + optional_attrs

        try:
            data = json.loads(web.data())
        except ValueError: # Check for invalid json
            raise web.badrequest(response_strings['invalid_json'])

        # Make sure all required attributes are present
        for required_attr in required_attrs:
            if not data.has_key(required_attr):
                raise web.badrequest(response_strings['missing_field'])

        # Make sure there aren't any extra, unrecognised fields
        for key in data:
            if key not in all_attrs:
                raise web.badrequest(response_strings['unrecognized_field'])

        # Validate number
        if not self.is_valid_number(data['number']):
            raise web.badrequest(response_strings['invalid_number'])


        fn = data['firstname']
        sn = data['surname']                
        nm = data['number']
        # Check to see whether address is present, or None if not
        addr = data.has_key('address') and data['address'] or None
        
        n = db.insert('phonebook',
                      firstname=fn,
                      surname=sn,
                      number=nm,
                      address=addr)
        # Return 201 Created
        return web.created(response_strings['add_success'] % (fn, sn))


    def is_valid_number(self, data):
        # Vague regex for phone number, inc spaces, dashes, extension hash
        p = "[0-9- #]{6,15}"
        if not re.search(p, data):
            return False
        return True





response_strings = {
    'invalid_json':"Invalid JSON data",
    'unrecognized_field':"Unrecognized field in POST data. \
        Request data must include firstname, surname, number, and optionally address.",
    'missing_field':"Attributes firstname, surname, and number must be present",
    'add_success':"Successfully added %s %s",
    'invalid_number':"Phone number must be 6-15 digits long, and contain only numbers, -, # or spaces."
    }

if __name__ == "__main__":
    app.run()