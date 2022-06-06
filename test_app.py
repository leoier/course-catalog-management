import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Subject, Instructor, Course


'''
Please update the access tokens as environment variables accordingly

- INSTRUCTOR_TOKEN  access token for role instructor
- DIRECTOR_TOKEN    access token for role director

'''

instructor_token = os.environ['INSTRUCTOR_TOKEN']
instructor_headers = {'Authorization' : 'Bearer '+ instructor_token}

director_token = os.environ['DIRECTOR_TOKEN']
director_headers = {'Authorization' : 'Bearer '+ director_token}


class TestCase(unittest.TestCase):
    """This class represents the test cases"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        # change this line to connect to your local postgresql database
        self.database_path = os.environ['TEST_DATABASE_URL']
        if self.database_path.startswith("postgres://"):
            self.database_path = self.database_path.replace("postgres://", "postgresql://", 1)

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass


    """
    Helper functions to assert 404, 422, 405 error is correctly handled
    """
    def assert_404(self, res):
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['code'], 404)
        self.assertEqual(data['message'], 'resource not found')


    def assert_422(self, res):
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['code'], 422)
        self.assertEqual(data['message'], 'request unprocessable')


    def assert_405(self, res):
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['code'], 405)
        self.assertEqual(data['message'], 'method not allowed')


    def assert_no_auth(self, res):
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Authorization header is expected')


    def assert_no_permission(self, res):
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Requested permission not allowed')


    """
    Tests on the end points and expected errors
    """

    def test_get_courses(self):
        res = self.client().get('/courses')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['courses'])


    def test_get_courses_by_subject(self):
        res = self.client().get('/subjects/2/courses')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['courses'])
        subject = Subject.query.filter_by(id=2).one_or_none()
        for course in data['courses']:
            self.assertEqual(course['subject'], subject.title)


    def test_get_courses_invalid_subject(self):
        res = self.client().get('/subjects/100/courses')
        self.assert_404(res)


    def test_get_courses_by_instructor(self):
        res = self.client().get('/instructors/2/courses')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['courses'])
        instructor = Instructor.query.filter_by(id=2).one_or_none()
        for course in data['courses']:
            self.assertEqual(course['instructor'], instructor.full_name())


    def test_get_courses_invalid_instructor(self):
        res = self.client().get('/instructors/100/courses')
        self.assert_404(res)


    def test_search_courses(self):
        res = self.client().post('/courses/search', json={
            'search_term': 'calculus'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['courses'])
        # verify the search result matches our expectation
        exp_match_id = [1, 2, 3]
        for course in data['courses']:
            self.assertTrue(course['id'] in exp_match_id)
            exp_match_id.remove(course['id'])
        self.assertEqual(len(exp_match_id), 0)


    def test_search_courses_missing_input(self):
        res = self.client().post('/courses/search', json={})
        self.assert_422(res)


    def test_create_course(self):
        res = self.client().post('/courses', json={
            'title': 'Differential Equaltions',
            'instructor_id': '3',
            'subject_id': '4',
            'prerequisites_id': '[3]',
            'credit_hours': '3'
        }, headers = director_headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['course created'])
        course = Course.query.filter_by(id=int(data['course created']['id'])).one_or_none()
        self.assertIsNotNone(course)


    def test_create_course_missing_input(self):
        res = self.client().post('/courses', json={
            'title': 'Differential Equaltions',
            'prerequisites_id': '[3]',
            'credit_hours': '3'
        }, headers = director_headers)
        self.assert_422(res)


    def test_create_course_no_auth(self):
        res = self.client().post('/courses', json={
            'title': 'Differential Equaltions',
            'instructor_id': '3',
            'subject_id': '4',
            'prerequisites_id': '[3]',
            'credit_hours': '3'
        })
        self.assert_no_auth(res)


    def test_create_course_no_permission(self):
        res = self.client().post('/courses', json={
            'title': 'Differential Equaltions',
            'instructor_id': '3',
            'subject_id': '4',
            'prerequisites_id': '[3]',
            'credit_hours': '3'
        }, headers = instructor_headers)
        self.assert_no_permission(res)


    def test_edit_course(self):
        res = self.client().patch('/courses/1', json={
            'credit_hours': '6'
        }, headers = instructor_headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['course updated'])
        course = Course.query.filter_by(id=1).one_or_none()
        self.assertIsNotNone(course)
        self.assertEqual(course.credit_hours, 6)
        self.assertEqual(course.approved, False)


    def test_edit_course_not_found(self):
        res = self.client().patch('/courses/100', json={
            'credit_hours': '6'
        }, headers = instructor_headers)
        self.assert_404(res)


    def test_edit_course_no_auth(self):
        res = self.client().patch('/courses/1', json={
           'credit_hours': '6'
        })
        self.assert_no_auth(res)


    def test_approve_course(self):
        res = self.client().post('courses/8/approval', headers = director_headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['course approved'])
        course = Course.query.filter_by(id=8).one_or_none()
        self.assertIsNotNone(course)
        self.assertEqual(course.approved, True)


    def test_approve_course_no_permission(self):
        res = self.client().post('courses/8/approval', headers = instructor_headers)
        self.assert_no_permission(res)


    def test_delete_course(self):
        res = self.client().delete('/courses/9', headers = director_headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['course deleted'])
        course = Course.query.filter_by(id=9).one_or_none()
        self.assertEqual(course, None)


    def test_delete_course_no_permission(self):
        res = self.client().delete('/courses/9', headers = instructor_headers)
        self.assert_no_permission(res)


    def test_get_subjects(self):
        res = self.client().get('/subjects')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['subjects'])


    def test_get_instructors(self):
        res = self.client().get('/instructors')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['instructors'])


    def test_create_instructor(self):
        res = self.client().post('/instructors', json={
            'first_name': 'Frank',
            'last_name': 'King',
            'title': 'Dr.',
            'department': 'Department of Economics',
            'email': 'fking@university@edu'
        }, headers = director_headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['instructor created'])
        instructor = Instructor.query.filter_by(id=int(data['instructor created']['id'])).one_or_none()
        self.assertIsNotNone(instructor)


    def test_create_instructor_missing_input(self):
        res = self.client().post('/instructors', json={
            'first_name': 'Frank',
            'email': 'fking@university@edu'
        }, headers = director_headers)
        self.assert_422(res)


    def test_create_instructor_no_permission(self):
        res = self.client().post('/instructors', json={
            'first_name': 'Frank',
            'last_name': 'King',
            'title': 'Dr.',
            'department': 'Department of Economics',
            'email': 'fking@university@edu'
        }, headers = instructor_headers)
        self.assert_no_permission(res)


    def test_edit_instructor(self):
        res = self.client().patch('/instructors/1', json={
            'title': 'Distinguished Professor',
            'phone': '999-999-9999'
        }, headers = director_headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['instructor updated'])
        instructor = Instructor.query.filter_by(id=1).one_or_none()
        self.assertIsNotNone(instructor)
        self.assertEqual(instructor.title, 'Distinguished Professor')
        self.assertEqual(instructor.phone, '999-999-9999')


    def test_edit_instructor_no_permission(self):
        res = self.client().patch('/instructors/1', json={
            'title': 'Distinguished Professor',
            'phone': '999-999-9999'
        }, headers = instructor_headers)
        self.assert_no_permission(res)


    def test_delete_instructor(self):
        res = self.client().delete('/instructors/4', headers = director_headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['instructor deleted'])
        instructor = Instructor.query.filter_by(id=4).one_or_none()
        self.assertEqual(instructor, None)
        # verify the related courses are deleted
        courses = Course.query.filter_by(instructor_id=4).all()
        self.assertEqual(len(courses), 0)


    def test_delete_instructor_not_found(self):
        res = self.client().delete('/instructors/100', headers = director_headers)
        self.assert_404(res)


    def test_delete_instructor_no_permission(self):
        res = self.client().delete('/instructors/100', headers = instructor_headers)
        self.assert_no_permission(res)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
