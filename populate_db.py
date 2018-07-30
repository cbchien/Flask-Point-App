from models import Role, User, Permission, Course, \
                UserPoint, PointType, PointLog
from database import db_session
from flask_security.utils import hash_password

def populate_db_roles():
    # Create default roles
    if not Role.query.filter_by(name='admin').first():
        role1 = Role('admin', 'View, Create, Edit', 'Admin', 1+2+4+8)
        db_session.add(role1)
    if not Role.query.filter_by(name='employee').first():
        role2 = Role('employee', 'View, Create', 'Employee', 1+2+4)
        db_session.add(role2)
    if not Role.query.filter_by(name='user').first():
        role3 = Role('user', 'Normal user', 'User', 1)
        db_session.add(role3)
    if not Role.query.filter_by(name='super_user').first():
        role4 = Role('super_user', 'Super user', 'Super user', 1+2)
        db_session.add(role4)
    db_session.commit()

def populate_db_users():
    # Create default users
    admin_role = Role.query.filter_by(name='admin').first()
    employee_role = Role.query.filter_by(name='employee').first()
    user_role = Role.query.filter_by(name='user').first()
    super_user_role = Role.query.filter_by(name='super_user').first()
    if not User.query.filter_by(unique_username='tom').first():
        user1 = User(
            email = 'tom@ggmail.com',
            unique_username = 'tom',
            password = hash_password('123456'),
            current_login_ip = '0.0.0.0',
            status = 'active',
            contact = '0912345678',
            address = '信義路一段1號',
            city = '台北市',
            categories = '家電',
            company = '獨立賣家',
            birthdate = '1980-01-01',
            gender = 'male'
        )
        admin_role.users.append(user1)
        db_session.add(user1)   
    if not User.query.filter_by(unique_username='tina').first():
        user2 = User(
            email = 'tina@ggmail.com',
            unique_username = 'tina',
            password = hash_password('123456'),
            current_login_ip = '0.0.0.0',
            status = 'active',
            contact = '0932345678',
            address = '中正一段1號',
            city = '台中市',
            categories = '服飾',
            company = '獨立賣家',
            birthdate = '1980-01-01',
            gender = 'female'
        )
        admin_role.users.append(user2)
        db_session.add(user2)
    if not User.query.filter_by(unique_username='ben').first():
        user3 = User(
            email = 'ben@ggmail.com',
            unique_username = 'ben',
            password = hash_password('123456'),
            current_login_ip = '0.0.0.0',
            status = 'active',
            contact = '0932347678',
            address = '中正一段65號',
            city = '台中市',
            categories = '3C',
            company = '獨立賣家',
            birthdate = '1980-01-01',
            level = 3,
            gender = 'male'
        )
        employee_role.users.append(user3)
        db_session.add(user3)
    if not User.query.filter_by(unique_username='bob').first():
        employee = Role.query.filter_by(name='employee').first()
        user4 = User(
            email = 'bob@ggmail.com',
            unique_username = 'bob',
            password = hash_password('123456'),
            current_login_ip = '0.0.0.0',
            status = 'active',
            contact = '0932345708',
            address = '中正一段1號',
            city = '台北市',
            categories = '服飾',
            company = '獨立賣家',
            birthdate = '1980-01-01',
            gender = 'male'
        )
        employee_role.users.append(user4)
        db_session.add(user4) 
    if not User.query.filter_by(unique_username='user_chris').first():
        employee = Role.query.filter_by(name='employee').first()
        user5 = User(
            email = 'chris@ggmail.com',
            unique_username = 'user_chris',
            password = hash_password('123456'),
            current_login_ip = '0.0.0.0',
            status = 'active',
            contact = '0932345708',
            address = '中正一段234號',
            city = '台北市',
            categories = '服飾',
            company = '獨立賣家',
            birthdate = '1985-01-01',
            gender = 'male'
        )
        user_role.users.append(user5)
        db_session.add(user5)  
    if not User.query.filter_by(unique_username='super_user_Oliver').first():
        employee = Role.query.filter_by(name='employee').first()
        user6 = User(
            email = 'oliver@ggmail.com',
            unique_username = 'super_user_Oliver',
            password = hash_password('123456'),
            current_login_ip = '0.0.0.0',
            status = 'active',
            contact = '0932345708',
            address = '中正一段5754號',
            city = '台北市',
            categories = '食品',
            company = '獨立賣家',
            birthdate = '1985-01-01',
            gender = 'male'
        )
        super_user_role.users.append(user6)
        db_session.add(user6)

    db_session.commit()

def populate_db_permission():
    # Create default role_auth
    if not Permission.query.filter_by(item='lesson_Add').first():
        p1 = Permission(
            bit = 1,
            item = "lesson_Add",
            page = "lesson"
        )
        db_session.add(p1)

    if not Permission.query.filter_by(item='lesson_Edit').first():
        p2 = Permission(
            bit = 2,
            item = "lesson_Edit",
            page = "lesson"
        )
        db_session.add(p2)

    if not Permission.query.filter_by(item='lesson_Delete').first():
        p3 = Permission(
            bit = 4,
            item = "lesson_Delete",
            page = "lesson"
        )
        db_session.add(p3)

    if not Permission.query.filter_by(item='lesson_View').first():
        p4 = Permission(
            bit = 8,
            item = "lesson_View",
            page = "lesson"
        )
        db_session.add(p4)

    if not Permission.query.filter_by(item='media_Add').first():
        p5 = Permission(
            bit = 16,
            item = "media_Add",
            page = "media"
        )
        db_session.add(p5)

    if not Permission.query.filter_by(item='media_Edit').first():
        p6 = Permission(
            bit = 32,
            item = "media_Edit",
            page = "media"
        )
        db_session.add(p6)

    if not Permission.query.filter_by(item='media_Delete').first():
        p7 = Permission(
            bit = 64,
            item = "media_Delete",
            page = "media"
        )
        db_session.add(p7)

    if not Permission.query.filter_by(item='media_View').first():
        p8 = Permission(
            bit = 128,
            item = "media_View",
            page = "media"
        )
        db_session.add(p8)

    db_session.commit()

def populate_db_courses():
    if not Course.query.filter_by(ecommerce_item_id='CRS001').first():
        course1 = Course(
            ecommerce_item_id = "CRS001",
            title = "如果操作APP",
            category = "入門",
            city = "台北市",
            head_count = 30,
            tag = "入門課程",
            description = "快速的開始使用APP",
            instructor = "APP達人",
            price = 10,
            point_price = 100,
            thumbnail_url = "https://images.pexels.com/photos/1239401/pexels-photo-1239401.jpeg?auto=compress",
            fullsize_url = "https://images.pexels.com/photos/1239401/pexels-photo-1239401.jpeg?auto=compress",
            store_url = "https://images.pexels.com/photos/1239401/pexels-photo-1239401.jpeg?auto=compress",
            created_at = "2018-07-18 12:00:10",
            status = "active",
            sale_start = "2018-07-19 12:00:10",
            sale_end = "2018-07-30 12:00:10",
            lesson_start = "2018-08-12 12:00:10",
            lesson_end = "2018-08-12 14:00:10",
            updated_at = "2018-07-18 12:00:10",
            last_updated_by = "admin"
        )
        db_session.add(course1)   
    
    if not Course.query.filter_by(ecommerce_item_id='CRS002').first():
        course2 = Course(
            ecommerce_item_id = "CRS002",
            title = "超厲害操作APP",
            category = "攝影",
            city = "台北市",
            head_count = 30,
            tag = "進階課程",
            description = "更厲害的使用APP",
            instructor = "APP達人",
            price = 10,
            point_price = 100,
            thumbnail_url = "https://images.pexels.com/photos/1239401/pexels-photo-1239401.jpeg?auto=compress",
            fullsize_url = "https://images.pexels.com/photos/1239401/pexels-photo-1239401.jpeg?auto=compress",
            store_url = "https://images.pexels.com/photos/1239401/pexels-photo-1239401.jpeg?auto=compress",
            created_at = "2018-07-18 12:00:10",
            status = "active",
            sale_start = "2018-07-19 12:00:10",
            sale_end = "2018-07-30 12:00:10",
            lesson_start = "2018-08-12 12:00:10",
            lesson_end = "2018-08-12 14:00:10",
            updated_at = "2018-07-18 12:00:10",
            last_updated_by = "admin"
        )
        db_session.add(course2)   
    
    db_session.commit()

def populate_db_points():
    if not PointType.query.filter_by(title='daily_login').first():
        point1 = PointType(
            title = "daily_login",
            description = "point for daily login",
            points = 5,
            updated_by = "tom@ggmail.com"
        )
        db_session.add(point1)   

    if not PointType.query.filter_by(title='attend_course').first():
        point2 = PointType(
            title = "attend_course",
            description = "point for attending a course",
            points = 25,
            updated_by = "tom@ggmail.com"
        )
        db_session.add(point2)

    if not PointType.query.filter_by(title='redeem_course').first():
        point2 = PointType(
            title = "redeem_course",
            description = "point for attending a course",
            points = -50,
            updated_by = "tom@ggmail.com"
        )
        db_session.add(point2)  

    db_session.commit()

def populate_db_userpoints(): 
    tom = User.query.filter_by(email='tom@ggmail.com').first()
    if not tom.user_point:
        tom_point = UserPoint(
            current_sum = 10,
            total_earned = 35,
        )
        tom.user_point = tom_point
        db_session.add(tom_point)
    
    tina = User.query.filter_by(email='tina@ggmail.com').first()
    if not tina.user_point:
        tina_point = UserPoint(
            current_sum = 60,
            total_earned = 135,
        )
        tina.user_point = tina_point
        db_session.add(tina_point)   

    bob = User.query.filter_by(email='bob@ggmail.com').first()
    if not bob.user_point:
        bob_point = UserPoint(
            current_sum = 30,
            total_earned = 499,
        )
        bob.user_point = bob_point
        db_session.add(bob_point)

    ben = User.query.filter_by(email='ben@ggmail.com').first()
    if not ben.user_point:
        ben_point = UserPoint(
            current_sum = 40,
            total_earned = 700,
        )
        ben.user_point = ben_point
        db_session.add(ben_point) 
    
    db_session.commit()