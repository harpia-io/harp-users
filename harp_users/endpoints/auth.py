import traceback

from microservice_template_core.tools.flask_restplus import api
from flask_restx import Resource
from microservice_template_core.tools.logger import get_logger
from harp_users.models.users import Users
from flask import request

logger = get_logger()
ns = api.namespace('api/v1/auth', description='Harp Auth endpoints')


@ns.route('/login')
class Login(Resource):
    @api.response(200, 'Login success')
    @api.response(401, 'Access denied')
    @api.response(500, 'Unexpected error on backend side')
    def post(self):
        """
        Verify user name and password
        Return access_token and refresh_token
        * Send a JSON object
        ```
            {
                "username": "somename",
                "password": "somepass"
            }
        ```
        * Response
        ```
            {
                "token": "token",
                "refresh_token": "refresh_token",
                "id": 1,
                "firstName": "FirstUser1",
                "secondName": "SecondUser2",
                "username": "buhtik",
                "email": "nasdaas@gmail.com",
                "role": "admins",
                "phone": "+380672797263",
                "active_environment_ids": [
                    1, 2, 3
                ],
                "status": "active"
            }
        ```
        """

        data = request.json
        username = data.get('username', None)
        password = data.get('password', None)

        logger.info(
            msg=f"Receive request for Login - {username}",
            extra={'tags': {}}
        )

        if not username:
            return {"msg": "Missing username parameter"}, 401
        if not password:
            return {"msg": "Missing password parameter"}, 401

        try:
            if '@' in username:
                user_id, auth = Users.authenticate(email=username, password=password)
            else:
                user_id, auth = Users.authenticate(username=username, password=password)
        except UserWarning as err:
            return {"msg": f"{err}"}, 401
        except PermissionError as err:
            return {"msg": f"{err}"}, 401
        except Exception as err:
            return {"msg": f"Unexpected error on backend side: {err}\nTrace: {traceback.format_exc()}"}, 500

        user_info = Users.get_user_info(user_id=user_id)

        user_info.update(auth)

        return user_info, 200
