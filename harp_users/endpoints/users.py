from microservice_template_core.tools.flask_restplus import api
from flask_restx import Resource
from harp_users.models.users import Users, UsersSchema
import traceback
from microservice_template_core.tools.logger import get_logger
from flask import request
from harp_users.logic.token import generate_confirmation_token
from harp_users.logic.email_confirmation import CreateEmail
from harp_users.logic.email_pass_reset import PasswordResetEmail
from microservice_template_core.decorators.auth_decorator import token_required
from werkzeug.exceptions import NotFound, BadRequest
from harp_users.logic.token import get_user_id_by_token
from marshmallow import ValidationError
from harp_users.logic.user_environments import UserEnvironments
from harp_users.logic.process_new_envs import ProcessNewEnvs

logger = get_logger()
ns = api.namespace('api/v1/users', description='Harp users endpoints')
users = UsersSchema()


@ns.route('/reset-password-username/<username>')
class ResetPasswordByUsername(Resource):
    @api.response(200, 'Invite to reset password has been sent')
    @api.response(500, 'Unexpected error on backend side')
    def post(self, username):
        """
        Invite to reset password
        Use this method to sent invite for password reset
        """
        try:
            obj = Users.obj_exist(username=username).user_password_reset()
            if obj is None:
                return f"User: {username} is not exist", 404

            user_invite = PasswordResetEmail(recipient_name=obj['email'], token=obj['token'], username=username)
            user_invite.create_email()
            logger.info(msg=f"Sent email confirmation to reset password for user - {username}")

            return {"status": "Confirmation email to reset password has been sent"}, 200
        except ValueError as val_exc:
            logger.warning(msg=str(val_exc))
            return {"msg": f"Exception raised: {str(val_exc)}"}, 400
        except Exception as exc:
            logger.critical(msg=f"General exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}")
            return {'msg': 'Exception raised. Check logs for additional info'}, 500


@ns.route('/reset-password-email/<email>')
class ResetPasswordByEmail(Resource):
    @api.response(200, 'Invite to reset password has been sent')
    @api.response(500, 'Unexpected error on backend side')
    def post(self, email):
        """
        Invite to reset password
        Use this method to sent invite for password reset
        """
        try:
            obj = Users.obj_exist(email=email).user_password_reset()
            if obj is None:
                return f"Email: {email} is not exist", 404

            user_invite = PasswordResetEmail(recipient_name=obj['email'], token=obj['token'], username=obj['username'])
            user_invite.create_email()
            logger.info(msg=f"Sent email confirmation to reset password for user - {obj['username']}")

            return {"status": "Confirmation email to reset password has been sent"}, 200
        except ValueError as val_exc:
            logger.warning(msg=str(val_exc))
            return {"msg": f"Exception raised: {str(val_exc)}"}, 400
        except Exception as exc:
            logger.critical(msg=f"General exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}")
            return {'msg': 'Exception raised. Check logs for additional info'}, 500


@ns.route('/reset-password/confirm')
class ConfirmInvite(Resource):
    @staticmethod
    @api.response(200, 'Password has been changed')
    def post():
        """
        Confirm password change
        Use this method to confirm password change.
        * Send a JSON object
        ```
            {
                "username": "nkondratyk",
                "token": "some token",
                "password": "some_pass"
            }
        ```
        """
        data = request.json
        new_obj = Users.confirm_password(data=data)

        return new_obj


@ns.route('/invite')
class CreateInvite(Resource):
    @api.response(200, 'Invite has been sent')
    @api.response(400, 'User already exist')
    @api.response(500, 'Unexpected error on backend side')
    def post(self):
        """
        Invite new user to Harp
        Use this method to invite new user to Harp.
        * Send a JSON object
        ```
            {
                "email": "nkondratyk93@gmail.com",
                "username": "Nick"
                "role": "admin",
                "active_environment_ids": {
                    "visible_only": [],
                    "hidden": []
                }
            }
        ```
        """
        try:
            data = users.load(request.get_json())
            token = generate_confirmation_token(data['email'])
            new_obj = Users.add(data, status='pending', token=token)
            result = users.dump(new_obj.dict())
        except ValueError as val_exc:
            logger.warning(
                msg=str(val_exc),
                extra={'tags': {}})
            return {"msg": str(val_exc)}, 400
        except Exception as exc:
            logger.critical(
                msg=f"General exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': 'Exception raised. Check logs for additional info'}, 500

        logger.info(msg=f"User has been added - {result}")

        user_invite = CreateEmail(recipient_name=data['email'], token=token, username=data['username'])
        user_invite.create_email()

        return result, 200


@ns.route('/invite/confirm')
class ConfirmInvite(Resource):
    @staticmethod
    @api.response(200, 'Invite has been sent')
    @api.response(601, 'No active invites for current user')
    @api.response(602, 'Email was already confirmed. User can login')
    def post():
        """
        Confirm invite
        Use this method to confirm invite.
        * Send a JSON object
        ```
            {
                "first_name": "Niko",
                "second_name": "Kondr",
                "username": "nkondratyk",
                "email": "some@gmail.com",
                "token": "some token",
                "password": "some_pass"
            }
        ```
        """
        data = request.json
        new_obj = Users.confirm_invite(data=data)

        return new_obj


@ns.route('/info/<user_id>')
class UserInfoByID(Resource):
    @staticmethod
    @api.response(200, 'Info has been collected')
    @api.response(404, 'User not found')
    @token_required()
    def get(user_id):
        """
        Get info about specific user by ID
        Use this method to get info about specific user
        """
        try:
            new_obj = Users.get_user_info(user_id=user_id)
            result = new_obj
        except IndexError:
            return {'status': f'User ID {user_id} not found'}, 404

        return result, 200


@ns.route('/info')
class UserInfoByToken(Resource):
    @staticmethod
    @api.response(200, 'Info has been collected')
    @api.response(404, 'User not found')
    @token_required()
    def get():
        """
        Get info about specific user by Token
        Use this method to get info about specific user
        """

        auth_token = request.headers.get('AuthToken')
        username = get_user_id_by_token(auth_token)

        if isinstance(username, str):
            try:
                new_obj = Users.get_user_info_by_name(username=username)
                result = new_obj
            except IndexError:
                return {'status': f'User ID {username} not found'}, 404

            return result, 200
        else:
            return username


@ns.route('/user-info/<username>')
class UserInfoByToken(Resource):
    @staticmethod
    @api.response(200, 'Info has been collected')
    @api.response(404, 'User not found')
    def get(username):
        """
        Get info about specific user by username
        Use this method to get info about specific user
        """

        if isinstance(username, str):
            try:
                new_obj = Users.get_user_info_by_name(username=username)
                result = new_obj
            except IndexError:
                return {'status': f'User ID {username} not found'}, 404

            return result, 200
        else:
            return username


@ns.route('/user-info-by-id/<user_id>')
class UserInfoByUserID(Resource):
    @staticmethod
    @api.response(200, 'Info has been collected')
    @api.response(404, 'User not found')
    def get(user_id):
        """
        Get info about specific user by user_id
        Use this method to get info about specific user
        """

        try:
            new_obj = Users.get_user_info_by_id(user_id=user_id)
            result = new_obj
        except IndexError:
            return {'status': f'User ID {user_id} not found'}, 404

        return result, 200


@ns.route('/user-exist')
class UserExist(Resource):
    # TODO Add auth by token in URL or Body
    @staticmethod
    @api.response(500, 'Unexpected error on backend side')
    # @token_required()
    def post():
        """
        Check if user exist
        Use this method to check if user exist
        * Send a JSON object
        ```
            {"username": "some_name"}
        ```
        """
        data = request.get_json()

        obj = Users.obj_exist(username=data['username'])

        if obj:
            return {"user_exist": True}, 200
        else:
            return {"user_exist": False}, 200


@ns.route('/user-email-exist/<user_email>')
class UserEmailExist(Resource):
    @staticmethod
    @api.response(200, 'User exist')
    @api.response(404, 'User is not exist')
    @api.response(500, 'Unexpected error on backend side')
    def get(user_email):
        """
        Check if user exist
        Use this method to check if user exist
        """
        obj = Users.obj_exist(email=user_email)

        if obj:
            return {"user_exist": True}, 200
        else:
            return {"user_exist": False}, 200


@ns.route('/profile')
class UserProfile(Resource):
    @staticmethod
    @api.response(200, 'Profile has been update')
    @api.response(500, 'Unexpected error on backend side')
    @token_required()
    def post():
        """
        Update existing user profile
        Use this method to update existing user profile
        * Send a JSON object
        ```
            {
                "first_name": "Name",
                "second_name": "Second",
                "email": "name@gmail.com",
                "phone": "686326",
                "active_environment_ids": {
                    "visible_only": [],
                    "hidden": []
                },
            }
        ```
        """
        data = request.get_json()

        auth_token = request.headers.get('AuthToken')
        username = get_user_id_by_token(auth_token)

        obj = Users.obj_exist(username=username)

        if not obj:
            raise NotFound(f'Profile with specified user name is not exist: {username}')
        try:
            if 'active_environment_ids' in data:
                data['active_environment_ids']['visible_only'] = [int(x) for x in data['active_environment_ids']['visible_only']]
                data['active_environment_ids']['hidden'] = [int(x) for x in data['active_environment_ids']['hidden']]

            # Write to MySQL
            obj.update_existing_profile(username=username, data=data)
            result = users.dump(obj.dict())
        except ValueError as val_exc:
            logger.warning(
                msg=f"User Profile updating exception \nException: {str(val_exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {"msg": str(val_exc)}, 400
        except BadRequest as bad_request:
            logger.warning(
                msg=f"User Profile updating exception \nException: {str(bad_request)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': str(bad_request)}, 400
        except Exception as exc:
            logger.critical(
                msg=f"User Profile updating exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': 'Exception raised. Check logs for additional info'}, 500
        return result, 200


@ns.route('/profile/<user_id>')
class UserProfileByID(Resource):
    @staticmethod
    @api.response(200, 'Profile has been update')
    @api.response(500, 'Unexpected error on backend side')
    @token_required()
    def post(user_id):
        """
        Update existing user profile by USER ID
        Use this method to update existing user profile
        * Send a JSON object
        ```
            {
                "first_name": "Name",
                "second_name": "Second",
                "email": "name@gmail.com",
                "phone": "686326",
                "active_environment_ids": {
                    "visible_only": [],
                    "hidden": []
                },
            }
        ```
        """
        data = request.get_json()

        obj = Users.obj_exist(user_id=user_id)

        if not obj:
            raise NotFound(f'Profile with specified user id is not exist: {user_id}')
        try:
            if 'active_environment_ids' in data:
                data['active_environment_ids']['visible_only'] = [int(x) for x in data['active_environment_ids']['visible_only']]
                data['active_environment_ids']['hidden'] = [int(x) for x in data['active_environment_ids']['hidden']]

            obj.update_existing_profile(user_id=user_id, data=data)
            result = users.dump(obj.dict())
        except ValueError as val_exc:
            logger.warning(
                msg=f"User Profile updating exception \nException: {str(val_exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {"msg": str(val_exc)}, 400
        except BadRequest as bad_request:
            logger.warning(
                msg=f"User Profile updating exception \nException: {str(bad_request)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': str(bad_request)}, 400
        except Exception as exc:
            logger.critical(
                msg=f"User Profile updating exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': 'Exception raised. Check logs for additional info'}, 500
        return result, 200


@ns.route('/password')
class UserPassword(Resource):
    @staticmethod
    @api.response(200, 'Password has been update')
    @api.response(500, 'Unexpected error on backend side')
    @token_required()
    def post():
        """
        Update existing user password by user token
        Use this method to update existing user password
        * Send a JSON object
        ```
            {
                "current_password": "some_pass",
                "new_password": "some_new_pass"
            }
        ```
        """
        data = request.get_json()

        auth_token = request.headers.get('AuthToken')
        username = get_user_id_by_token(auth_token)

        obj = Users.obj_exist(username=username)

        if not obj:
            result = {"status": f"User name is not exist: {username}"}
            return result, 404
        try:
            obj.update_password(username=username, current_password=data['current_password'], new_password=data['new_password'])
            result = {"status": f"password for user: {username} has been updated"}
        except ValueError as val_exc:
            logger.warning(
                msg=f"User password updating exception \nException: {str(val_exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {"msg": str(val_exc)}, 400
        except BadRequest as bad_request:
            logger.warning(
                msg=f"User password updating exception \nException: {str(bad_request)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': str(bad_request)}, 400
        except Exception as exc:
            logger.critical(
                msg=f"User password updating exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': 'Exception raised. Check logs for additional info'}, 500
        return result, 200


@ns.route('/all')
class GetAllUser(Resource):
    @staticmethod
    @api.response(200, 'Info has been collected')
    @token_required()
    def get():
        """
        Get list of all exist users
        Use this method to get list of all exist users
        """
        new_obj = Users.get_all_users()

        result = {'users': new_obj}

        return result, 200


@ns.route('/create')
class CreateUser(Resource):
    @staticmethod
    @api.response(200, 'User has been created')
    @api.response(400, 'User already exist')
    @api.response(422, 'Validation Error')
    @api.response(500, 'Unexpected error on backend side')
    def put():
        """
        Create user directly (without invite)
        Use this method to create user directly (without invite)
        * Send a JSON object
        ```
        {
            "username": "nkondratyk",
            "first_name": "Kolya",
            "second_name": "Kolya2",
            "email": "nasdaas@gmail.com",
            "role": "admin",
            "active_environment_ids": {
                "visible_only": [],
                "hidden": []
            },
            "phone": "+380986627571",
            "status": "active",
            "password": "some_pass"
        }
        ```
        """
        try:
            # Prepare input data
            data = users.load(request.get_json())

            # Format all elements to INT
            data['active_environment_ids']['visible_only'] = [int(x) for x in data['active_environment_ids']['visible_only']]
            data['active_environment_ids']['hidden'] = [int(x) for x in data['active_environment_ids']['hidden']]

            # Decorate events
            if 'phone' not in data:
                data['phone'] = False
            if 'status' not in data:
                data['status'] = 'active'

            # Write to MySQL
            new_obj = Users.create_user(data)
            result = users.dump(new_obj.dict())
        except ValidationError as error:
            return error.messages, 422
        except ValueError as val_exc:
            logger.warning(
                msg=str(val_exc),
                extra={'tags': {}})
            return {"msg": str(val_exc)}, 400
        except Exception as exc:
            logger.critical(
                msg=f"General exception \nException: {str(exc)} \nTraceback: {traceback.format_exc()}",
                extra={'tags': {}})
            return {'msg': 'Exception raised. Check logs for additional info'}, 500

        return result, 200


@ns.route('/delete/<user_id>')
class DeleteUser(Resource):
    @staticmethod
    @api.response(200, 'User has been delete')
    @api.response(500, 'Unexpected error on backend side')
    def delete(user_id):
        """
            Delete User object with specified id
        """
        if not user_id:
            return {'msg': f'user_id should be specified'}, 404
        obj = Users.obj_exist(user_id=user_id)
        try:
            if obj:
                obj.delete_obj()
                logger.info(msg=f"User deletion. Id: {user_id}")
            else:
                return {'msg': f'Object with specified user_id - {user_id} is not found'}, 404
        except Exception as exc:
            logger.critical(
                msg=f"User deletion exception - {exc}\nTrace: {traceback.format_exc()}")
            return {'msg': f'Deletion of user with id: {user_id} failed. '
                           f'Exception: {str(exc)}'}, 500
        return {'msg': f"User with id: {user_id} successfully deleted"}, 200


@ns.route('/block/<user_id>')
class BlockUser(Resource):
    @staticmethod
    @api.response(200, 'User has been blocked')
    @api.response(500, 'Unexpected error on backend side')
    def post(user_id):
        """
            Block User with specified id
        """
        if not user_id:
            return {'msg': f'user_id should be specified'}, 404
        obj = Users.obj_exist(user_id=user_id)
        try:
            if obj:
                obj.block_user(user_id=user_id)
                logger.info(msg=f"User was blocked. Id: {user_id}")
            else:
                return {'msg': f'Object with specified user_id - {user_id} is not found'}, 404
        except Exception as exc:
            logger.critical(
                msg=f"User block exception - {exc}\nTrace: {traceback.format_exc()}")
            return {'msg': f'Block of user with id: {user_id} failed. '
                           f'Exception: {str(exc)}'}, 500
        return {'msg': f"User with id: {user_id} successfully blocked"}, 200


@ns.route('/availableEnvironments')
class UserAvailableEnvironments(Resource):
    @staticmethod
    @token_required()
    def get():
        """
            Get all envs for specific user
        """
        auth_token = request.headers.get('AuthToken')
        username = get_user_id_by_token(auth_token)

        user_info = Users.get_user_info_by_name(username=username)['active_environment_ids']

        user_environments = UserEnvironments(env_filter=user_info, username=username)
        available_envs = user_environments.get_available_envs()

        return available_envs, 200


@ns.route('/availableUsers')
class AvailableUsers(Resource):
    @staticmethod
    @token_required()
    def post():
        """
            Get all users for specific env
        ```
            {
                "env_name": "Nova Street",
                "env_settings": {
                    "description": "Some Env Desc",
                    "default_scenario": 1
                },
                "available_for_users_id": {
                    "visible_only": [],
                    "hidden": []
                }
            }
        ```
        """
        data = request.get_json()
        process_env = ProcessNewEnvs(new_env=data)
        affected_users = process_env.update_user_env()

        return affected_users, 200
