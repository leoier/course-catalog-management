import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Instructor, Subject, Course
from auth import AuthError, requires_auth

expected_errors = [404, 422, 405, 500]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  CORS(app, resources={r'/*': {'origins': '*'}})

  @app.after_request
  def after_request(response):
      response.headers.add(
        'Access-Control-Allow-Headers', 'Content-Type'
      )
      response.headers.add(
        'Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTION'
      )
      return response


  '''
  end points
  '''
  @app.route('/courses')
  def get_list_courses():
      try:
          course_lst = Course.query.order_by('subject_id', 'id').all()
          courses = [course.format() for course in course_lst]
          return jsonify({
              'success': True,
              'courses': courses
          })
      except:
          abort(422)


  @app.route('/courses/search', methods = ['POST'])
  def search_course():
      data = request.get_json()
      if 'search_term' not in data:
          abort(422)
      search_term = data['search_term']
      matched_lst = Course.query.filter(Course.title.ilike(f'%{search_term}%')).all()
      courses = [course.format() for course in matched_lst]
      return jsonify({
          'success': True,
          'courses': courses
      })


  @app.route('/courses', methods = ['POST'])
  @requires_auth('post:courses')
  def create_course(payload):
      data = request.get_json()
      try:
          required_fields = ['title', 'instructor_id', 'subject_id',\
              'prerequisites_id', 'subject_id', 'credit_hours']
          for field in required_fields:
              if field not in data:
                  abort(422)

          if 'description' in data:
              description = data['description']
          else:
              description = ""

          course = Course(
              title = data['title'],
              instructor_id = data['instructor_id'],
              subject_id = data['subject_id'],
              prerequisites_id = data['prerequisites_id'],
              credit_hours = data['credit_hours'],
              description = description,
              approved = True
          )
          course.insert()
          return jsonify({
              'success': True,
              'course created': course.format()
          })

      except AuthError as error:
          abort(error.status_code)
      except Exception as e:
          if 'code' in dir(e) and e.code in expected_errors:
              abort(e.code)
          else:
              abort(422)


  @app.route('/courses/<cid>', methods = ['PATCH'])
  @requires_auth('patch:courses')
  def edit_course(payload, cid):
      try:
          course = Course.query.filter_by(id=cid).one_or_none()
          if course is None:
              abort(404)
          data = request.get_json()
          if 'title' in data:
              course.title = data['title']
          if 'instructor_id' in data:
              course.instructor_id = data['instructor_id']
          if 'subject_id' in data:
              course.subject_id = data['subject_id']
          if 'prerequisites_id' in data:
              course.prerequisites_id = data['prerequisites_id']
          if 'credit_hours' in data:
              course.credit_hours = data['credit_hours']
          if 'description' in data:
              course.description = data['description']
          course.approved = False
          course.update()
          return jsonify({
              'success': True,
              'course updated': course.format()
          })
      except AuthError as error:
          abort(error.status_code)
      except Exception as e:
          if 'code' in dir(e) and e.code in expected_errors:
              abort(e.code)
          else:
              abort(422)


  @app.route('/courses/<cid>/approval', methods = ['POST'])
  @requires_auth('approve:courses')
  def approve_course(payload, cid):
      try:
          course = Course.query.filter_by(id=cid).one_or_none()
          if course is None:
              abort(404)
          course.approved = True
          course.update()
          return jsonify({
              'success': True,
              'course approved': course.format()
          })
      except AuthError as error:
          abort(error.status_code)
      except Exception as e:
          if 'code' in dir(e) and e.code in expected_errors:
              abort(e.code)
          else:
              abort(422)



  @app.route('/courses/<cid>', methods = ['DELETE'])
  @requires_auth('delete:courses')
  def delete_course(payload, cid):
      try:
          course = Course.query.filter_by(id=cid).one_or_none()
          if course is None:
              abort(404)
          course.delete()
          return jsonify({
              'success': True,
              'course deleted': cid
          })
      except AuthError as error:
          abort(error.status_code)
      except Exception as e:
          if 'code' in dir(e) and e.code in expected_errors:
              abort(e.code)
          else:
              abort(422)


  @app.route('/subjects')
  def get_subjects():
      try:
          subject_lst = Subject.query.order_by('id').all()
          subjects = [subject.format() for subject in subject_lst]
          return jsonify({
              'success': True,
              'subjects': subjects
          })
      except:
          abort(422)


  @app.route('/subjects/<sid>/courses')
  def get_list_courses_by_subject(sid):
      subject = Subject.query.filter_by(id=sid).one_or_none()
      if subject is None:
          abort(404)
      courses = [course.format() for course in subject.courses]
      return jsonify({
          'success': True,
          'courses': courses
      })



  @app.route('/instructors')
  def get_instructors():
      try:
          instructor_lst = Instructor.query.order_by('last_name').all()
          instructors = [instructor.format() for instructor in instructor_lst]
          return jsonify({
              'success': True,
              'instructors': instructors
          })
      except:
          abort(422)


  @app.route('/instructors/<iid>/courses')
  def get_list_courses_by_instructor(iid):
      instructor = Instructor.query.filter_by(id=iid).one_or_none()
      if instructor is None:
          abort(404)
      courses = [course.format() for course in instructor.courses]
      return jsonify({
          'success': True,
          'courses': courses
      })


  @app.route('/instructors', methods = ['POST'])
  @requires_auth('post:instructors')
  def create_instructor(payload):
      data = request.get_json()
      try:
          required_fields = ['first_name', 'last_name']
          for field in required_fields:
              if field not in data:
                  abort(422)

          if 'title' in data:
              title = data['title']
          else:
              title = None

          if 'department' in data:
              department = data['department']
          else:
              department = None

          if 'email' in data:
              email = data['email']
          else:
              email = None

          if 'phone' in data:
              phone = data['phone']
          else:
              phone = None

          instructor = Instructor(
              first_name = data['first_name'],
              last_name = data['last_name'],
              title = title,
              department = department,
              email = email,
              phone = phone
          )
          instructor.insert()
          return jsonify({
              'success': True,
              'instructor created': instructor.format()
          })

      except AuthError as error:
          abort(error.status_code)
      except Exception as e:
          if 'code' in dir(e) and e.code in expected_errors:
              abort(e.code)
          else:
              abort(422)


  @app.route('/instructors/<iid>', methods = ['PATCH'])
  @requires_auth('patch:instructors')
  def edit_instructor(payload, iid):
      try:
          instructor = Instructor.query.filter_by(id=iid).one_or_none()
          if instructor is None:
              abort(404)
          data = request.get_json()
          if 'first_name' in data:
              instructor.first_name = data['first_name']
          if 'last_name' in data:
              instructor.last_name = data['last_name']
          if 'title' in data:
              instructor.title = data['title']
          if 'department' in data:
              instructor.department = data['department']
          if 'email' in data:
              instructor.email = data['email']
          if 'phone' in data:
              instructor.phone = data['phone']
          instructor.update()
          return jsonify({
              'success': True,
              'instructor updated': instructor.format()
          })

      except AuthError as error:
          abort(error.status_code)
      except Exception as e:
          if 'code' in dir(e) and e.code in expected_errors:
              abort(e.code)
          else:
              abort(422)


  @app.route('/instructors/<iid>', methods = ['DELETE'])
  @requires_auth('delete:instructors')
  def delete_instructor(payload, iid):
      try:
          instructor = Instructor.query.filter_by(id=iid).one_or_none()
          if instructor is None:
              abort(404)
          instructor.delete()
          return jsonify({
              'success': True,
              'instructor deleted': iid
          })

      except AuthError as error:
          abort(error.status_code)
      except Exception as e:
          if 'code' in dir(e) and e.code in expected_errors:
              abort(e.code)
          else:
              abort(422)


  @app.route('/')
  def index():
      return 'Welcome to the University Course Catalog Management System!' +
        'The API references can be found at https://github.com/leoier/udacity-full-stack-capstone/blob/main/README.md'


  '''
  Error handlers on expected errors
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
        'success': False,
        'code': 404,
        'message': 'resource not found'
      }), 404


  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        'success': False,
        'code': 422,
        'message': 'request unprocessable'
      }), 422


  @app.errorhandler(405)
  def method_not_allowed(error):
      return jsonify({
        'success': False,
        'code': 405,
        'message': 'method not allowed'
      }), 405


  @app.errorhandler(500)
  def internal_server_error(error):
      return jsonify({
        'success': False,
        'code': 500,
        'message': 'internal server error'
      }), 500


  '''
  Error handlers for AuthError
  '''
  @app.errorhandler(401)
  def unauthorized(error):
      return jsonify({
          "success": False,
          "error": "401",
          "message": error.description
      }), 401


  @app.errorhandler(403)
  def forbidden(error):
      return jsonify({
          "success": False,
          "error": "403",
          "message": error.description
      }), 403


  return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
