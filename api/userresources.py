from app import security, user_datastore, api_version, client
import datetime, re, ast, json
from database import db_session
from flask import request, jsonify, session
from flask_restful import Resource
from flask_security import Security, login_required, current_user
from flask_security.utils import hash_password, verify_password, login_user, logout_user
from models import User, Role, Logging, PointLog, PointType
from utils import check_member_role, return_permission_list_for_user

class MemberChangePassword(Resource):
    """Change a member's password \n
    return {message} and {data} 

    :param string email: Member's email as primary account identifier \n
    :param string current_password: User's current password \n
    :param string new_password: At least 6 digits \n
    :param array new_password_retype: Retype new password
    """
    def post(self):
        email = request.json["email"]
        # For future use if members can change their own password
        # current_password = request.json["current_password"]
        new_password = request.json["new_password"]
        new_password_retype = request.json["new_password_retype"]
        user = User.query.filter_by(email=email).first()
        # if verify_password(current_password, user.password) and new_password == new_password_retype and len(current_password) > 5:
        if new_password == new_password_retype and len(new_password) > 5:
            user_datastore.find_user(email=email).password = hash_password(new_password)
            db_session.commit()
        return {
            "version": api_version,
            "message":"Member password for {} has been updated".format(email),
            "data": {
                "email": "{}".format(email),
            }
        }, 200

class MemberList(Resource):
    def get(self):
        all_user = User.query.order_by(User.id).all()
        data = [user.as_dict() for user in all_user]

        return {
            "version": api_version,
            "message": 'All user',
            "data": data
        }, 200

    """Register for a new member \n
    return {message} and {data} 

    :param string email: Member's email as primary account identifier \n
    :param string password: At least 6 digits \n
    :param string username: A user defined username \n
    :param array suppliers: A array of supplier ID. Default N/A \n
    :param string company: The company that the member belongs to \n
    :param string contact: Member's contact number
    """
    def post(self):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        if "application/json" in request.headers["Content-Type"]:
            email = request.json["email"]
            print('\n\n',email,'\n\n')
            password = request.json["password"]
            cocospace_username = request.json.get("cocospace_username")
            current_login_ip = request.remote_addr
            company = request.json.get("company")
            contact = request.json.get("contact")
            address = request.json.get("address")
            city = request.json.get("city")
            birthdate = request.json.get("birthdate")
            gender = request.json.get("gender")
            categories = request.json.get("categories")
            role = request.json.get("role")
            
            status = "active" # default

        # Data input checkers
        if user_datastore.get_user(email):
            return {
                "version": api_version,
                "message": "User {} exist. Please login".format(email),
                "data": {}
            }, 422 
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {
                "version": api_version,
                "message": "Please check your email format.",
                "data": {}
            }, 422
        elif len(password) < 6 or not password:
            return {
                "version": api_version,
                "message": "Password must be at least 6 characters long.",
                "data": {}
            }, 422
        elif not Role.query.filter_by(name=role).first():
            return {
                "version": api_version,
                "message": "This role: {} does not exist".format(role),
                "data": {}
            }, 422

        # create user and add user role
        user = User(
            email = email,
            cocospace_username = cocospace_username,
            password = hash_password(password),
            current_login_ip = current_login_ip,
            status = status,
            contact = contact,
            address = address,
            city = city,
            categories = categories,
            company = company,
            birthdate = birthdate,
            gender = gender
        )

        role_to_append = Role.query.filter_by(name=role).first()
        role_to_append.users.append(user)
        db_session.add(user)
        db_session.commit()

        user = User.query.filter_by(email=email).first()
        data = user.as_dict()
        return {
                "version": api_version,
                "message": "User {} created.".format(email),
                "data": data
            }, 200

class Member(Resource):
    """Display member info with given member id \n
    return {message} and {data} 
    """
    def get(self, member_id):
        # if check_member_role(["admin"], current_user.email) == False:
        #     return {
        #         "message": 'Missing authorization to retrieve content',
        #     }, 401
        user = User.query.filter_by(id=member_id).first()
        data = user.as_dict()
        return {
            "version": api_version,
            "message": 'User id: {} - {}'.format(user.id,user.email),
            "data": data
        }, 200

    """Change a member's information \n
    return {message} and {data} 

    :param string username: Member's email as primary account identifier \n
    :param array suppliers: An array of suppilers' ID \n
    :param string contact: Member's phone number \n
    :param string company: The company the member belongs to \n
    :param boolean: Member status status
    """
    def put(self, member_id):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        if "application/json" in request.headers["Content-Type"]:
            cocospace_username = request.json.get("cocospace_username")
            company = request.json.get("company")
            contact = request.json.get("contact")
            address = request.json.get("address")
            city = request.json.get("city")
            birthdate = request.json.get("birthdate")
            gender = request.json.get("gender")
            categories = request.json.get("categories")
            role = request.json.get("role")
            status = request.json.get("status")

            if role and not Role.query.filter_by(name=role).first():
                return {
                    "version": api_version,
                    "message": "This role: {} does not exist".format(role),
                    "data": {}
                }, 422

            user = User.query.filter_by(id=member_id).first()
            role_to_append = Role.query.filter_by(name=role).first()

            if user:
                if cocospace_username is not None:
                    user.cocospace_username = cocospace_username
                if company is not None:
                    user.company = company
                if contact is not None:
                    user.contact = str(contact)
                if address is not None:
                    user.address = address
                if city is not None:
                    user.city = city
                if birthdate is not None:
                    user.birthdate = birthdate
                if gender is not None:
                    user.gender = gender
                if categories is not None:
                    user.categories = categories
                if status is not None:
                    user.status = status
                if role is not None and role_to_append:
                    role_to_append.users.append(user)
                db_session.commit()
                user_updated = User.query.filter_by(id=member_id).first()
                return {
                    "version": api_version,
                    "message":"Update {}(id: {}) info".format(user_updated.email, user_updated.id),
                    "data": user_updated.as_dict()
                }, 200
        return {
                "version": api_version,
                "message":"Check header and data type",
                "data": {}
            }, 404
            
class MemberLogin(Resource):
    """Change a member's information \n
    return {message} and {data} 

    :param string email: Member's email as primary account identifier \n
    :param string password: Member's password
    """
    def post(self):
        if "application/json" in request.headers["Content-Type"]:
            email = request.json["email"]
            password = request.json["password"]
            user = user_datastore.find_user(email=email)
            if user and verify_password(password, user.password):
                login_user(user)
                user.login_count += 1
                user.last_login_ip = user.current_login_ip
                user.current_login_ip = request.remote_addr
                user.last_login_at = user.current_login_at
                user.current_login_at = datetime.datetime.now()
                db_session.commit()
                try:
                    format_permission = return_permission_list_for_user(user.id)
                except:
                    format_permission = "server error"
                
                # Add daily login point
                exist_entry = user.user_point
                point_type = PointType.query.filter_by(title="daily_login").first()
                points_to_add = point_type.points

                # only add once
                today_date = datetime.datetime.now().date()
                added = user.point_log.filter(PointLog.timestamp >= today_date).filter_by(point_type_id=point_type.id).first()
                if not added:
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

                    # save action log
                    log = PointLog(
                        entry_type = "Credit",
                        description = "Points {} to {}".format(points_to_add, email),
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
                    "message": "Successfully logged in as {}".format(email),
                    "data": {
                        "email": email,
                        "username": user.cocospace_username,
                        "company": user.company,
                        "contact": user.contact,
                        "address": user.address,
                        "role": user.role.name,
                        "profile_url": user.profile_url,
                        "permission": format_permission
                    }
                }, 200
            return {
                "version": api_version,
                "message": "Please check your log in credentials for {}".format(email),
                "data": {}
                }, 401
        else:
            return {
                "version": api_version,
                "message": "Please check your input type",
                "data": {}
            }, 404

class MemberLogout(Resource):
    """Logout member \n
    return {message} and {data} 
    """
    @login_required
    def post(self):
        logout_user()
        return {
                    "version": api_version,
                    "message": "Successfully logged out",
                    "data": {}
                }, 200

class OpsHistoryList(Resource):
    """Display all operation history
       Limited to 300 entries
    """
    def get(self):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401
        
        ops_history = Logging.query.order_by(Logging.timestamp.desc()).limit(300)
        data = [log.as_dict() for log in ops_history]
        return {
            "version": api_version,
            "message": 'Ops history',
            "data": data
        }, 200

class OpsHistory(Resource):
    """Display member's operation history \n
    return {message} and {data} 

    :param string email: Member's email as primary account identifier \n
    """
    def get(self, member_id):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        if "application/json" in request.headers["Content-Type"]:
            user = user_datastore.find_user(id=member_id)
            ops_history = Logging.query.filter_by(email=user.email).all()
            data = [log.as_dict() for log in ops_history]
            return {
                "version": api_version,
                "message": 'Ops history for {} (User id {})'.format(user.email, user.id),
                "data": data
            }, 200
        return {
            "version": api_version,
            "message": "Please check your input data type",
            "data": {}
        }, 404



