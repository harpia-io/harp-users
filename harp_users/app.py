from microservice_template_core import Core
from microservice_template_core.settings import ServiceConfig, FlaskConfig, DbConfig
from harp_users.endpoints.users import ns as users
from harp_users.endpoints.auth import ns as auth
from microservice_template_core.tools.logger import get_logger
from harp_users.logic.process_new_envs import process_kafka_message
from harp_users.endpoints.health import ns as health
import threading

logger = get_logger()


def init_consumer():
    env_update_consumer = threading.Thread(name='Env Update Consumer', target=process_kafka_message, daemon=True)
    env_update_consumer.start()


def main():
    ServiceConfig.configuration['namespaces'] = [users, auth, health]
    FlaskConfig.FLASK_DEBUG = False
    DbConfig.USE_DB = True

    init_consumer()
    app = Core()
    app.run()


if __name__ == '__main__':
    main()

