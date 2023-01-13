import requests
from microservice_template_core.tools.logger import get_logger
import harp_users.settings as settings
import traceback
import requests_cache

log = get_logger()

requests_cache.install_cache(cache_name='cache', backend='memory', expire_after=15, allowable_methods='GET')

def bot_config(bot_name):
    url = f"{settings.BOTS_SERVICE}/{bot_name}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    log.info(msg=f"Request {bot_name} config from bots service: {url}")
    try:
        req = requests.get(url=url, headers=headers, timeout=10)
        if req.status_code == 200:
            log.info(msg=f"Receive {bot_name} response from bots service: {req.json()}")
            return req.json()['config']
        else:
            log.error(msg=f"Error during receiving bot config: {req.content}, stack: {traceback.format_exc()}")
    except Exception as err:
        log.error(msg=f"Error during receiving bot config: {err}, stack: {traceback.format_exc()}")
        return {'msg': None}
