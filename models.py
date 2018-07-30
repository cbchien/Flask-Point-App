import datetime, json
from database import Base, JsonEncodedDict
from flask_security import UserMixin, RoleMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                       String, ForeignKey, Text, VARCHAR, TIMESTAMP
from sqlalchemy.types import JSON, ARRAY
from werkzeug.security import generate_password_hash, check_password_hash

# Table to store all roles
class Role(Base, RoleMixin):
    __tablename__ = 'role'
    __table_args__ = {'extend_existing': True} 
    id = Column(Integer(), primary_key=True)
    name = Column(String(45), unique=True)
    description = Column(String(255))
    label = Column(String(255))
    permission = Column(Integer())
    users = relationship('User', backref='user_roles', lazy='dynamic')

    def __init__(self, name, description, label, permission):
        self.name = name
        self.description = description
        self.label = label
        self.permission = permission

    def __repr__(self):
        return '%r' %(self.id)
    
    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return data

# Table to store all roles' viewing authorities
# Bitwise operator roles and permission system
# >>1	00000001         >> 8	00001000
# >>2	00000010         >>16	00010000
# >>4	00000100         >>32	00100000
# The & operator compares each binary digit of two integers and returns a new integer
# with a 1 wherever both numbers had a 1 and a 0 anywhere else. 
# 7	    00000111  return 1, 2, and 4
# 23    00010111  return 1, 2, 4, and 16
# 33    00100001  return 1 and 128
# http://sforsuresh.in/implemention-of-user-permission-with-php-mysql-bitwise-operators/   
class Permission(Base):
    __tablename__ = 'permission'
    __table_args__ = {'extend_existing': True} 
    id = Column(Integer(), primary_key=True)
    bit = Column(Integer())
    item = Column(VARCHAR(100))
    page = Column(VARCHAR(100))

    def __init__(self, **kwargs):
        vars(self).update(kwargs)

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return data

# Table for user. user id is used throughout the app for primary key     
class User(Base, UserMixin):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True} 
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    unique_username = Column(VARCHAR(255))
    password = Column(String(255))
    last_login_at = Column(DateTime(), default=datetime.datetime.now())
    current_login_at = Column(DateTime(), default=datetime.datetime.now())
    last_login_ip = Column(String(100), default='0.0.0.0')
    current_login_ip = Column(String(100))
    login_count = Column(Integer, default=1)
    status = Column(VARCHAR(30), default='pending')
    contact = Column(VARCHAR(255))
    address = Column(VARCHAR(255))
    city = Column(VARCHAR(10))
    categories = Column(VARCHAR(255))
    company = Column(String(255)) # The compnay the member works for 
    confirmed_at = Column(DateTime(), default=datetime.datetime.now()) # Saved for future Approval functionality
    birthdate = Column(DateTime())
    gender = Column(VARCHAR(20))
    level = Column(Integer, default=1)
    access_token = Column(VARCHAR(255)) # Oauth access token
    profile_url = Column(VARCHAR(512)) # Save user profile url from Google or Facebook
    register_method = Column(VARCHAR(255)) # Local, Google, Facebook, etc..
    external_user_id = Column(VARCHAR(255)) # Save user id from Google or Facebook
    role_id = Column(Integer(), ForeignKey('role.id'))
    role = relationship("Role")
    user_point = relationship("UserPoint", uselist=False, back_populates="user")
    point_log = relationship("PointLog", back_populates="user", lazy='dynamic')

    def __init__(self, **kwargs):
        vars(self).update(kwargs)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        del(data["password"])
        del(data["role_id"])
        data["confirmed_at"] = str(data["confirmed_at"])
        data["last_login_at"] = str(data["last_login_at"])
        data["current_login_at"] = str(data["current_login_at"])
        data["birthdate"] = str(data["birthdate"])
        data["role"] = self.role.name

        return data

# Table One-to-One relationship to User table to store all points related information
class UserPoint(Base):
    __tablename__ = 'user_point'
    __table_args__ = {'extend_existing': True} 
    id = Column(Integer, primary_key=True)
    current_sum = Column(Integer()) # Store current displayed points
    total_earned = Column(Integer()) # Store lifetime earned points, for calculating user level
    updated_at = Column(DateTime(), default=datetime.datetime.now())
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="user_point")

    def __init__(self, **kwargs):
        vars(self).update(kwargs)

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["updated_at"] = str(data["updated_at"])
        return data

# Table to store all point history
class PointLog(Base):
    __tablename__ = 'point_log'
    id = Column(Integer, primary_key=True)
    entry_type = Column(VARCHAR(255)) # Credit, Update, Redeem, Fix, etc...
    description = Column(VARCHAR(255)) # action description
    action_points = Column(Integer()) # store points that took place during the action
    total_points = Column(Integer()) # store total points at the end of the action
    timestamp = Column(DateTime(), default=datetime.datetime.now())
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="point_log")
    point_type_id = Column(Integer, ForeignKey('point_type.id'))
    point_type = relationship("PointType", back_populates="point_log")

    def __init__(self, **kwargs):
        vars(self).update(kwargs)

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["timestamp"] = str(data["timestamp"])
        return data

# Table to store all point types
class PointType(Base):
    __tablename__ = 'point_type'
    id = Column(Integer, primary_key=True)
    title = Column(VARCHAR(255))
    description = Column(VARCHAR(255)) # description
    points = Column(Integer()) # store points for this entry action
    updated_at = Column(DateTime(), default=datetime.datetime.now())
    updated_by = VARCHAR(255) # store user that last modified the entry
    status = VARCHAR(255)
    point_log = relationship("PointLog", back_populates="point_type")

    def __init__(self, **kwargs):
        vars(self).update(kwargs)

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["updated_at"] = str(data["updated_at"])
        return data

# Table to store all api actions
class Logging(Base):
    __tablename__ = 'logging'
    id = Column(Integer, primary_key=True)
    email = Column(String(255))
    request_remote_addr = Column(String(255))
    method = Column(String(255))
    scheme = Column(String(255))
    full_path = Column(String(100))
    res_status = Column(String(100))
    message = Column(String(255))
    timestamp = Column(DateTime(), default=datetime.datetime.now())

    def __init__(self, email, request_remote_addr, method, scheme, full_path, res_status, message):
        self.email = email
        self.request_remote_addr = request_remote_addr
        self.method = method
        self.scheme = scheme
        self.full_path = full_path
        self.res_status = res_status
        self.message = message

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["timestamp"] = str(data["timestamp"])
        return data

    def __repr__(self):
        return '%r %r %r %r %r' %(self.request_remote_addr, self.method, self.scheme, self.full_path, self.status)

# Table to store lessons information from ecommerce store
class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)  # 課程編號
    ecommerce_item_id = Column(String(255))    # 商品編號
    title = Column(String(255))             # 課程名稱
    category = Column(String(30))           # 課程類別 (行銷, 美編, ...)
    city = Column(String(30))               # 地區
    head_count = Column(Integer())          # 名額
    tag = Column(String(255))               # 課程深度 (入門課程, 進階, 高階)
    description = Column(String(255))       # 簡介
    instructor = Column(String(255))        # 教師
    price = Column(Integer())               # 價格
    point_price = Column(Integer())         # 積分價格
    thumbnail_url = Column(String(255))     # 上架圖片
    fullsize_url = Column(String(255))      # 詳細資訊圖片
    store_url = Column(String(255))         # 賣場連結
    created_at = Column(DateTime(), default=datetime.datetime.now()) # 上架時間
    inactive_at = Column(DateTime())        # 下架時間
    status = Column(String(255))            # 顯示狀態
    sale_start = Column(DateTime())         # 開賣時間
    sale_end = Column(DateTime())           # 停賣時間
    lesson_start = Column(DateTime())       # 課程開始時間 1900-MM-DD HH:MM:SS
    lesson_end = Column(DateTime())         # 課程結束時間 1900-MM-DD HH:MM:SS
    updated_at = Column(DateTime())         # 最後更新時間
    last_updated_by = Column(String(255))   # 最後更新人

    def __init__(self, **kwargs):
        vars(self).update(kwargs)

    def as_dict(self):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data["created_at"] = str(data["created_at"])
        data["inactive_at"] = str(data["inactive_at"])
        data["sale_start"] = str(data["sale_start"])
        data["sale_end"] = str(data["sale_end"])
        data["lesson_start"] = str(data["lesson_start"])
        data["lesson_end"] = str(data["lesson_end"])
        data["updated_at"] = str(data["updated_at"])
        return data