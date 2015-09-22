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

        data = self.load_json(web.data())

        # Make sure all required attributes are present
        for required_attr in required_attrs:
            if not data.has_key(required_attr):
                raise web.badrequest(response_strings['missing_field'])

        # Make sure there aren't any extra, unrecognised fields
        for key in data:
            if key not in all_attrs:
                raise web.badrequest(response_strings['unrecognized_field'])
            # Validate input
            try:
                self.validate_data(data[key], key, all_attrs)
            except ValueError, e:
                raise web.badrequest(e)


        fn = data['firstname']
        sn = data['surname']                
        nm = data['number']
        # Check to see whether address is present, or None if not
        addr = data.has_key('address') and data['address'] or None

        # Check whether firstname+lastname already exists for uniqueness assumption
        if self.already_exists(fn, sn):
            raise web.conflict(response_strings['entry_exists'] % (fn, sn))
        
        
        n = db.insert('phonebook',
                      firstname=fn,
                      surname=sn,
                      number=nm,
                      address=addr)
        # Return 201 Created
        return web.created(response_strings['add_success'] % (fn, sn))


    def already_exists(self, firstname, surname):
        result = db.query('''SELECT * FROM phonebook
                 WHERE firstname=$firstname
                 AND surname=$surname''',
                  vars={'firstname':firstname, 'surname':surname})
        if len(list(result)) > 0:
            return True
        return False


    def validate_data(self, data, field, all_attrs):
        def validate_number(data):
            # Vague regex for phone number, inc spaces, dashes, extension hash
            p = "[0-9- #]{6,15}"
            if not re.search(p, data):
                raise ValueError(response_strings['invalid_number'])

        def validate_string(data):
            # Just check it's not blank!
            if not data:
                raise ValueError(response_strings['empty_string'])
        
        if field not in all_attrs:
            raise ValueError(response_strings['unrecognized_field'])
        if field == 'number':
            validate_number(data)
        else:
            validate_string(data)


    def load_json(self, input):
        try:
            data = json.loads(input)
            return data
        except ValueError:
            raise web.badrequest(response_strings['invalid_json'])



response_strings = {
    'invalid_json':"Invalid JSON data",
    'unrecognized_field':"Unrecognized field in POST data. \
        Request data must include firstname, surname, number, and optionally address.",
    'missing_field':"Attributes firstname, surname, and number must be present",
    'add_success':"Successfully added %s %s",
    'invalid_number':"Phone number must be 6-15 digits long, and contain only numbers, -, # or spaces.",
    'empty_string':"Field must not be null or an empty string.",
    'entry_exists':"Could not create new entry for %s %s as one already exists."
    }

if __name__ == "__main__":
    app.run()