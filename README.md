# phonebook
Alchemy phonebook

## To start

phonebook.py runs with Python 2.7. Clone the git repository and run ```python phonebook.py```. This launches a web.py server on port 8080 and starts the phonebook HTTP service.

You can choose a different port with ```python phonebook.py <port>```.

## Run tests

Run the test suite with ```python test_phonebook.py```.

## API calls

You can make the following API calls:

### List entries

| HTTP Verb | URL | Request body | Description |
|-----------|----|--------------|---------------|
| `GET` | `/` | Not required | List all entries in the phonebook |

- Example JSON response (status 200)

```
[
    {
        "address": null,
        "surname": "Mouse",
        "id": 3,
        "firstname": "Mickey",
        "number": "01234567789"
    },
    {
        "address": "13 Other Road, Disneyland",
        "surname": "Mouse",
        "id": 6,
        "firstname": "Minnie",
        "number": "02045679920"
    }
]
```

### Add an entry to the phonebook

| HTTP Verb | URL | Request body | Description |
|-----------|----|--------------|---------------|
| `POST` | `/` | JSON stanza that must contain `firstname`,`surname`,`number` attributes. Optional `address` attribute. | Add an entry |

- Successful creation results in a `201 Created` response, with no body content. 
- The URI of the newly-created phonebook entry, consisting of the object id, is returned in the HTTP Location header, e.g. `/123`. 
- Use this URI, with the entry id, to request updates or deletion.

##### Error responses

| Response code | Reason |
|---------------|--------|
| 400 Bad Request | Invalid JSON data |
| 400 Bad Request | Required attributes must be present |
| 400 Bad Request | Unrecognized field in POST data. Request data must include firstname, surname, number, and optionally address. |
| 400 Bad Request | Field must not be null or an empty string. |
| 400 Bad Request | Phone number must be 6-15 digits long, and contain only numbers, -, # or spaces. |

### Update a phonebook entry

| HTTP Verb | URL | Request body | Description |
|-----------|----|--------------|---------------|
| `PUT` | `/<entry_id>` | JSON stanza that must contain at least one of `firstname`,`surname`,`number`,`address` attributes. You can send an address attribute of "" (empty string) to remove an existing address for an entry. | Update an entry |

- Successful creation results in a `204 No Content` response, with no body content. 
- Find the <entry_id> attribute from the API call to list entries, or from the Location response header after successful creation of an entry.

##### Error responses

| Response code | Reason |
|---------------|--------|
| 400 Bad Request | Update PUT request must contain at least one field. |
| 400 Bad Request | Invalid JSON data |
| 400 Bad Request | Required attributes must be present |
| 400 Bad Request | Unrecognized field in POST data. Request data must include firstname, surname, number, and optionally address. |
| 400 Bad Request | Field must not be null or an empty string. |
| 400 Bad Request | Phone number must be 6-15 digits long, and contain only numbers, -, # or spaces. |
| 404 Not Found | No phonebook entry exists with this id. |

### Delete a phonebook entry

| HTTP Verb | URL | Request body | Description |
|-----------|----|--------------|---------------|
| `DELETE` | `/<entry_id>` | Not required | Delete an entry |

- Successful deletion results in a `204 No Content` response, with no body content. 
- Find the <entry_id> attribute from the API call to list entries, or from the Location response header after successful creation of an entry.

##### Error responses

| Response code | Reason |
|---------------|--------|
| 404 Not Found | No phonebook entry exists with this id. |

### Search phonebook by surname

| HTTP Verb | URL | Request body | Description |
|-----------|----|--------------|---------------|
| `GET` | `/<surname>` | Not required | Search the phonebook for all entries with this surname |

- Example JSON response (status 200)

```
[
    {
        "address": null,
        "surname": "Mouse",
        "id": 3,
        "firstname": "Mickey",
        "number": "01234567789"
    },
    {
        "address": "13 Other Road, Disneyland",
        "surname": "Mouse",
        "id": 6,
        "firstname": "Minnie",
        "number": "02045679920"
    }
] 
```
