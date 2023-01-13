import os

TOKEN_EXPIRE_HOURS = os.getenv('TOKEN_EXPIRE_HOURS', 24)
ENVIRONMENTS_HOST = os.getenv('ENVIRONMENTS_HOST', 'https://dev.harpia.io/harp-environments')
ENVIRONMENT_UPDATE_TOPIC = os.getenv('ENVIRONMENT_UPDATE_TOPIC', 'environment-update')

SERVICE_NAMESPACE = os.getenv('SERVICE_NAMESPACE', 'dev')
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))

BOTS_SERVICE = os.getenv('BOTS_SERVICE', 'https://playground.harpia.io/harp-bots/api/v1/bots')

DOCKER_SERVER_IP = os.getenv('DOCKER_SERVER_IP', False)