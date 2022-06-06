import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# database url should be set as environment variable
database_path = os.environ['DATABASE_URL']
if database_path.startswith("postgres://"):
    database_path = database_path.replace("postgres://", "postgresql://", 1)

db = SQLAlchemy()


'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


# Specification of the data Models for app.py

class Instructor(db.Model):
    __tablename__ = 'instructors'
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String, nullable = False)
    title = db.Column(db.String)
    department = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.String)
    courses = db.relationship('Course', backref = 'instructor', lazy = 'joined', cascade = 'all, delete')

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def format(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'title': self.title,
            'department': self.department,
            'email': self.email,
            'phone': self.phone
        }

    '''
    insert, update and delete the model in the database
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    courses = db.relationship('Course', backref = 'subject', lazy = 'joined', cascade = 'all, delete')

    def format(self):
        return {'id': self.id, 'title': self.title}

    '''
    insert, update and delete the model in the database
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'), nullable = False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable = False)
    # a list with the format [1, 2, 3]
    prerequisites_id = db.Column(db.String, default = '[]')
    credit_hours = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String)
    approved = db.Column(db.Boolean, nullable = False, default = False)

    def format(self):
        instructor = Instructor.query.filter_by(id=self.instructor_id).one_or_none()
        if instructor:
            instructor = instructor.full_name()
        subject = Subject.query.filter_by(id=self.subject_id).one_or_none()
        if subject:
            subject = subject.title
        prerequisites_lst = []
        prerequisites_id = self.prerequisites_id.replace('[', '').replace(']','')\
            .split(', ')

        for str_id in prerequisites_id:
            if len(str_id) == 0:
                continue
            course = self.query.filter_by(id=int(str_id)).one_or_none()
            if course:
                prerequisites_lst.append(course.title)
        return {
            'id': self.id,
            'title': self.title,
            'instructor': instructor,
            'subject': subject,
            'prerequisites': prerequisites_lst,
            'credit hours': self.credit_hours,
            'description': self.description
        }

    '''
    insert, update and delete the model in the database
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()



'''
Reseting database and import dummy data for testing.
Careful! Importing dummy data will clear all data in the database.
'''
def import_dummy_data():
    db.drop_all()
    db.create_all()
    Subject(title='Arts and Humanities').insert()
    Subject(title='Engineering and Technology').insert()
    Subject(title='Life Sciences').insert()
    Subject(title='Natural Sciences').insert()
    Subject(title='Social Sciences and Management').insert()

    Instructor(
        first_name='Steven', last_name='Vikin', title='Lecturer',
        department='Computer Science', email='sviking@university.edu',
        phone='111-222-3333'
    ).insert()
    Instructor(
        first_name='Mary', last_name='Rose', title='Assistant Professor',
        department='Economics', email='mrose@university.edu',
        phone='321-321-3210'
    ).insert()
    Instructor(
        first_name='Alexander', last_name='Adams', title='Professor',
        department='Mathematics', email='aadams@university.edu',
        phone='123-456-7890'
    ).insert()
    Instructor(
        first_name='Gorden', last_name='Nicole', title='Postdoc',
        department='Literature', email='gnicole@university.edu',
        phone='555-666-7777'
    ).insert()

    Course(
        title='Calculus 1', instructor_id=3, subject_id=4,
        prerequisites_id='[]', credit_hours=4, approved=True,
        description='Derivative of one variable'
    ).insert()
    Course(
        title='Calculus 2', instructor_id=3, subject_id=4,
        prerequisites_id='[1]', credit_hours=4, approved=True,
        description='Integration of one variable'
    ).insert()
    Course(
        title='Calculus 3', instructor_id=3, subject_id=4,
        prerequisites_id='[2]', credit_hours=4, approved=True,
        description='Derivative and integration of multi variables'
    ).insert()
    Course(
        title='Principles of Microeconomics', instructor_id=2, subject_id=5,
        prerequisites_id='[2, 3]', credit_hours=3, approved=True,
        description='Fundamentals of microeconomics'
    ).insert()
    Course(
        title='Principles of Macroeconomics', instructor_id=2, subject_id=5,
        prerequisites_id='[2, 3]', credit_hours=3, approved=True,
        description='Fundamentals of macroeconomics'
    ).insert()
    Course(
        title='Intermediate Microeconomics', instructor_id=2, subject_id=5,
        prerequisites_id='[4]', credit_hours=3, approved=True,
        description='Intermediate tools of microeconomics'
    ).insert()
    Course(
        title='Intermediate Macroeconomics', instructor_id=2, subject_id=5,
        prerequisites_id='[5]', credit_hours=3, approved=True,
        description='Intermediate tools of macroeconomics'
    ).insert()
    Course(
        title='Advanced Microeconomics', instructor_id=2, subject_id=5,
        prerequisites_id='[6]', credit_hours=3, approved=False,
        description='Advanced tools of microeconomics'
    ).insert()
    Course(
        title='Advanced Macroeconomics', instructor_id=2, subject_id=5,
        prerequisites_id='[7]', credit_hours=3, approved=True,
        description='Advanced tools of macroeconomics'
    ).insert()
    Course(
        title='Introduction to Computer Science', instructor_id=1, subject_id=2,
        prerequisites_id='[]', credit_hours=4, approved=True,
        description='Introduction to computer science and programming'
    ).insert()
    Course(
        title='Discrete Mathematics', instructor_id=3, subject_id=4,
        prerequisites_id='[]', credit_hours=4, approved=True,
        description='Introduction on set theory, logic, proof techniques, ' +
            'functions and relations, graphs, and trees'
    ).insert()
    Course(
        title='Data Structure', instructor_id=1, subject_id=2,
        prerequisites_id='[2, 10, 11]', credit_hours=4, approved=True,
        description='Introduction to basic data structures'
    ).insert()
    Course(
        title='English Literature', instructor_id=4, subject_id=1,
        prerequisites_id='[]', credit_hours=3, approved=True,
        description='Introduction to English literature'
    ).insert()
    Course(
        title='World Literature', instructor_id=4, subject_id=1,
        prerequisites_id='[]', credit_hours=3, approved=True,
        description='Introduction to World literature'
    ).insert()
