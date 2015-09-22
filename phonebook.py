import web
import json

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
        try:
            data = json.loads(web.data())
        except ValueError:
            # Check for invalid json
            raise web.badrequest(response_strings['invalid_json'])

        # Make sure all required attributes are present
        for required_attr in ('firstname','surname','number'):
            if not data.has_key(required_attr):
                raise web.badrequest(response_strings['missing_field'])

        # Make sure there aren't any extra, unrecognised fields
        for key in data:
            if key not in ('firstname','surname','number','address'):
                raise web.badrequest(response_strings['unrecognized_field'])
        
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



response_strings = {
    'invalid_json':"Invalid JSON data",
    'unrecognized_field':"Unrecognized field in POST data. \
        Request data must include firstname, surname, number, and optionally address.",
    'missing_field':"Attributes firstname, surname, and number must be present",
    'add_success':"Successfully added %s %s"
    }

if __name__ == "__main__":
    app.run()