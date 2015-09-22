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
        data = json.loads(web.data())

        # Make sure all required attributes are present
        for required_attr in ('firstname','surname','number'):
            if not data.has_key(required_attr):
                raise web.badrequest("Attributes firstname, surname, and number must be present")
        
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
        return web.created("Successfully added %s %s" % (fn, sn))


if __name__ == "__main__":
    app.run()