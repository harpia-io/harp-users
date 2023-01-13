import traceback
from microservice_template_core import db
import datetime
import json
from marshmallow import Schema, fields, validate
from microservice_template_core.tools.logger import get_logger
from flask_jwt_extended import create_access_token, create_refresh_token
import harp_users.settings as settings
from sqlalchemy.sql import func
from passlib.hash import pbkdf2_sha256 as sha256

logger = get_logger()


class Users(db.Model):
    __tablename__ = 'harp_users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.VARCHAR(70), nullable=True, unique=False)
    second_name = db.Column(db.VARCHAR(70), nullable=True, unique=False)
    username = db.Column(db.VARCHAR(70), nullable=True, unique=True)
    email = db.Column(db.String(120), unique=False, nullable=False)
    role = db.Column(db.VARCHAR(70), nullable=False, unique=False)
    phone = db.Column(db.VARCHAR(70), nullable=True, unique=False)
    active_environment_ids = db.Column(db.Text(4294000000), default='{}')
    status = db.Column(db.VARCHAR(70), nullable=True, unique=False)
    password = db.Column(db.VARCHAR(120), nullable=True, unique=False)
    token = db.Column(db.VARCHAR(70), nullable=True, unique=False)
    create_ts = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow(), nullable=False)
    last_update_ts = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow(), nullable=False)
    last_login_ts = db.Column(db.DateTime, default=func.now())

    def __repr__(self):
        return f"{self.user_id}_{self.username}"

    def dict(self):
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'second_name': self.second_name,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'active_environment_ids': json.loads(self.active_environment_ids),
            'status': self.status,
            'password': self.password,
            'token': self.token,
            'create_ts': self.create_ts,
            'last_update_ts': self.last_update_ts,
            'last_login_ts': self.last_login_ts
        }

    def user_info_dict(self):
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'second_name': self.second_name,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'active_environment_ids': json.loads(self.active_environment_ids),
            'status': self.status
        }

    def user_password_reset(self):
        return {
            'email': self.email,
            'token': self.token,
            'username': self.username
        }

    @classmethod
    def get_all_users(cls):
        get_all_users = cls.query.filter_by().all()
        all_users = [single_event.user_info_dict() for single_event in get_all_users]

        return all_users

    @classmethod
    def get_user_info(cls, user_id: int):
        get_all_users = cls.query.filter_by(user_id=user_id).all()
        all_users = [single_event.user_info_dict() for single_event in get_all_users][0]

        return all_users

    @classmethod
    def get_user_info_by_name(cls, username: str):
        get_all_users = cls.query.filter_by(username=username).all()
        all_users = [single_event.user_info_dict() for single_event in get_all_users][0]

        return all_users

    @classmethod
    def get_user_info_by_id(cls, user_id: int):
        get_all_users = cls.query.filter_by(user_id=user_id).all()
        all_users = [single_event.user_info_dict() for single_event in get_all_users][0]

        return all_users

    @classmethod
    def confirm_invite(cls, data: dict):
        token = data['token']
        email = data['email']
        invite_pending = cls.query.filter_by(email=email, token=token, status='pending').one_or_none()
        invite_closed = cls.query.filter_by(email=email, token=token, status='active').one_or_none()
        invite_all = cls.query.filter_by(email=email, token=token).one_or_none()

        if invite_all is None:
            return f'No invites for {email}', 601

        if invite_closed:
            return f'Email: {email} was already confirmed. Need to login', 602

        if invite_pending:
            data['status'] = 'active'
            data['password'] = cls.generate_hash(data['password'])
            cls.query.filter_by(email=email, token=token).update(data)
            db.session.commit()
            return f'Email: {email} was confirmed', 200

    @classmethod
    def confirm_password(cls, data: dict):
        token = data['token']

        user = cls.query.filter_by(username=data['username']).one_or_none()
        if user is None:
            return f"User: {data['username']} - not present", 404

        user_token = cls.query.filter_by(username=data['username'], token=token).one_or_none()
        if user_token is None:
            return f'User token is not the same in Invite and in DB. Pass was not changed', 401

        new_password = cls.generate_hash(data['password'])
        cls.query.filter_by(username=data['username']).update({"password": new_password})
        db.session.commit()

        logger.info(msg=f"User data has been update - {data}")

        return f"Password for user - {data['username']} has been changed", 200

    @classmethod
    def add(cls, data, status, token=None):
        exist_username = cls.query.filter_by(username=data['username']).one_or_none()
        exist_email = cls.query.filter_by(username=data['email']).one_or_none()
        if exist_username:
            raise ValueError(f"Username: {data['username']} already exist")
        if exist_email:
            raise ValueError(f"Email: {data['email']} already exist")

        new_obj = Users(
            first_name=data['username'],
            email=data['email'],
            role=data['role'],
            active_environment_ids=json.dumps(data['active_environment_ids']),
            status=status,
            token=token
        )
        new_obj = new_obj.save()
        return new_obj

    @classmethod
    def create_user(cls, data):
        exist_username = cls.query.filter_by(username=data['username']).one_or_none()
        exist_email = cls.query.filter_by(username=data['email']).one_or_none()
        if exist_username:
            raise ValueError(f"Username: {data['username']} already exist")
        if exist_email:
            raise ValueError(f"Email: {data['email']} already exist")

        new_obj = Users(
            first_name=data['first_name'],
            second_name=data['second_name'],
            username=data['username'],
            email=data['email'],
            role=data['role'],
            active_environment_ids=json.dumps(data['active_environment_ids']),
            phone=data['phone'],
            status=data['status'],
            password=cls.generate_hash(data['password'])
        )
        new_obj = new_obj.save()
        return new_obj

    def save(self):
        try:
            db.session.add(self)
            db.session.flush()
            db.session.commit()

            return self
        except Exception as exc:
            logger.critical(
                msg=f"Can't commit changes to DB \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}}
            )
            db.session.rollback()

    def delete_obj(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def generate_hash(cls, password):
        """
        generate hash from password by encryption using sha256
        """
        return sha256.hash(password)

    @classmethod
    def verify_hash(cls, password, hash_):
        """
        Verify hash and password
        """
        return sha256.verify(password, hash_)

    @classmethod
    def update_password(cls, username, current_password, new_password):
        user = cls.query.filter_by(username=username).one_or_none()

        if user is None:
            raise UserWarning(f"User: {username} - not present")

        if cls.verify_hash(password=current_password, hash_=user.password) is False:
            raise PermissionError('Wrong current password')

        password = {'password': cls.generate_hash(new_password)}

        cls.query.filter_by(username=username).update(password)

        return f'Password for user: {user.username} has been changed'

    @classmethod
    def authenticate(cls, password, username=None, email=None):
        if username:
            user = cls.query.filter_by(username=username).one_or_none()
            if user is None:
                raise UserWarning(f"User: {username} - not present")

            if user.status == 'blocked':
                raise UserWarning(f"User: {username} - was blocked by admin")

            if user.status == 'pending':
                raise UserWarning(f"User: {username} - should accept invite in mail box")

        else:
            user = cls.query.filter_by(email=email).one_or_none()
            if user is None:
                raise UserWarning(f"Email: {email} - not present")

            if user.status == 'blocked':
                raise UserWarning(f"User: {username} - was blocked by admin")

            if user.status == 'pending':
                raise UserWarning(f"User: {username} - should accept invite in mail box")

        if cls.verify_hash(password=password, hash_=user.password) is False:
            raise PermissionError('Wrong password')

        expires = datetime.timedelta(hours=int(settings.TOKEN_EXPIRE_HOURS))
        access_token = create_access_token(identity=user.username, expires_delta=expires)
        refresh_token = create_refresh_token(identity=user.username, expires_delta=expires)
        logger.info(msg=f"User login: {user.username}", extra={"event_name": "User login", "class_name": cls.__name__})
        user.last_login_ts = func.now()
        db.session.commit()

        result = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

        return user.user_id, result

    @classmethod
    def obj_exist(cls, user_id=None, username=None, email=None):
        if user_id:
            return cls.query.filter_by(user_id=user_id).one_or_none()
        if username:
            return cls.query.filter_by(username=username).one_or_none()
        if email:
            return cls.query.filter_by(email=email).one_or_none()

    def update_existing_profile(self, data, username=None, user_id=None):
        if 'active_environment_ids' in data:
            data['active_environment_ids'] = json.dumps(data['active_environment_ids'])

        if username:
            self.query.filter_by(username=username).update(data)
        if user_id:
            self.query.filter_by(user_id=user_id).update(data)

        db.session.commit()

    def block_user(self, user_id):
        data = {'status': 'blocked'}

        self.query.filter_by(user_id=user_id).update(data)

        db.session.commit()


class UsersSchema(Schema):
    user_id = fields.Int(dump_only=True)
    first_name = fields.Str(required=False)
    second_name = fields.Str(required=False)
    username = fields.Str(required=False)
    email = fields.Email(required=True)
    role = fields.Str(required=True, validate=validate.OneOf(["admin", "user"]))
    phone = fields.Str(required=False)
    status = fields.Str(required=False)
    password = fields.Str(required=False)
    token = fields.Str(required=False)
    active_environment_ids = fields.Dict(required=True)
    create_ts = fields.DateTime("%Y-%m-%d %H:%M:%S", dump_only=True)
    last_update_ts = fields.DateTime("%Y-%m-%d %H:%M:%S", dump_only=True)
    last_login_ts = fields.DateTime("%Y-%m-%d %H:%M:%S", dump_only=True)
