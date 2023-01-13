from microservice_template_core.tools.logger import get_logger
from harp_users.settings import ENVIRONMENTS_HOST
import requests
import traceback
import requests_cache

logger = get_logger()
requests_cache.install_cache(cache_name='cache', backend='memory', expire_after=15, allowable_methods='GET')


class UserEnvironments(object):
    def __init__(self, env_filter, username):
        self.env_filter = env_filter
        self.username = username
        self.all_envs = self.get_all_envs()

    @staticmethod
    def get_all_envs():
        url = f"{ENVIRONMENTS_HOST}/api/v1/environments/all"
        all_envs = []
        try:
            req = requests.get(
                url=url,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=10
            )
            if req.status_code == 200:
                logger.info(
                    msg=f"Requested Environments list\nReceived response: {req.json()}"
                )

                return req.json()
            else:
                logger.error(
                    msg=f"Can`t connect to Env service to get full Env list"
                )
                return all_envs
        except Exception as err:
            logger.error(
                msg=f"Error: {err}, stack: {traceback.format_exc()}"
            )
            return all_envs

    def prepare_available_envs(self):
        all_envs_decorated = []
        for env_id in self.all_envs:
            all_envs_decorated.append(int(env_id))

        if len(self.env_filter['visible_only']) == 0:
            if len(self.env_filter['hidden']) == 0:
                logger.info(msg=f"User: {self.username} has access to all Envs")
                return all_envs_decorated
            else:
                for hidden_env in self.env_filter['hidden']:
                    if hidden_env in all_envs_decorated:
                        all_envs_decorated.remove(hidden_env)
                logger.info(msg=f"User: {self.username} has access to all Envs except hidden - {self.env_filter['hidden']}")
                return all_envs_decorated

        if self.env_filter['visible_only']:
            if len(self.env_filter['hidden']) == 0:
                logger.info(msg=f"User: {self.username} has access to specific Envs - {self.env_filter['visible_only']}")
                return self.env_filter['visible_only']
            else:
                for hidden_env in self.env_filter['hidden']:
                    if hidden_env in self.env_filter['visible_only']:
                        self.env_filter['visible_only'].remove(hidden_env)
                logger.info(
                    msg=f"User: {self.username} has access to all Envs except hidden - {self.env_filter['hidden']}")
                return self.env_filter['visible_only']

        logger.error(msg=f"You should choose one filter for user - {self.username}. Currently you have - {self.env_filter}")

        return []

    def get_available_envs(self):
        envs_to_show_user = {}
        available_envs = self.prepare_available_envs()

        for env_id, env_name in self.all_envs.items():
            if int(env_id) in available_envs:
                envs_to_show_user[env_id] = env_name

        return envs_to_show_user
