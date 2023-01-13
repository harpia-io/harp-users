from microservice_template_core.tools.logger import get_logger
from harp_users.models.users import Users
from microservice_template_core import KafkaConsumeMessages
import traceback
import json
import harp_users.settings as settings

logger = get_logger()


class ProcessEnvDelete(object):
    def __init__(self, env_id):
        self.env_id = env_id

    def delete_env(self):
        deleted_for_users = []
        new_obj = Users.get_all_users()
        for user in new_obj:
            if self.env_id in user['active_environment_ids']['visible_only']:
                user['active_environment_ids']['visible_only'].remove(self.env_id)
                deleted_for_users.append(user['user_id'])

            if self.env_id in user['active_environment_ids']['hidden']:
                user['active_environment_ids']['hidden'].remove(self.env_id)
                deleted_for_users.append(user['user_id'])

            obj = Users.obj_exist(user_id=user['user_id'])
            obj.update_existing_profile(user_id=user['user_id'], data=user)

        logger.info(msg=f"Env {self.env_id} was deleted for users - {deleted_for_users}")
        return deleted_for_users


class ProcessNewEnvs(object):
    """
    Add environment object
    Use this method to create new Env
    * Send a JSON object
    ```
        {
            "env_id": 12,
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
    def __init__(self, new_env):
        self.env_id = new_env['id']
        self.env_name = new_env['env_name']
        self.user_filter = new_env['available_for_users_id']

    @staticmethod
    def get_all_users():
        user_ids = []
        new_obj = Users.get_all_users()
        for user in new_obj:
            user_ids.append(int(user['user_id']))

        return user_ids

    def prepare_affected_users(self):
        all_users = self.get_all_users()

        if len(self.user_filter['visible_only']) == 0:
            if len(self.user_filter['hidden']) == 0:
                logger.info(msg=f"Env: {self.env_name} will be added to all users - {all_users}")
                return all_users
            else:
                for hidden_user in self.user_filter['hidden']:
                    if hidden_user in all_users:
                        all_users.remove(hidden_user)
                logger.info(msg=f"Env: {self.env_name} will be added to all users except hidden - {self.user_filter['hidden']}")
                return all_users

        if self.user_filter['visible_only']:
            if len(self.user_filter['hidden']) == 0:
                logger.info(msg=f"Env: {self.env_name} will be added to specific users - {self.user_filter['visible_only']}")
                return self.user_filter['visible_only']
            else:
                for hidden_user in self.user_filter['hidden']:
                    if hidden_user in self.user_filter['visible_only']:
                        self.user_filter['visible_only'].remove(hidden_user)
                logger.info(msg=f"Env: {self.env_name} will be added to all visible users except hidden - {self.user_filter['hidden']}")
                return self.user_filter['visible_only']

        logger.error(msg=f"User Filter is wrong - {self.user_filter}")

        return []

    def update_user_env(self):
        attached_to_users = []
        for single_user in self.prepare_affected_users():
            user_info = Users.get_user_info(user_id=single_user)['active_environment_ids']
            logger.info(msg=f"Get info for user - {single_user}: {user_info}")
            if user_info['visible_only']:
                logger.info(msg=f"Exact List is used by user {single_user}. It will be updated by new Env: {self.env_name}")
                if self.env_id not in user_info['visible_only']:
                    user_info['visible_only'].append(self.env_id)
                    data = {'active_environment_ids': user_info}
                    obj = Users.obj_exist(user_id=single_user)
                    obj.update_existing_profile(user_id=single_user, data=data)
                    logger.info(msg=f"visible_only has been updated for user: {single_user}")
                    attached_to_users.append(single_user)
                else:
                    logger.info(msg=f"Env name: {self.env_name} and env id: {self.env_id} already present in user visible_only - {user_info['visible_only']}")

        return f'Env {self.env_id} has been attached to users - {attached_to_users}'


def process_kafka_message():
    kafka_consumer = KafkaConsumeMessages(kafka_topic=settings.ENVIRONMENT_UPDATE_TOPIC)
    consumer = kafka_consumer.start_consumer()

    for message in consumer:
        parsed_json = None
        try:
            parsed_json = json.loads(message.value.decode('utf-8'))
            logger.info(msg=f"Get event from Kafka:\nJSON: {parsed_json}")

            if parsed_json['type'] == 'add':
                process_env = ProcessNewEnvs(new_env=parsed_json['body'])
                process_env.update_user_env()

            if parsed_json['type'] == 'update':
                process_env = ProcessNewEnvs(new_env=parsed_json['body'])
                process_env.update_user_env()

            if parsed_json['type'] == 'delete':
                process_env = ProcessEnvDelete(env_id=parsed_json['body']['environment_id'])
                process_env.delete_env()

        except ConnectionResetError as err:
            logger.warning(msg=f"Can`t connect to DB: {err}\nStack: {traceback.format_exc()}\n{parsed_json}")
            continue
        except Exception as err:
            logger.error(msg=f"Exception in Thread: {err}\nStack: {traceback.format_exc()}\n{parsed_json}")
            continue
