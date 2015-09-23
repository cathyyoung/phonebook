import web, json, re

db = web.database(dbn="sqlite", db="phonebook.db")

urls = ("/", "Phonebook",
        "/([0-9]+)", "Entry")
app = web.application(urls, globals())
   
class Phonebook:
    
    def GET(self):
        '''Returns all entries in phonebook'''
        
        results = []
        q = db.query("SELECT id, firstname, surname, number, address FROM phonebook")
        for row in q:
            results.append({'id':row.id,
                            'firstname':row.firstname,
                            'surname':row.surname,
                            'number':row.number,
                            'address':row.address})
        json_response = json.dumps(results)
        return json_response


    def POST(self):
        '''Add entry to phonebook with firstname, surname, number, and optional address'''
        
        required_attrs = ['firstname','surname','number']
        optional_attrs = ['address']
        all_attrs = required_attrs + optional_attrs

        data = load_json(web.data())

        # Checks all required attributes are present
        # Checks there are no unrecognized fields
        # Validates input
        # Raises 400 Bad request if not valid
        validate_fields(data, required_attrs, all_attrs)

        fn = data['firstname']
        sn = data['surname']                
        nm = data['number']
        # Check to see whether address is present, or None if not
        addr = 'address' in data.keys() and data['address'] or None       
        
        row_id = db.insert('phonebook',
                      seqname='id',
                      firstname=fn,
                      surname=sn,
                      number=nm,
                      address=addr)
        
        # Return 201 Created
        return web.created(headers={'Location':'/%d'%row_id})

class Entry:
    def PUT(self, id):
        '''Update an existing entry in the phonebook. URI must match /<id>
        of an existing entry'''

        if not entry_exists(id):
            raise web.notfound("No matching phonebook entry with id %s" % id)
        
        required_attrs = []
        optional_attrs = ['firstname','surname','number','address']
        all_attrs = required_attrs + optional_attrs

        data = load_json(web.data())

        if not data:
            # 400 Bad request for empty data
            raise web.badrequest(response_strings['update_fields'])

        # Checks all required attributes are present
        # Checks there are no unrecognized fields
        # Validates input
        # Raises 400 Bad request if not valid
        validate_fields(data, required_attrs, all_attrs)

        # feed in data dict
        res = db.update('phonebook', where="id=$id",
                        vars={'id':id},
                        **data)
        return web.nocontent()

    def DELETE(self, id):
        '''Remove an existing entry in the phonebook. URI must match /<id>
        of an existing entry'''

        if not entry_exists(id):
            raise web.notfound("No matching phonebook entry with id %s" % id)

        db.delete('phonebook', where="id=$id",
                  vars={'id':id})
        return web.nocontent()


## Utility methods ##
#####################

def make_json_response(**kwargs):
    json_response = json.dumps(kwargs)
    return json_response

def entry_exists(entry_id):
    result = db.where('phonebook',id=entry_id)
    if len(list(result)) > 0:
        return True
    return False

def validate_fields(data, required_attrs, all_attrs):
    # Make sure all required attributes are present
    for required_attr in required_attrs:
        if not required_attr in data.keys():
            raise web.badrequest(response_strings['missing_field'])

    # Make sure there aren't any extra, unrecognised fields
    for key in data:
        if key not in all_attrs:
            raise web.badrequest(response_strings['unrecognized_field'])
        # Validate input
        try:
            validate_data(data[key], key, all_attrs)
        except ValueError, e:
            raise web.badrequest(e)

def validate_data(data, field, all_attrs):
    def validate_number(data):
        # Vague regex for phone number, inc spaces, dashes, extension hash
        p = "[0-9- #]{6,15}"
        if not re.search(p, data):
            raise ValueError(response_strings['invalid_number'])

    def validate_string(data):
        # Just check it's not blank!
        # Only for firstname, lastname, as address can be blank.
        if not data:
            raise ValueError(response_strings['empty_string'])
    
    if field not in all_attrs:
        raise ValueError(response_strings['unrecognized_field'])
    if field == 'number':
        validate_number(data)
    elif field == 'firstname' or field == 'lastname':
        validate_string(data)

def load_json(input):
    try:
        data = json.loads(input)
        return data
    except ValueError:
        raise web.badrequest(response_strings['invalid_json'])


response_strings = {
    'invalid_json':"Invalid JSON data",
    'unrecognized_field':"Unrecognized field in POST data. \
        Request data must include firstname, surname, number, and optionally address.",
    'missing_field':"Required attributes must be present",
    'add_success':"Successfully added %s %s",
    'invalid_number':"Phone number must be 6-15 digits long, and contain only numbers, -, # or spaces.",
    'empty_string':"Field must not be null or an empty string.",
    'entry_exists':"Could not create new entry for %s %s as one already exists.",
    'update_fields':"Update PUT request must contain at least one field."
    }

if __name__ == "__main__":
    app.run()