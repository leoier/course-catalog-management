import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# # for local tests
# from dotenv import load_dotenv
# load_dotenv()

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
