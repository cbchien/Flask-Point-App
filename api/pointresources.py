from app import security, user_datastore, api_version
import datetime
from database import db_session
from flask import request, jsonify
from flask_restful import Resource
from flask_security import Security, login_required, current_user
from models import Role, User, PointLog, UserPoint, PointType
from utils import check_member_role

# Resource for front-end website with current user
class UserPointUser(Resource):
    """Get points information for current user\n
    return {message} and {data} 
    """
    def get(self):
        data = current_user.user_point.as_dict()
        return {
            "version": api_version,
            "message":"Get points information for {}".format(current_user.email),
            "data": data
        }, 200

    """Add points for current user\n
    return {message} and {data} 
    """
    def post(self, point_id):
        try:
            email = current_user.email
            point_type = PointType.query.filter_by(id=point_id).first()
            points_to_add = point_type.points
            exist_entry = current_user.user_point

            # Direct to add points
            if points_to_add >= 0:
                if not exist_entry:
                    new_entry = UserPoint(
                        current_sum = points_to_add,
                        total_earned = points_to_add,
                    )
                    exist_entry = new_entry
                    db_session.add(new_entry)
                    db_session.commit()

                elif exist_entry:
                    exist_entry.current_sum = exist_entry.current_sum + points_to_add
                    exist_entry.total_earned = exist_entry.total_earned + points_to_add
                    exist_entry.updated_at = datetime.datetime.now()

                entry_type = "Credit" # Default to credit 
                description = "Add points {} to {}".format(points_to_add, email)
            
            # Direct to redeem points
            elif points_to_add < 0:
                entry_type = "Redeem"
                description = "Redeem points {} from {}".format(points_to_add, email)
                # Check for sufficient points
                if int(exist_entry.current_sum) >= abs(points_to_add):
                    exist_entry.current_sum = exist_entry.current_sum + points_to_add
                else:
                    data = current_user.user_point.as_dict()
                    return {
                        "version": api_version,
                        "message":"Not enough points for {}".format(current_user.email),
                        "data": data
                    }, 200

            new_data = current_user.user_point.as_dict()

            # save action log
            log = PointLog(
                entry_type = entry_type,
                description = description,
                action_points = points_to_add,
                total_points = current_user.user_point.current_sum
                )
            # add database Many-to-One relationship
            current_user.point_log.append(log)
            point_type.point_log.append(log)
            # save log to db
            db_session.add(log)
            db_session.commit()
            
            return {
                "version": api_version,
                "message": "Update with point type {} {} points for current user email {} with total points {}".format(point_type.title, points_to_add, current_user.email, exist_entry.current_sum),
                "data": new_data
            }, 200

        except Exception as e: 
            return {
                "version": api_version,
                "message": "Please see error",
                "data": {},
                "error":"{}".format(e)
            }, 404
    
# Resource for admin dashboard dealing with points
class UserPointAdmin(Resource):   
    """Get points for a user from admin panel\n
    return {message} and {data} 
    """
    def get(self, user_id):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        user = User.query.filter_by(id=user_id).first()

        data = user.user_point.as_dict()

        return {
            "version": api_version,
            "message":"Get points information for {}".format(user.email),
            "data": data
        }, 200

    """Add points for a user from admin panel\n
    return {message} and {data} 
    """
    def post(self, user_id, point_id):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401
        user = User.query.filter_by(id=user_id).first()

        try:
            email = user.email
            point_type = PointType.query.filter_by(id=point_id).first()
            points_to_add = point_type.points
            exist_entry = user.user_point
            # Direct to add points
            if points_to_add >= 0:
                if not exist_entry:
                    new_entry = UserPoint(
                        current_sum = points_to_add,
                        total_earned = points_to_add
                    )
                    user.user_point = new_entry
                    db_session.add(new_entry)
                    db_session.commit()

                elif exist_entry:
                    exist_entry.current_sum = exist_entry.current_sum + points_to_add
                    exist_entry.total_earned = exist_entry.total_earned + points_to_add
                    exist_entry.updated_at = datetime.datetime.now()

                entry_type = "Credit"
                description = "Points {} to {}".format(points_to_add, email)
            
            # Direct to redeem points
            elif points_to_add < 0:
                entry_type = "Redeem"
                description = "Redeem points {} from {}".format(points_to_add, email)
                # Check for sufficient points
                if int(exist_entry.current_sum) >= abs(points_to_add):
                    exist_entry.current_sum = exist_entry.current_sum + points_to_add
                else:
                    data = user.user_point.as_dict()
                    return {
                        "version": api_version,
                        "message":"Not enough points for {}".format(user.email),
                        "data": data
                    }, 200

            updated_user = User.query.filter_by(id=user_id).first()
            new_data = updated_user.user_point.as_dict()
            
            # save action log
            log = PointLog(
                entry_type = entry_type,
                description = "Points {} to {}".format(points_to_add, email),
                action_points = points_to_add,
                total_points = updated_user.user_point.current_sum
                )
            # add database Many-to-One relationship
            updated_user.point_log.append(log)
            point_type.point_log.append(log)
            # save log to db
            db_session.add(log)
            db_session.commit()

            return {
                "version": api_version,
                "message": "{} {} points for user {} to total points {}".format(point_type.title, points_to_add, user.email, updated_user.user_point.current_sum),
                "data": new_data
            }, 200
        except Exception as e: 
            return {
                "version": api_version,
                "message": "Please see error",
                "data": "{}".format(e)
            }, 404



        return "Add {} point type to user {} as an admin".format(user_id, point_id)

class PointTypeAdmin(Resource):
    """Get a point type from admin panel\n
    return {message} and {data} 
    """
    def get(self, point_id):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        try:
            if int(point_id) <= 0 or int(point_id) > 999: # check point id is integer between 0 and 999
                return {
                    "version": api_version,
                    "message": "Please check your point id input"
                }, 422
            
            else:
                single_data = PointType.query.filter_by(id=point_id).first().as_dict()
                return {
                        "version": api_version,
                        "message": "Viewing point type {} as an admin".format(point_id),
                        "data": single_data
                }, 200
        except Exception as e:
            return {
                    "version": api_version,
                    "message": "An error occurred. Please see error message",
                    "error": "{}".format(e)
                }, 404

    """Update a point type from admin panel\n
    return {message} and {data} 
    """
    def put(self, point_id):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        if "application/json" in request.headers["Content-Type"]:
            current_entry = PointType.query.filter_by(id=point_id).first()
            if current_entry:
                input_title = request.json.get("title")
                input_description = request.json.get("description")
                input_points = request.json.get("points")
                change = []
                if input_title is not None:
                    # current_entry.title = input_title
                    change.append({"title":input_title})
                if input_description is not None:
                    # current_entry.description = input_description
                    change.append({"description":input_description})
                if input_points is not None:
                    # current_entry.points = input_points
                    change.append({"input":input_points})

                updated_current_entry = PointType.query.filter_by(id=point_id).first()

                # create log for modification
                log = PointLog(
                    entry_type = "Update Point ssssType",
                    description = "update with {}".format(change),
                    action_points = "",
                    total_points = ""
                    )
                # add database Many-to-One relationship
                current_user.point_log.append(log)
                updated_current_entry.point_log.append(log)
                # save log to db
                db_session.add(log)
                db_session.commit()

                return {
                    "version": api_version,
                    "message": "Updated {}: {} with {}".format(point_id, updated_current_entry.title, change),
                    "data": updated_current_entry.as_dict()
                }, 200

        return {
            "version": api_version,
            "message":"Check header and data",
            "data": {}
        }, 404

class PointTypeListAdmin(Resource):
    """Get a list of point type from admin panel\n
    return {message} and {data} 
    """
    def get(self):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        try:
            all_point_type = PointType.query.order_by(PointType.id).all()
            all_data = [i.as_dict() for i in all_point_type]
            return {
                "version": api_version,
                "message": "Viewing all point type as an admin",
                "data": all_data,
            }, 200
            
        except Exception as e:
            return {
                    "version": api_version,
                    "message": "An error occurred. Please see error message",
                    "error": "{}".format(e)
                }, 404

    """Add a point type from admin panel\n
    return {message} and {data} 
    """
    def post(self):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        if "application/json" in request.headers["Content-Type"]:
            try:
                input_title = request.json.get("title")
                input_description = request.json.get("description")
                input_points = request.json.get("points")
                if input_title is None or input_description is None or input_points is None:
                    return {
                        "version": api_version,
                        "message": "Please make sure you enter all the required input field",
                        "data": {}
                    }, 422
                current_entry = PointType.query.filter_by(title=input_title).first()
                if current_entry:
                    return {
                        "version": api_version,
                        "message": "There is an existing point tpye with the same title",
                        "data": current_entry.as_dict()
                    }, 422
                
                new_point_type = PointType(
                        title = input_title,
                        description = input_description,
                        points = input_points,
                        updated_by = current_user.email
                    )
                db_session.add(new_point_type)  
                db_session.commit()
                added_entry = PointType.query.filter_by(title=input_title).first()

                # create log for new entry
                fields = [{"title": input_title, "description": input_description, "points" :input_points }]
                log = PointLog(
                    entry_type = "Create Point Type",
                    description = "Create new point type {}".format(fields),
                    action_points = "",
                    total_points = ""
                    )
                # add database Many-to-One relationship
                current_user.point_log.append(log)
                added_entry.point_log.append(log)
                # save log to db
                db_session.add(log)
                db_session.commit()

                return {
                    "version": api_version,
                    "message": "Created {} {} points for {}".format(added_entry.title, added_entry.points, added_entry.description),
                    "data": added_entry.as_dict()
                }, 200

            except Exception as e:
                return {
                    "version": api_version,
                    "message": "An error occurred. Please see error message",
                    "error": "{}".format(e)
                }, 404

        return {
            "version": api_version,
            "message":"Check header and data",
            "data": {}
        }, 404

class PointLogAdmin(Resource):
    """Get point logs for a user from admin panel\n
    return {message} and {data} 
    """
    def get(self, user_id):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        return "Seeing {}'s point log as an admin".format(user_id)
