import os, re
from flask import Flask, json, request, jsonify, render_template, send_from_directory, url_for, session, redirect, url_for
from flask_security import Security, login_required, roles_required, roles_accepted, SQLAlchemySessionUserDatastore, current_user
from flask_login import LoginManager
from flask_security.utils import hash_password
from flask_restful import Api
from db_pool import PooledDB
from database import db_session, init_db, Client
from models import User, Role, Logging
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from populate_db import populate_db_roles, populate_db_users, \
                    populate_db_permission, populate_db_courses, \
                    populate_db_points, populate_db_userpoints

# Create app
app = Flask(__name__, static_folder="./client/static", template_folder="./client")
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "super-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@localhost/localwarehouse"
app.config["SQLALCHEMY_BINDS "] = {
    "warehouse_tw": "mysql://brianchien:V99PlgLd9RVh9RxV@10.4.211.50/warehouse_tw"
}
app.config["SECURITY_PASSWORD_HASH"] = "pbkdf2_sha512"
app.config["SECURITY_PASSWORD_SALT"] = "wwefafvbdmyumdhngfrdefrthyjukmi"
app.config["SECURITY_LOGIN_URL"] = "/flask-login"
#app.config["WTF_CSRF_ENABLED"] = False
app.config["OAUTHLIB_INSECURE_TRANSPORT"] = 1

# Set up social secrets
google_blueprint = make_google_blueprint(
    client_id="800990402749-mof20bpb44v2jdd9775hs69gdatk646m.apps.googleusercontent.com",
    client_secret="lyrN7U1SGHZYt3s6m0ynLaZ7",
    scope=["profile", "email"]
)
app.register_blueprint(google_blueprint, url_prefix="/google_login")

facebook_blueprint = make_facebook_blueprint(
    client_id="",
    client_secret="",
    scope=["profile", "email"],
)
app.register_blueprint(facebook_blueprint, url_prefix="/facebook_login")


# post login page is set to a hypothetical profile page instead of Flask-Security’s default of the root index
app.config['SECURITY_POST_LOGIN'] = '/profile'

# Set up flask restful
api = Api(app)
api_version = 0.1

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore)

# Set up pooled database connection client
client=Client()

# Logging feature
from time import strftime
from logging.handlers import RotatingFileHandler
import logging
import traceback
handler = RotatingFileHandler('app.log', maxBytes=50000, backupCount=3, encoding='utf8')
logger = logging.getLogger('werkzeug')
# getLogger(__name__): decorators loggers to file + werkzeug loggers to stdout
# getLogger('werkzeug'): decorators loggers to file + nothing to stdout
logger.setLevel(logging.ERROR)
logger.addHandler(handler)

# Create a user to test with
@app.before_first_request
def create_users_and_roles():
    init_db()
    populate_db_roles()
    populate_db_users()
    populate_db_permission()
    populate_db_courses()
    populate_db_points()
    populate_db_userpoints()

@app.login_manager.unauthorized_handler
def unauth_handler():
    return jsonify(success=False,
                   data={'login_required': True},
                   message='Authorization required to access this page'), 401

@app.after_request
def after_request(response):
    """ Logging after every request. """
    # 500 is logged via @app.errorhandler.
    if response.status_code != 500:
        timestamp = strftime('[%Y-%b-%d %H:%M]')
        try:
            message = response.json.get('message')
        except:
            if response.status_code > 499:
                message = 'Server error'
            elif response.status_code > 399:
                message = 'Client error'
            else:
                message = 'Undefined message'
        try:
            email = current_user.email
        except:
            email = 'AnonymousUser'

        # filter out /static/ and index.html requests 
        regexp = re.compile(r'(static)|(index.html)|(debugger)')
        if not regexp.search(request.full_path):
            # print('\n', "session after request", request.full_path, session)
            logger.error('%s, %s, %s, %s, %s, %s, %s, %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status, email, message)
            new_log = Logging(email, request.remote_addr, request.method, request.scheme, request.full_path, response.status, message)
            db_session.add(new_log)
            db_session.commit()
    return response

# @app.errorhandler(Exception)
# def exceptions(e):
#     """ Logging after every Exception. """
#     timestamp = strftime('[%Y-%b-%d %H:%M]')
#     trace = traceback.format_exc()
#     try:
#         email = current_user.email
#     except:
#         email = 'AnonymousUser'
#     logger.error('%s, %s, %s, %s, %s, %s, %s, %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, '500', email, trace)
#     new_log = Logging(email, request.remote_addr, request.method, request.scheme, request.full_path, '500', 'Server Error')
#     db_session.add(new_log)
#     db_session.commit()
#     return traceback, 500

@app.route("/spec")
def spec():
    return jsonify(swagger(app))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'client'),
                               'favicon.ico', mimetype='image/x-icon')

@app.route('/service-worker.js')
def service_worker_js():
    return send_from_directory(os.path.join(app.root_path, 'client'),
                               'service-worker.js')

@app.route('/profile')
def profile():
    return render_template(
        'profile.html',
        content='Profile Page')

@app.route("/google")
def google_index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    return "You are {email} on Google".format(email=resp.json()["email"])

# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def catch_all(path):
#     return render_template("index.html")

@app.route("/login")
def login():
    return render_template("index.html")

# List of APIs
from api import roleresources, userresources, pointresources, courseresources

api.add_resource(roleresources.Roles, '/api/roles/<int:role_id>') #[GET, PUT]
api.add_resource(roleresources.RoleList, '/api/roles') #[GET, POST]
api.add_resource(roleresources.Permissions, '/api/permission/<int:permission_id>') #[GET, PUT]
api.add_resource(roleresources.PermissonList, '/api/permission') #[GET, POST]

api.add_resource(userresources.Member, '/api/members/<int:member_id>')  #[GET, PUT]
api.add_resource(userresources.MemberList, '/api/members') #[GET, POST]
api.add_resource(userresources.MemberChangePassword, '/api/members/changepassword') #[POST]
api.add_resource(userresources.MemberLogin, '/api/userlogin') #[POST]
api.add_resource(userresources.MemberLogout, '/api/userlogout') #[POST]

api.add_resource(userresources.OpsHistory, '/api/opshistory/<int:member_id>')  #[GET]
api.add_resource(userresources.OpsHistoryList, '/api/opshistory')  #[GET]

api.add_resource(pointresources.UserPointUser, '/api/point', #[GET]
                                        '/api/point/<int:point_id>') #[POST]
api.add_resource(pointresources.UserPointAdmin, '/api/admin/point/<int:user_id>', #[GET]
                                            '/api/admin/point/<int:user_id>/<int:point_id>') #[POST]                            
api.add_resource(pointresources.PointTypeAdmin, '/api/admin/pointtype/<int:point_id>') #[GET, PUT]
api.add_resource(pointresources.PointTypeListAdmin, '/api/admin/pointtype') #[GET, POST]
api.add_resource(pointresources.PointLogAdmin, '/api/admin/pointlog/<int:user_id>') #[GET]

api.add_resource(courseresources.CoursesList, '/api/courses') #[GET, POST]
api.add_resource(courseresources.CoursesFilterList, '/api/courses/<string:months>') #[GET]
api.add_resource(courseresources.Courses, '/api/courses/<string:cocospace_item_id>') #[GET, POST]

if __name__ == "__main__":
    app.run(port=5000)
