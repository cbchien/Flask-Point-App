from app import security, user_datastore, api_version
from database import db_session
from flask import request, jsonify
from flask_restful import Resource
from flask_security import Security, login_required, current_user
from models import Role, User, Permission
from utils import check_member_role, return_permission_list

class RoleList(Resource):
    """Return a list of roles\n
    return {message} and {data} 
    """
    def get(self):
        all_roles = Role.query.order_by(Role.id).all()
        data = [role.as_dict() for role in all_roles]
        return {
            "version": api_version,
            "message": "Get all roles",
            "data": data
        }, 200

    """Create a new role\n
    return {message} and {data} 
    """
    def post(self):
        if "application/json" in request.headers["Content-Type"]:
            new_role_name = request.json["new_role_name"]
            description = request.json["description"]
            label = request.json["label"]
            permission = request.json["permission"]

            exist_role = Role.query.filter_by(name=new_role_name).first()
            if exist_role:
                format_permission_list = return_permission_list(exist_role.permission)
                return {
                    "version": api_version,
                    "message": "Role {} exist in database already".format(new_role_name),
                    "data": {
                        "role": exist_role.name,
                        "description": exist_role.description,
                        "label": exist_role.label,
                        "permission": format_permission_list
                }
            }, 422

            
            new_role = Role(new_role_name, description, label, int(permission))
            db_session.add(new_role)
            db_session.commit()

            new_role = Role.query.filter_by(name=new_role_name).first()
            if description:
                new_role.description = description
            else:
                new_role.description = "A brand new role"

            if label:
                new_role.label = label
            else:
                new_role.label = new_role_name
            db_session.commit()

            updated_new_role = Role.query.filter_by(name=new_role_name).first()
            format_permission_list = return_permission_list(updated_new_role.permission)
            return {
                "version": api_version,
                "message": "Created new role: {}".format(new_role_name),
                "data": {
                    "role": updated_new_role.name,
                    "label": updated_new_role.label,
                    "description": updated_new_role.description,
                    "permission": format_permission_list
                    
                }
            }, 200
        return {
            "version": api_version,
            "message": "Check data input",
            "data": {}
        }, 404

class Roles(Resource):
    """Get details for a role\n
    return {message} and {data} 
    """
    def get(self, role_id):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        role = Role.query.filter_by(id=role_id).first()
        data = role.as_dict()
        data["permission"] = return_permission_list(role.permission)
        return {
            "version": api_version,
            "message": 'Role id: {} - {}'.format(role.id,role.label),
            "data": data
        }, 200    

    """Update details for a role\n
    return {message} and {data} 
    """
    def put(self, role_id):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        if "application/json" in request.headers["Content-Type"]:
            description = request.json.get("description")
            label = request.json.get("label")
            permission = request.json.get("permission")
            
            role = Role.query.filter_by(id=role_id).first()
            if role:
                if description is not None:
                    role.description = description
                if label is not None:
                    role.label = label
                if permission is not None:
                    role.permission = permission
                db_session.commit()
                role_updated = Role.query.filter_by(id=role_id).first()
                format_permission_list = return_permission_list(role_updated.permission)
                return {
                    "version": api_version,
                    "message":"Update {}(id: {}) info".format(role_updated.label, role_updated.id),
                    "data": {
                        "id": role_updated.id,
                        "description": role_updated.description,
                        "label": role_updated.label,
                        "render_structure": format_permission_list
                    }
                }, 200
        return {
                "version": api_version,
                "message":"Check header and data",
                "data": {}
            }, 404

class PermissonList(Resource):
    """Return a list of permissions\n
    return {message} and {data} 
    """
    def get(self):
        all_permission = Permission.query.order_by(Permission.id).all()
        data = [i.as_dict() for i in all_permission]
        return {
            "version": api_version,
            "message": "Get all permissions",
            "data": data
        }, 200

    """Add a new permission\n
    return {message} and {data} 
    """
    def post(self):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        if "application/json" in request.headers["Content-Type"]:
            item = request.json.get("item")
            page = request.json.get("page")

            check_exist = Permission.query.filter_by(item=item).first()
            if check_exist:
                return {
                    "version": api_version,
                    "message": "Permission {} exist in database already".format(item),
                    "data": {
                        "item": check_exist.item,
                        "page": check_exist.description,
                        "bit": check_exist.label
                    }
                }, 422

            last_entry = Permission.query.order_by(Permission.bit.desc()).first()
            bit = int(last_entry.bit) * 2

            new_p = Permission(
                bit = bit,
                item = item,
                page = page
            )
            db_session.add(new_p)
            db_session.commit()

            new_permission = Permission.query.order_by(Permission.bit.desc()).first()

        return {
            "version": api_version,
            "message": "Get all roles",
            "data": new_permission.as_dict()
        }, 200

class Permissions(Resource):
    """Get details for a permission\n
    return {message} and {data} 
    """
    def get(self, permission_id):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        permission = Permission.query.filter_by(id=permission_id).first()
        data = permission.as_dict()
        return {
            "version": api_version,
            "message": 'Permission id: {} - {}'.format(permission.id,permission.item),
            "data": data
        }, 200 

    """Update details for a permission\n
    return {message} and {data} 
    """
    def put(self, permission_id):
        if check_member_role(["cocospace_admin"], current_user.email) == False:
            return {
                "message": 'Missing authorization to retrieve content',
            }, 401

        if "application/json" in request.headers["Content-Type"]:
            item = request.json.get("item")
            page = request.json.get("page")
            
            permission = Permission.query.filter_by(id=permission_id).first()
            if permission:
                if item is not None:
                    permission.item = item
                if page is not None:
                    permission.page = page
                db_session.commit()
                permission_updated = Permission.query.filter_by(id=permission_id).first()
                
                return {
                    "version": api_version,
                    "message":"Update {}(id: {}) info".format(permission_updated.item, permission_updated.id),
                    "data": permission_updated.as_dict()
                }, 200
        return {
                "version": api_version,
                "message":"Check header and data",
                "data": {}
            }, 404