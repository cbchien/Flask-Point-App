from flask_security import current_user
from app import user_datastore, client
import datetime

def check_member_role(role, email):
    """Check a member's viewing authorization.
    return Boolean
    
    :param roles: A list of acceptable roles
    :param email: Email of the person who will perform the action
    """
    required_roles = role
    user_role = user_datastore.find_user(email=email).role
    if user_role.name in required_roles:
        return True
    return False

def return_permission_list_for_user(user_id):
    """
    Return a list of permissions base on user id.
    User id will be joined with permission table to perform Bitwise operator
    :param user_id: user id 
    """
    try:
        query = """
            SELECT permission.item
            FROM user 
            LEFT JOIN permission 
            ON (SELECT permission 
                FROM role 
                LEFT JOIN user 
                ON user.role_id = role.id 
                WHERE user.id = {}
            ) & permission.bit 
            WHERE user.id = {};
        """.format(user_id, user_id)
        user_permission = client._requests(query)
        format_permission = []
        for i in user_permission["data"]:
            format_permission.append(i["item"])
    except:
        format_permission = "server error"
    return format_permission

def return_permission_list(bit_sum):
    """
    Return a list of permissions. Input a bit sum for permission Bitwise operator.
    :param bit_sum: a bit sum representing permission from permission table
    """
    try:
        query = """
            SELECT distinct 
	            permission.item,
	            permission.bit
            FROM user 
            LEFT JOIN permission 
            ON {} & permission.bit;
        """.format(bit_sum)
        user_permission = client._requests(query)
        format_permission = []
        for i in user_permission["data"]:
            format_permission.append(i["item"])
    except:
        format_permission = "server error"
    return format_permission