from app import security, user_datastore, api_version
import datetime
from database import db_session
from flask import request, jsonify
from flask_restful import Resource
from flask_security import Security, login_required, current_user
from models import Role, User, Course
from utils import check_member_role
from sqlalchemy.sql import func

class Courses(Resource):
    """Get details for a course\n
    return {message} and {data} 
    """
    def get(self, ecommerce_item_id):
        if not current_user.is_authenticated or check_member_role(["admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        course = Course.query.filter_by(ecommerce_item_id=ecommerce_item_id).first()
        if course:
            return {
                "version": api_version,
                "message": "Course information for {}".format(ecommerce_item_id),
                "data": course.as_dict()
            }, 200
        return {
                "version": api_version,
                "message": "No course found for id: {}".format(ecommerce_item_id),
                "data": {}
        }, 404

    """Update details for a course\n
    return {message} and {data} 
    """
    def put(self, ecommerce_item_id):
        if not current_user.is_authenticated or check_member_role(["admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        if "application/json" in request.headers["Content-Type"]:
            exist_course = Course.query.filter_by(ecommerce_item_id=ecommerce_item_id).first()
            if not exist_course:
                return {
                    "version": api_version,
                    "message": "This item {} does not exist in database".format(ecommerce_item_id),
                    "data": {}
                }, 404
            if request.json["ecommerce_item_id"]:
                exist_course.ecommerce_item_id = request.json["ecommerce_item_id"]
            if request.json["category"]:
            	exist_course.category = request.json["category"]
            if request.json["city"]:
            	exist_course.city = request.json["city"]
            if request.json["head_count"]:
            	exist_course.head_count = request.json["head_count"]
            if request.json["tag"]:
            	exist_course.tag = request.json["tag"]
            if request.json["description"]:
            	exist_course.description = request.json["description"]
            if request.json["instructor"]:
            	exist_course.instructor = request.json["instructor"]
            if request.json["price"]:
            	exist_course.price = request.json["price"]
            if request.json["point_price"]:
            	exist_course.point_price = request.json["point_price"]
            if request.json["thumbnail_url"]:
            	exist_course.thumbnail_url = request.json["thumbnail_url"]
            if request.json["fullsize_url"]:
            	exist_course.fullsize_url = request.json["fullsize_url"]
            if request.json["store_url"]:
            	exist_course.store_url = request.json["store_url"]
            if request.json["inactive_at"]:
            	exist_course.inactive_at = request.json["inactive_at"]
            if request.json["status"]:
            	exist_course.status = request.json["status"]
            if request.json["sale_start"]:
            	exist_course.sale_start = request.json["sale_start"]
            if request.json["sale_end"]:
            	exist_course.sale_end = request.json["sale_end"]
            if request.json["lesson_start"]:
            	exist_course.lesson_start = request.json["lesson_start"]
            if request.json["lesson_end"]:
            	exist_course.lesson_end = request.json["lesson_end"]
            exist_course.updated_at = datetime.datetime.now()
            exist_course.last_updated_by = current_user.email

            updated_course = Course.query.filter_by(ecommerce_item_id=ecommerce_item_id).first()
            return {
                "version": api_version,
                "message": "Updated course: {}".format(updated_course.title),
                "data": updated_course.as_dict()
            }, 200
        return {
            "version": api_version,
            "message": "Check data input",
            "data": {}
        }, 404

class CoursesList(Resource):
    """Return a list of courses\n
    return {message} and {data} 
    """
    def get(self):
        today_date = datetime.datetime.now().date()

        if request.args.get('months') and request.args.get('keyword'):
            filter_months = request.args.get('months').split(',')
            filter_keyword = request.args.get('keyword').split(',')
<<<<<<< HEAD
            all_available_courses = Course.query.filter(Course.sale_end >= today_date).filter(func.MONTH(Course.lesson_start).in_(filter_months)).filter(Course.title.contains(filter_keyword)).all()
=======
            #  all_available_courses = Course.query.filter(Course.sale_end >= today_date).filter(func.MONTH(Course.lesson_start).in_(filter_months)).filter(Course.title.contains(filter_keyword)).all()
            all_available_courses = Course.query.filter(Course.sale_end >= today_date).filter(func.MONTH(Course.lesson_start).in_(filter_months)).filter(Course.category.in_(filter_keyword)).all()
>>>>>>> 422bb86c162a1f366fc8349a67c752c6ccfc937d

        elif request.args.get('months'):
            filter_months = request.args.get('months').split(',')
            all_available_courses = Course.query.filter(Course.sale_end >= today_date).filter(func.MONTH(Course.lesson_start).in_(filter_months)).all()

        elif request.args.get('keyword'):
            filter_keyword = request.args.get('keyword').split(',')
<<<<<<< HEAD
            all_available_courses = Course.query.filter(Course.sale_end >= today_date).filter(Course.title.contains(filter_keyword)).all()
=======
            all_available_courses = Course.query.filter(Course.sale_end >= today_date).filter(Course.category.in_(filter_keyword)).all()
>>>>>>> 422bb86c162a1f366fc8349a67c752c6ccfc937d
        
        else:
            all_available_courses = Course.query.filter(Course.sale_end >= today_date).all()

        data = [c.as_dict() for c in all_available_courses]
<<<<<<< HEAD

=======
        
>>>>>>> 422bb86c162a1f366fc8349a67c752c6ccfc937d
        return {
            "version": api_version,
            "message": "Get all courses",
            "data": data
        }, 200

    """Create a new course\n
    return {message} and {data} 
    """
    def post(self):
        if not current_user.is_authenticated or check_member_role(["admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        if "application/json" in request.headers["Content-Type"]:
            # Maybe incoorporate the following to set variables more efficiently
            # for key, value in request.json.items():
            #     exec(key + '=value')

            ecommerce_item_id = request.json["ecommerce_item_id"]
            title = request.json["title"]
            category = request.json["category"]
            city = request.json["city"]
            head_count = request.json["head_count"]
            tag = request.json["tag"]
            description = request.json["description"]
            instructor = request.json["instructor"]
            price = request.json["price"]
            point_price = request.json["point_price"]
            thumbnail_url = request.json["thumbnail_url"]
            fullsize_url = request.json["fullsize_url"]
            store_url = request.json["store_url"]
            inactive_at = request.json["inactive_at"]
            status = request.json["status"]
            sale_start = request.json["sale_start"]
            sale_end = request.json["sale_end"]
            lesson_start = request.json["lesson_start"]
            lesson_end = request.json["lesson_end"]
            updated_at = datetime.datetime.now()
            last_updated_by = current_user.email
            
            # id cannot be duplicate 
            exist_course = Course.query.filter_by(ecommerce_item_id=ecommerce_item_id).first()
            if exist_course:
                return {
                    "version": api_version,
                    "message": "Course {} exist in database already".format(title),
                    "data": exist_course.as_dict()
            }, 422

            new_course = Course(ecommerce_item_id = ecommerce_item_id, title = title, category = category, city = city, head_count = head_count, \
                tag = tag, description = description, instructor = instructor, price = price, point_price = point_price, \
                thumbnail_url = thumbnail_url, fullsize_url = fullsize_url, store_url = store_url, inactive_at = inactive_at, \
                status = status, sale_start = sale_start, sale_end = sale_end, lesson_start = lesson_start, \
                lesson_end = lesson_end, updated_at = updated_at, last_updated_by = last_updated_by,
            )

            db_session.add(new_course)
            db_session.commit()

            created_course = Course.query.filter_by(ecommerce_item_id=ecommerce_item_id).first()
            return {
                "version": api_version,
                "message": "Created new course: {}".format(title),
                "data": created_course.as_dict()
            }, 200
        return {
            "version": api_version,
            "message": "Check data input",
            "data": {}
        }, 404
    
class CoursesFilterList(Resource):
    """Return a list of courses\n
    return {message} and {data} 
    """
    def get(self, months):
        today_date = datetime.datetime.now().date()
        filter_months = months.split(',')
        all_available_courses = Course.query.filter(Course.sale_end >= today_date).filter(func.MONTH(Course.lesson_start).in_(filter_months)).all()
        data = [c.as_dict() for c in all_available_courses]

        return {
            "version": api_version,
            "message": "Get all courses filtered ",
            "data": data
        }, 200
