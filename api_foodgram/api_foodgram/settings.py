import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY", "fcyjmjx^xxl967jx=-35tmn7+#8x5pmuit=p7!0g7q)heghjr%"
)

DEBUG = False

ALLOWED_HOSTS = [os.getenv("SERVER_HOST", "127.0.0.1")]

INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "djoser",
    "users.apps.UsersConfig",
    "recipes",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "api_foodgram.urls"

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "api_foodgram.wsgi.application"

DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = ("./data",)
STATICFILES_DIRS_DATA = os.path.join(BASE_DIR, "csv_data")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Redefining the 'User' model
AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
}

# Debug mode settings
if DEBUG:
    INSTALLED_APPS.extend(("debug_toolbar", "corsheaders"))
    MIDDLEWARE.extend(
        (
            "debug_toolbar.middleware.DebugToolbarMiddleware",
            "corsheaders.middleware.CorsMiddleware",
            "django.middleware.common.CommonMiddleware",
        )
    )
    REST_FRAMEWORK.update(
        {
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "rest_framework.authentication.TokenAuthentication",
                "rest_framework.authentication.SessionAuthentication",
            ],
        }
    )
    CORS_ALLOWED_ORIGINS = ("http://localhost:3000",)
    CORS_URLS_REGEX = r"^/api.*$"
    CSRF_TRUSTED_ORIGINS = ('http://localhost', 'http://127.0.0.1')

# Djoser settings
DJOSER = {
    "LOGIN_FIELD": "email",
    "HIDE_USERS": False,
    "PERMISSIONS": {
        "user": ["rest_framework.permissions.IsAuthenticated"],
        "user_list": ["rest_framework.permissions.AllowAny"],
        "activation": ["api.v1.permissions.DeniedAny"],
        "password_reset": ["api.v1.permissions.DeniedAny"],
        "password_reset_confirm": ["api.v1.permissions.DeniedAny"],
        "username_reset": ["api.v1.permissions.DeniedAny"],
        "username_reset_confirm": ["api.v1.permissions.DeniedAny"],
        "set_username": ["api.v1.permissions.DeniedAny"],
    },
    "SERIALIZERS": {
        "user_create": "api.v1.serializers.CustomUserCreateSerializer",
        "user": "api.v1.serializers.UserSerializer",
        "current_user": "api.v1.serializers.UserSerializer",
    },
}

# Pagination options
PAGE_SIZE = 6
MAX_PAGE_SIZE = 24
DEFAULT_LIMIT = 3
MAX_LIMIT = 7
