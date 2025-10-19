
DEBUG = True
#ALLOWED_HOSTS = ['*']

from integration_utils.bitrix24.local_settings_class import LocalSettingsClass

TINKOFF_API_KEY = 'your-api-key'
ENDPOINT_TINKOFF = 'your-secret-key'
API_KEY_TINKOFF = 'your-api-key'
SECRET_KEY_TINKOFF = 'your-secret-key'

OPEN_AI_API_KEY = 'your-api-key'

NGROK_URL = 'https://nonsententious-kimberlee-noneagerly.ngrok-free.dev'

APP_SETTINGS = LocalSettingsClass(
    portal_domain='b24-k1o8cr.bitrix24.ru',
    app_domain='127.0.0.1:8000',
    app_name='Applications',
    salt='wefiewofioiI(IF(Eufrew8fju8ewfjhwkefjlewfjlJFKjewubhybfwybgybHBGYBGF',
    secret_key='wefewfkji4834gudrj.kjh237tgofhfjekewf.kjewkfjeiwfjeiwjfijewf',
    application_bitrix_client_id='local.68e68afcd59400.97066536',
    application_bitrix_client_secret='99fjTokbueA0KAvF4l7DKhrFCy4kAjHa53DxPuMKpjRSY1dPD8',
    application_index_path='/',
)

DOMAIN = "56218ef983f3-8301993767665431593.ngrok-free.app"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'DB_internship_B24',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
    },
}