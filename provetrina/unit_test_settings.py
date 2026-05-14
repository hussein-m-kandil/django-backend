from django.conf import global_settings

from provetrina.settings import *  # noqa: F403

print('Using unit test settings...')

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher'
] + global_settings.PASSWORD_HASHERS
