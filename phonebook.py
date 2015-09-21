import web
import json

db = web.database(dbn="sqlite", db="phonebook.db")

urls = ("/", "Phonebook")
app = web.application(urls, globals())

class Phonebook:
    
    def GET(self):
        return "This will list all entries"

    def POST(self):
        data = json.loads(web.data())
        
        fn = data['firstname']
        sn = data['surname']
        nm = data['number']
        if data.has_key('address'):
            addr = data['address']
        n = db.insert('phonebook',
                      firstname=fn,
                      surname=sn,
                      number=nm)
        return "Successfully added %s %s" % (fn, sn)
    

if __name__ == "__main__":
    app.run()