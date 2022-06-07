# University Course Catalog Management System

This is the backend of a simple university course catalog, which enables users to retrieve information of the courses, instructors and subjects in the course catalog database. And provide management access to manage courses and instructors to different roles. The API of the system is currently hosted on [https://course-catalog-leoier.herokuapp.com](https://course-catalog-leoier.herokuapp.com).


## Role-based access control

Role-based access control (RBAC) is implemented to control access of different roles interacting with the course catalog database. Authentication is done by passing a Bearer Token in the request header. The roles with different access levels are as follows:

1. Public and students: View the information of the courses and instructors.
2. Instructors: Edit the courses, in addiction to all access of public and students.
3. Department Director: Add, edit, delete instructors; add, edit, approve, delete courses, in addiction to all access of instructors.

Access Token is issued through this [link](https://dev--s9qtz0w.us.auth0.com/authorize?response_type=token&audience=course&client_id=4TcuieFIWK3q8sKE5zPqswmyTN0SW3U4&redirect_uri=https://course-catalog-leoier.herokuapp.com) by logging in the responding account of a specific role. No access token is required for the public and students.

## Preparations

1. **Python 3.8** - Follow instructions to install python 3.8 for your platform in the [python docs](https://docs.python.org/3.8/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)  

3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies we selected within the `requirements.txt` file by running:
```bash
pip install -r requirements.txt
```

4. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py.

 - [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server.

 - [Python-Jose](https://python-jose.readthedocs.io/en/latest/) is used to process the JSON Web Tokens for access control.  


These are the files relevant for the current project
```bash
 .
 ├── Procfile               # specifications for Heroku deploy
 ├── README.md        
 ├── app.py                 # implements the app and apis
 ├── auth.py                # implements RBAC authentication
 ├── courseCatalog.psql     # postgresql script to restore dummy data
 ├── manage.py              # database manage & migrations on Heroku
 ├── models.py              # database implementation
 ├── requirements.txt       # dependencies
 ├── runtime.txt            # specifications for Heroku deploy
 ├── setup.sh               # set up environment variables for local run and tests
 ├── test_app.py            # unit tests for the app
 ├── udacity-capstone-course-catalog.postman_collection.json  # postman collection to test the apis
 └── unitTests.sh           # script to initialize test database and run unit tests
```

## Database Setup

First export the database specifications as the environment variable `DATABASE_URL`, or modify the database specifications in [`setup.sh`](./setup.sh) of your local database and run `source setup.sh` to update the environment variables.

With Postgres running, you may restore a database using the courseCatalog.psql file provided. In terminal run:
```bash
psql course_catalog < courseCatalog.psql
```

Alternatively, you may use `import_dummy_data` in [`models.py`](./models.py) to initialize the database with some dummy data for testing. Run the following commands in the terminal
```bash
flask shell
```
```python
from models import setup_db, import_dummy_data, Subject, Instructor, Course
import_dummy_data()
```

## Running the Server Locally

First ensure you are working using your created virtual environment.

To run the server, execute:

```bash
python3 app.py
```

You can also modify the running specifications of the app in [`app.py`](./app.py), default running specs are `host='0.0.0.0', port=8080, debug=True`.


## Testing
To run local unit tests, we assume the name of the test database is `course_catalog_test`, then export the database url as the environment variable `TEST_DATABASE_URL` to connect to your local test database. Also, get two valid tokens as the role Instructor and Director, and export them as the environment variables `INSTRUCTOR_TOKEN` and `DIRECTOR_TOKEN`.

Alternatively, you may enter the test database url and access tokens in [`setup.sh`](./setup.sh), and run `source setup.sh` to update the environment variables.

Then run
```bash
dropdb course_catalog_test --if-exists
createdb course_catalog_test
psql course_catalog_test < courseCatalog.psql
python3 test_app.py
```

Or, if you are using bash, simply run
```bash
./unittest.sh
```

To test the online api, import the collection [`udacity-capstone-course-catalog.postman_collection.json`](./udacity-capstone-course-catalog.postman_collection.json) to [Postman](https://www.postman.com/), and update the access tokens for Instructor and Director, then run the tests.

## API References

Using the course catalog API you can:

- Create, retrieve, search, update, and delete courses in the course catalog

- Retrieve the subjects of the courses

- Create, retrieve, update, and delete the instructors

The API works with standard HTTP requests, accepts json formatted request bodies, and returns json formatted responses. And authentication is done by including a Bearer token in the request header.

The base URL of the API is [https://course-catalog-leoier.herokuapp.com](https://course-catalog-leoier.herokuapp.com).

### Errors

This API follows usual HTTP response status codes to initicate success or failure of the request.  
The following is a summary of the status codes:
- 200: OK, the request works as expected
- 404: Resouce not found, the requested resouce does not exist on the server
- 401: Unauthorized, authentication is required for the request
- 403: Forbidden, the permission is insufficient to make the request
- 405: Method not Allowed, the requested method is not allowed at the address
- 422: Unprocessable, the request cannot be processed, usually due to missing or invalid parameters

Sample error response
```json
{
  "code":404,
  "message":"resource not found",
  "success":false
}
```

### Subjects

Subject object stores the id and the title of the subjects of the courses in the catalog.

#### Endpoints
```
GET /subjects
GET /subjects/${id}/courses
```
#### `GET /subjects`
- Fetches a list of subjects
- Roles Allowed: Students, Instructor, Director
- Return: An object with a single key, subjects - a list of subjects, in which the keys are the ids and the title is the corresponding string of the subject, and other status information

Sample response
```json
{
    "subjects": [
        {"id": 1, "title": "Arts and Humanities"},
        {"id": 2, "title": "Engineering and Technology"},
        {"id": 3, "title": "Life Sciences"},
        {"id": 4, "title": "Natural Sciences"},
        {"id": 5, "title": "Social Sciences and Management"}
    ],
    "success": true
}
```

#### `GET /subjects/${id}/courses`
- Fetches a list of the courses in the subject with the given id
- Roles Allowed: Students, Instructor, Director
- Return: An object with a single key, courses - a list of courses of the given subject, in which each course is a dictionary encoded with key:value pairs, and other status information

Sample response of subject Engineering and Technology
```json
{
    "courses": [
        {   "credit hours": 4, "description": "Course 1", "id": 10,
            "instructor": "Inst 1", "prerequisites": [],
            "subject": "Engineering and Technology", "title": "Course 1"
        },
        {   "credit hours": 4, "description": "Course 2", "id": 15,
            "instructor": "Inst 2", "prerequisites": [],
            "subject": "Engineering and Technology", "title": "Course 2"
        },
    ],
    "success": true
}
```

### Instructors

Instructor object stores the id, first name, last name, title, department, and contact information of the instructor in the university.

#### End Points
```
   GET /instructors
   GET /instructors/${id}/courses
  POST /instructors
 PATCH /instructors/${id}
DELETE /instructors/${id}
```

#### `GET /instructors`
- Fetches a list of the instructors in the database
- Roles Allowed: Students, Instructor, Director
- Return: A list of instructors, in which each instructor is a dictionary encoded with key:value pairs, ordered by their last name, and other status information

Sample response
```json
{
    "instructors": [
        {   "department": "Mathematics", "title": "Professor",
            "first_name": "Name1", "last_name": "Name2", "id": 3,
            "phone": "123-456-7890", "email": "a@university.edu"
        },
        {   "department": "Economics", "title": "Lecturer",
            "first_name": "Name3", "last_name": "Name4", "id": 2,
            "phone": "123-456-7890", "email": "a@university.edu"
        }
    ],
    "success": true
}
```

#### `GET /instructors/${id}/courses`
- Fetches a list of the courses taught by the given instructor
- Roles Allowed: Students, Instructor, Director
- Return: A list of courses, in which each course is a dictionary encoded with key:value pairs, and other status information

Sample response
```json
{
    "courses": [
        {   "credit hours": 3, "description": "Course 1", "id": 1,
            "instructor": "Instructor 1", "prerequisites": [],
            "subject": "Engineering and Technology", "title": "Course 1"
        },
        {   "credit hours": 4, "description": "Course 2", "id": 5,
            "instructor": "Instructor 1", "prerequisites": [2],
            "subject": "Natural Science", "title": "Course 2"
        },
    ],
    "success": true
}
```


#### `POST /instructors`
- Creates a new instructor into the database, requires first name and last name in the request body
- Roles Allowed: Director
- Return: A dictionary of the instructor created, and other status information

Sample request body
```json
{   "first_name": "FName", "last_name": "LName",
    "title": "Assistant Professor", "department": "Economics",
    "email": "email@university@edu"
}
```

Sample response
```json
{
    "instructor created": {   
        "first_name": "FName", "last_name": "LName", "id": 3,
        "title": "Assistant Professor", "department": "Economics",
        "email": "email@university@edu", "phone": Null},
    "success": true
}
```

#### `PATCH /instructors/${id}`
- Updates the information of an existing instructor
- Roles Allowed: Director
- Return: A dictionary of the instructor updated, and other status information

Sample request body on instructor with id = 3
```json
{   
    "title": "Professor"
}
```

Sample response
```json
{
    "instructor updated": {   
        "first_name": "FName", "last_name": "LName", "id": 3,
        "title": "Professor", "department": "Economics",
        "email": "email@university@edu", "phone": Null},
    "success": true
}
```

#### `DELETE /instructors/${id}`
- Deletes an existing instructor
- Roles Allowed: Director
- Return: The id of the deleted instructor, and other status information

Sample response on instructor with id = 3
```json
{
    "instructor deleted": 3,
    "success": true
}
```


### Courses

Course object stores the id, title, subject id, instructor id, a list of the id of prerequisite courses, credit hours, description, and approved status of a course in the catalog.

#### Endpoints
```
   GET /courses
  POST /courses
  POST /courses/search
 PATCH /courses/${id}
  POST /courses/${id}/approval
DELETE /courses/${id}
```

#### `GET /courses`
- Fetch a list of crouses in the course catalog database, ordered by subject id and their own id
- Roles Allowed: Students, Instructor, Director
- Return: A list of courses, in which each course is a dictionary encoded with key:value pairs, and other status information

Sample response
```json
{
    "courses": [
        {   "credit hours": 3, "description": "Course 13", "id": 10,
            "instructor": "Inst 3", "prerequisites": [],
            "subject": "Subject 1", "title": "Course 10"
        },
        {   "credit hours": 3, "description": "Course 13", "id": 13,
            "instructor": "Inst 1", "prerequisites": [],
            "subject": "Subject 1", "title": "Course 13"
        },
        {   "credit hours": 4, "description": "Course 2", "id": 2,
            "instructor": "Inst 2", "prerequisites": [],
            "subject": "Subject 2", "title": "Course 2"
        }
    ],
    "success": true
}
```

#### `POST /courses`
- Create a course in the course catalog database, requires course title, instructor id, subject id, prerequisites id, credit hours in the request body
- Roles Allowed: Director
- Return: The course created as a dictionary encoded with key:value pairs, and other status information

Sample request body
```json
{
    "title": "Course Title",
    "instructor_id": "4",
    "subject_id": "3",
    "prerequisites_id": "[3]",
    "credit_hours": "3"
}
```

Sample response
```json
{
    "course created": {
        "credit hours": 3,
        "description": "",
        "id": 15,
        "instructor": "Instructor 1",
        "prerequisites": [
            "Calculus 3"
        ],
        "subject": "Natural Sciences",
        "title": "Course Title"
    },
    "success": true
}
```

#### `POST /courses/search`
- Search a course existing in the course catalog database based on title text (case insensitive). 'search_term' is required in the request body
- Roles Allowed: Student, Instructor, Director
- Return: A list of matched courses, in which each course is a dictionary encoded with key:value pairs, and other status information

Sample request body
```json
{
    "search_term": "calculus"
}
```

Sample response
```json
{
    "courses": [
        {
            "credit hours": 4, "description": "", "id": 1,
            "instructor": "Instructor 1", "prerequisites": [],
            "subject": "Natural Sciences", "title": "Calculus 1"
        },
        {
            "credit hours": 4, "description": "", "id": 2,
            "instructor": "Instructor 1", "prerequisites": ["Calculus 1"],
            "subject": "Natural Sciences", "title": "Calculus 2"
        }
    ],
    "success": true
}
```

#### `PATCH /courses/${id}`
- Update a course existing in the course catalog database, and set it pending for approval from the director
- Roles Allowed: Instructor, Director
- Return: The course updated as a dictionary encoded with key:value pairs, and other status information

Sample request body of course with id = 1
```json
{
    "credit_hours": "6"
}
```

Sample response
```json
{
    "course updated": {
        "credit hours": 6,
        "description": "",
        "id": 1,
        "instructor": "Instructor",
        "prerequisites": [],
        "subject": "Subject",
        "title": "Course Title"
    },
    "success": true
}
```

#### `POST /courses/${id}/approval`
- Approve a course that was updated previously in the course catalog database
- Roles Allowed: Director
- Return: The course approved as a dictionary encoded with key:value pairs, and other status information

Sample response of course with id = 1
```json
{
    "course approved": {
        "credit hours": 3,
        "description": "",
        "id": 1,
        "instructor": "Instructor",
        "prerequisites": [],
        "subject": "Subject",
        "title": "Course Title"
    },
    "success": true
}
```


#### `DELETE /courses/${id}`
- Deletes an existing course in the course catalog database
- Roles Allowed: Director
- Return: The id of the deleted course, and other status information

Sample response on course with id = 3
```json
{
    "course deleted": 3,
    "success": true
}
