"""
Django settings for qfieldcloud project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from datetime import timedelta

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .settings_utils import ConfigValidationError, get_storages_config

# QFieldCloud specific configuration
QFIELDCLOUD_HOST = os.environ["QFIELDCLOUD_HOST"]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", default=0))

# if we are in debug, we need to update the internal IPS to make the
# debug toolbar work within docker
if DEBUG:
    import socket  # only if you haven't already imported this

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]

ENVIRONMENT = os.environ.get("ENVIRONMENT")

# 'DJANGO_ALLOWED_HOSTS' should be a single string of hosts with a space between each.
# For example: 'DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]'
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(" ")

# A tuple representing an HTTP header/value combination that signifies a request is secure, which is important for Django’s CSRF protection.
# We need to set it in QFieldCloud as we run behind a proxy.
# Read more: https://docs.djangoproject.com/en/4.2/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

WEB_HTTP_PORT = os.environ.get("WEB_HTTP_PORT")
WEB_HTTPS_PORT = os.environ.get("WEB_HTTPS_PORT")

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    # custom QFC backend that extends the `allauth` specific authentication methods
    # such as login by email, but restricting who can login to only regular users
    "qfieldcloud.authentication.auth_backends.AuthenticationBackend",
]


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": "memcached:11211",
        "OPTIONS": {
            "no_delay": True,
            "ignore_exc": True,
            "max_pool_size": 10,
            "use_pooling": True,
        },
    }
}

# Application definition
INSTALLED_APPS = [
    # admin theme
    "jazzmin",
    # django contrib
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.gis",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # 3rd-party apps
    # if django_filters defined after [rest_framework] caused '... _frozen_importlib._DeadlockError ...'
    # https://stackoverflow.com/questions/55844680/deadlock-detected-when-trying-to-start-server
    "django_filters",
    # debug
    "debug_toolbar",
    # style
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.microsoft",
    "allauth.socialaccount.providers.openid_connect",
    "storages",  # Integration with S3 Storages
    "invitations",
    "django_cron",
    "django_countries",
    "timezone_field",
    "auditlog",
    # Local
    "qfieldcloud.core",
    # listed after core because we overwrite createsuperuser command
    "django.contrib.auth",
    "qfieldcloud.subscription",
    "qfieldcloud.notifs",
    "qfieldcloud.authentication",
    "qfieldcloud.filestorage",
    # 3rd party - keep at bottom to allow overrides
    "notifications",
    "axes",
    "migrate_sql",
    "constance",
    "django_extensions",
    "django_cleanup.apps.CleanupConfig",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "qfieldcloud.core.middleware.requests.attach_keys",  # QF-2540: Inspecting request after Django middlewares
    "log_request_id.middleware.RequestIDMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_currentuser.middleware.ThreadLocalUserMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
    "qfieldcloud.core.middleware.timezone.TimezoneMiddleware",
    "qfieldcloud.core.middleware.test.TestMiddleware",
    "axes.middleware.AxesMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "qfieldcloud.core.middleware.qgis_auth.QGISAuthenticationMiddleware",
]

CRON_CLASSES = [
    "qfieldcloud.notifs.cron.SendNotificationsJob",
    # "qfieldcloud.core.cron.DeleteExpiredInvitationsJob",
    "qfieldcloud.core.cron.ResendFailedInvitationsJob",
    "qfieldcloud.core.cron.SetTerminatedWorkersToFinalStatusJob",
    "qfieldcloud.core.cron.DeleteObsoleteProjectPackagesJob",
]

ROOT_URLCONF = "qfieldcloud.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "qfieldcloud", "core", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "builtins": [
                "qfieldcloud.core.templatetags.filters",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "qfieldcloud.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
        "OPTIONS": {"sslmode": os.environ.get("POSTGRES_SSLMODE")},
        "TEST": {
            "NAME": os.environ.get("POSTGRES_DB_TEST"),
        },
    }
}

# Connection details for the geodb
GEODB_HOST = os.environ.get("GEODB_HOST")
GEODB_PORT = os.environ.get("GEODB_PORT")
GEODB_DB = os.environ.get("GEODB_DB")
GEODB_USER = os.environ.get("GEODB_USER")
GEODB_PASSWORD = os.environ.get("GEODB_PASSWORD")

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = os.environ.get("QFIELDCLOUD_DEFAULT_LANGUAGE") or "en"

TIME_ZONE = os.environ.get("QFIELDCLOUD_DEFAULT_TIME_ZONE") or "Europe/Zurich"

USE_I18N = bool(os.environ.get("QFIELDCLOUD_USE_I18N")) or True

USE_TZ = True


LANGUAGES = [
    ("en", "English"),
    ("es", "Spanish"),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "qfieldcloud", "core", "staticfiles"),
]

MEDIA_URL = "/mediafiles/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

# S3 Storage
STORAGE_ACCESS_KEY_ID = os.environ.get("STORAGE_ACCESS_KEY_ID")
STORAGE_SECRET_ACCESS_KEY = os.environ.get("STORAGE_SECRET_ACCESS_KEY")
STORAGE_BUCKET_NAME = os.environ.get("STORAGE_BUCKET_NAME")
STORAGE_REGION_NAME = os.environ.get("STORAGE_REGION_NAME")
STORAGE_ENDPOINT_URL = os.environ.get("STORAGE_ENDPOINT_URL")

_storage_config = get_storages_config()

STORAGES = {
    **_storage_config["STORAGES"],
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

LEGACY_STORAGE_NAME = _storage_config["LEGACY_STORAGE_NAME"]

# Maximum filename length in characters
# NOTE the keys on S3 cannot be longer than 1024 _bytes_, see https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html
# NOTE the files on Windows cannot be longer than 260 _chars_ by default, see https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file?redirectedfrom=MSDN#maximum-path-length-limitation
# NOTE minio limit is 255 _chars_ per filename segment, read https://min.io/docs/minio/linux/operations/concepts/thresholds.html#id1
STORAGE_FILENAME_MAX_CHAR_LENGTH = 255

# Filename validator regex.
# Should filter out all the names that have reserved characters and words for both Linux and Windows.
STORAGES_FILENAME_VALIDATION_REGEX = (
    r'^(?!.*[<>:"/\\|?*])'
    r"(?!(?:COM[0-9]|CON|LPT[0-9]|NUL|PRN|AUX|com[0-9]|con|lpt[0-9]|nul|prn|aux)$)"
    # dynamically set the max char length
    r'[^\\\/:*"?<>|]{1,' + str(STORAGE_FILENAME_MAX_CHAR_LENGTH) + "}"
    r"(?<![\s\.])$"
)

STORAGES_PROJECT_DEFAULT_STORAGE = (
    os.environ.get("STORAGES_PROJECT_DEFAULT_STORAGE") or "default"
)

if STORAGES_PROJECT_DEFAULT_STORAGE not in STORAGES:
    raise ConfigValidationError(
        f"Missing {STORAGES_PROJECT_DEFAULT_STORAGE=} from the `STORAGES` configuration, available storages: {STORAGES.keys()}"
    )

AUTH_USER_MODEL = "core.User"

# QFieldCloud variables
AUTH_TOKEN_LENGTH = 100
AUTH_TOKEN_EXPIRATION_HOURS = int(
    os.environ.get("QFIELDCLOUD_AUTH_TOKEN_EXPIRATION_HOURS") or 24 * 30
)

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "qfieldcloud.authentication.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "qfieldcloud.core.rest_utils.exception_handler",
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SITE_ID = 1

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "index"

# Sentry configuration
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
if SENTRY_DSN:
    SENTRY_SAMPLE_RATE = float(os.environ.get("SENTRY_SAMPLE_RATE", 1))

    def before_send(event, hint):
        from rest_framework.exceptions import MethodNotAllowed, UnsupportedMediaType
        from rest_framework.exceptions import ValidationError as RestValidationError

        from qfieldcloud.core.exceptions import (
            AuthenticationViaTokenFailedError,
            ProjectAlreadyExistsError,
            ValidationError,
        )
        from qfieldcloud.subscription.exceptions import (
            InactiveSubscriptionError,
            PlanInsufficientError,
            QuotaError,
        )

        ignored_exceptions = (
            ValidationError,
            ProjectAlreadyExistsError,
            QuotaError,
            PlanInsufficientError,
            InactiveSubscriptionError,
            RestValidationError,
            UnsupportedMediaType,
            # Purely a client error
            MethodNotAllowed,
            # the client sent invalid authentication token, the user should fix his token
            AuthenticationViaTokenFailedError,
        )

        if "exc_info" in hint:
            exc_class, _exc_object, _exc_tb = hint["exc_info"]

            # Skip sending errors
            if issubclass(exc_class, ignored_exceptions):
                return None

        return event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        server_name=QFIELDCLOUD_HOST,
        #
        # Sentry sample rate between 0 and 1. Read more on https://docs.sentry.io/platforms/python/configuration/sampling/ .
        sample_rate=SENTRY_SAMPLE_RATE,
        #
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        #
        # Filter some of the exception which we do not want to see on Sentry. Read more on https://docs.sentry.io/platforms/python/configuration/filtering/ .
        before_send=before_send,
        #
        # Sentry environment should have been configured like this, but I didn't make it work.
        # Therefore the Sentry environment is defined as `SENTRY_ENVIRONMENT` in `docker-compose.yml`.
        # environment=ENVIRONMENT,
    )

# QF-2704
# Flag to turn on/off byte-for-byte copy of request's body
# Only requests with a < 10MB body will be reported
SENTRY_REPORT_FULL_BODY = True

# Django allauth configurations
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""

# Django allauth's RateLimiter configuration
# https://docs.allauth.org/en/latest/account/rate_limits.html
ACCOUNT_RATE_LIMITS = False

# Choose one of "mandatory", "optional", or "none".
# For local development and test use "optional" or "none"
ACCOUNT_EMAIL_VERIFICATION = os.environ.get("ACCOUNT_EMAIL_VERIFICATION")

# This setting determines whether the username is stored in lowercase (False) or whether its casing is to be preserved (True).
# Note that when casing is preserved, potentially expensive __iexact lookups are performed when filter on username.
# For now, the default is set to True to maintain backwards compatibility.
# See https://docs.allauth.org/en/dev/account/configuration.html
ACCOUNT_PRESERVE_USERNAME_CASING = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_ADAPTER = "qfieldcloud.core.adapters.AccountAdapter"
ACCOUNT_LOGOUT_ON_GET = True

# Django allauth's social account configuration
# https://docs.allauth.org/en/dev/socialaccount/configuration.html
SOCIALACCOUNT_ADAPTER = "qfieldcloud.core.adapters.SocialAccountAdapter"
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_LOGIN_ON_GET = True

QFIELDCLOUD_PASSWORD_LOGIN_DISABLED = (
    os.environ.get("QFIELDCLOUD_PASSWORD_LOGIN_DISABLED", "true").lower() == "true"
)

QFIELDCLOUD_SSO_PROVIDER_STYLES = {
    "keycloak": {
        # https://github.com/keycloak/keycloak-misc/tree/main/logo
        "required": False,
        "light": {
            "logo": "sso/keycloak.svg",
            "color_fill": "#FFFFFF",
            "color_stroke": "#747775",
            "color_text": "#1F1F1F",
        },
        "dark": {
            "logo": "sso/keycloak.svg",
            "color_fill": "#131314",
            "color_stroke": "#8E918F",
            "color_text": "#E3E3E3",
        },
    },
    "google": {
        # https://developers.google.com/identity/branding-guidelines
        "required": True,
        "light": {
            "logo": "sso/google.svg",
            "color_fill": "#FFFFFF",
            "color_stroke": "#747775",
            "color_text": "#1F1F1F",
        },
        "dark": {
            "logo": "sso/google.svg",
            "color_fill": "#131314",
            "color_stroke": "#8E918F",
            "color_text": "#E3E3E3",
        },
    },
    "github": {
        # https://github.com/logos
        "required": False,
        "light": {
            "logo": "sso/github-light.svg",
            "color_fill": "#FFFFFF",
            "color_stroke": "#747775",
            "color_text": "#1F1F1F",
        },
        "dark": {
            "logo": "sso/github-dark.svg",
            "color_fill": "#131314",
            "color_stroke": "#8E918F",
            "color_text": "#E3E3E3",
        },
    },
}

# Django axes configuration
# https://django-axes.readthedocs.io/en/latest/4_configuration.html
###########################
# The integer number of login attempts allowed before a record is created for the failed logins. Default: 3
AXES_FAILURE_LIMIT = 5
# Configures the limiter to handle username only (see https://django-axes.readthedocs.io/en/latest/2_installation.html#version-7-breaking-changes-and-upgrading-from-django-axes-version-6)
AXES_LOCKOUT_PARAMETERS = ["username"]
# If set, defines a period of inactivity after which old failed login attempts will be cleared. If an integer, will be interpreted as a number of hours. Default: None
AXES_COOLOFF_TIME = lambda _request: timedelta(minutes=30)  # noqa: E731
# If True, a successful login will reset the number of failed logins. Default: False
AXES_RESET_ON_SUCCESS = True

# Django email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "").lower() == "true"
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "").lower() == "true"
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")


# Django invitations configurations
# https://github.com/bee-keeper/django-invitations#additional-configuration
INVITATIONS_INVITATION_EXPIRY = 365  # integer in days, 0 disables invitations
INVITATIONS_INVITATION_ONLY = False
# INVITATIONS_ACCEPT_INVITE_AFTER_SIGNUP = True
INVITATIONS_GONE_ON_ACCEPT_ERROR = False

TEST_RUNNER = "qfieldcloud.testing.QfcTestSuiteRunner"

LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG").upper()
LOG_REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
GENERATE_REQUEST_ID_IF_NOT_IN_HEADER = False
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"request_id": {"()": "log_request_id.filters.RequestIDFilter"}},
    "formatters": {
        "json": {
            "()": "qfieldcloud.core.logging.formatters.CustomisedJSONFormatter",
        },
    },
    "handlers": {
        "console.json": {
            "class": "logging.StreamHandler",
            "filters": ["request_id"],
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console.json"],
        "level": "INFO",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Whether we are currently running tests
# NOTE automatically set when running tests, don't change manually!
IN_TEST_SUITE = False

# The format used in the deprecated field `last_modified` in storage related serializers.
# The settings and `last_modified` field are deprecated and soon to be removed.
QFIELDCLOUD_STORAGE_DT_LAST_MODIFIED_FORMAT = "%d.%m.%Y %H:%M:%S %Z"

QFIELDCLOUD_SUBSCRIPTION_MODEL = os.environ.get(
    "QFIELDCLOUD_SUBSCRIPTION_MODEL", "subscription.Subscription"
)

QFIELDCLOUD_TOKEN_SERIALIZER = "qfieldcloud.core.serializers.TokenSerializer"
QFIELDCLOUD_USER_SERIALIZER = "qfieldcloud.core.serializers.CompleteUserSerializer"

# Admin URLS which will be skipped from checking if they return HTTP 200
QFIELDCLOUD_TEST_SKIP_VIEW_ADMIN_URLS = (
    "/admin/login/",
    "/admin/logout/",
    "/admin/password_change/",
    "/admin/password_change/done/",
    "/admin/autocomplete/",
    "/admin/core/delta/add/",
    "/admin/core/job/add/",
    "/admin/axes/accessattempt/add/",
    "/admin/axes/accessfailurelog/add/",
    "/admin/axes/accesslog/add/",
    "/admin/auditlog/logentry/add/",
    "/admin/account/emailaddress/admin/export_emails_to_csv/",
)

# Sets the default admin list view per page, the Django default is 100
QFIELDCLOUD_ADMIN_LIST_PER_PAGE = 20

# Use pg meta table estimate for pagination and display above n entries
QFIELDCLOUD_ADMIN_EXACT_COUNT_LIMIT = 10000

# Default limit for paginating data from views using QfcLimitOffsetPagination
QFIELDCLOUD_API_DEFAULT_PAGE_LIMIT = 50

# Admin sort URLs which will be skipped from checking if they return HTTP 200
QFIELDCLOUD_TEST_SKIP_SORT_ADMIN_URLS = ("/admin/django_cron/cronjoblog/?o=4",)

APPLY_DELTAS_LIMIT = 1000

# the value of the "source" key in each logger entry
LOGGER_SOURCE = os.environ.get("LOGGER_SOURCE", None)

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda r: DEBUG and ENVIRONMENT == "development",
}

QFIELDCLOUD_ADMIN_URI = os.environ.get("QFIELDCLOUD_ADMIN_URI", "admin/")

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_DATABASE_CACHE_BACKEND = "default"
CONSTANCE_DATABASE_CACHE_AUTOFILL_TIMEOUT = 60 * 60 * 24
CONSTANCE_CONFIG = {
    "WORKER_TIMEOUT_S": (
        600,
        "Timeout of the workers before being terminated by the wrapper in seconds.",
        int,
    ),
    "WORKER_QGIS_MEMORY_LIMIT": (
        "1000m",
        "Maximum memory for each QGIS worker container.",
        str,
    ),
    "SENTRY_REQUEST_MAX_SIZE_TO_SEND": (
        0,
        "Maximum request size to send the raw request to Sentry. Value 0 disables the raw request copy.",
        int,
    ),
    "WORKER_QGIS_CPU_SHARES": (
        512,
        "Share of CPUs for each QGIS worker container. By default all containers have value 1024 set by docker.",
        int,
    ),
    "TRIAL_PERIOD_DAYS": (
        28,
        "Days in which the trial period expires.",
        int,
    ),
}
CONSTANCE_ADDITIONAL_FIELDS = {
    "textarea": [
        "django.forms.CharField",
        {
            "widget": "django.forms.Textarea",
        },
    ]
}
CONSTANCE_CONFIG_FIELDSETS = {
    "Worker": (
        "WORKER_TIMEOUT_S",
        "WORKER_QGIS_MEMORY_LIMIT",
        "WORKER_QGIS_CPU_SHARES",
    ),
    "Debug": ("SENTRY_REQUEST_MAX_SIZE_TO_SEND",),
    "Subscription": ("TRIAL_PERIOD_DAYS",),
}

# Name of the qgis docker image used as a worker by worker_wrapper
QFIELDCLOUD_QGIS_IMAGE_NAME = os.environ["QFIELDCLOUD_QGIS_IMAGE_NAME"]

# URL the qgis worker will use to access the running API endpoint on the app service
QFIELDCLOUD_WORKER_QFIELDCLOUD_URL = os.environ["QFIELDCLOUD_WORKER_QFIELDCLOUD_URL"]

# Absolute path on the docker host where `libqfieldsync` is mounted from for development
QFIELDCLOUD_LIBQFIELDSYNC_VOLUME_PATH = os.environ.get(
    "QFIELDCLOUD_LIBQFIELDSYNC_VOLUME_PATH"
)

# Absolute path on the docker host where `qfieldcloud-sdk-python` is mounted from for development
QFIELDCLOUD_QFIELDCLOUD_SDK_VOLUME_PATH = os.environ.get(
    "QFIELDCLOUD_QFIELDCLOUD_SDK_VOLUME_PATH"
)

# Volume name where transformation grids required by `PROJ` are downloaded to
QFIELDCLOUD_TRANSFORMATION_GRIDS_VOLUME_NAME = os.environ.get(
    "QFIELDCLOUD_TRANSFORMATION_GRIDS_VOLUME_NAME"
)

# Name of the docker compose network to be used by the worker containers
QFIELDCLOUD_DEFAULT_NETWORK = os.environ.get("QFIELDCLOUD_DEFAULT_NETWORK")

# `django-auditlog` configurations, read more on https://django-auditlog.readthedocs.io/en/latest/usage.html
AUDITLOG_INCLUDE_TRACKING_MODELS = [
    # NOTE `Delta` and `Job` models are not being automatically audited, because their data changes very often and timestamps are available in their models.
    {
        "model": "account.emailaddress",
    },
    # NOTE Constance model cannot be audited. If enabled, an `IndexError list index out of range` is raised.
    # {
    #     "model": "constance.config",
    # },
    {
        "model": "core.geodb",
    },
    {
        "model": "core.organization",
    },
    # TODO check if we can use `Organization.members` m2m when next version is released as described in "Many-to-many fields" here https://django-auditlog.readthedocs.io/en/latest/usage.html#automatically-logging-changes
    {
        "model": "core.organizationmember",
    },
    {
        "model": "core.person",
        "exclude_fields": ["last_login", "updated_at"],
    },
    {
        "model": "core.project",
        # these fields are updated by scripts and will produce a lot of audit noise
        "exclude_fields": [
            "updated_at",
            "data_last_updated_at",
            "data_last_packaged_at",
            "last_package_job",
            "file_storage_bytes",
        ],
    },
    # TODO check if we can use `Project.collaborators` m2m when next version is released as described in "Many-to-many fields" here https://django-auditlog.readthedocs.io/en/latest/usage.html#automatically-logging-changes
    {
        "model": "core.projectcollaborator",
    },
    {
        "model": "core.secret",
        "mask_fields": [
            "value",
        ],
    },
    # TODO check if we can use `Team.members` m2m when next version is released as described in "Many-to-many fields" here https://django-auditlog.readthedocs.io/en/latest/usage.html#automatically-logging-changes
    {
        "model": "core.team",
    },
    {
        "model": "core.teammember",
    },
    {
        "model": "core.user",
        "exclude_fields": ["last_login", "updated_at"],
    },
    {
        "model": "core.useraccount",
    },
    {
        "model": "invitations.invitation",
    },
    {
        "model": "subscription.package",
    },
    {
        "model": "subscription.packagetype",
    },
    {
        "model": "subscription.plan",
    },
    {
        "model": "subscription.subscription",
    },
    {
        "model": "filestorage.file",
        "exclude_fields": ["latest_version_count"],
    },
    {
        "model": "filestorage.fileversion",
        # exclude the `BinaryField` instances until https://github.com/jazzband/django-auditlog/pull/689 is merged and released
        "exclude_fields": ["md5sum", "sha256sum"],
    },
]

SPECTACULAR_SETTINGS = {
    "TITLE": "QFieldCloud JSON API",
    "DESCRIPTION": "QFieldCloud JSON API",
    "VERSION": "v1",
    "CONTACT": {"email": "info@opengis.ch"},
    "LICENSE": {"name": "License"},
}

JAZZMIN_SETTINGS = {
    # Page title. Defaults to `current_admin_site.site_title` if empty.
    "site_title": "QFieldCloud: Admin",
    # Site header title (max 19 chars). Defaults to  `current_admin_site.site_header` if empty.
    "site_header": "QFieldCloud",
    # Brand name (max 19 chars). Defaults to  `current_admin_site.site_header` if empty.
    "site_brand": "QFieldCloud admin",
    # Favicon filename. Defaults to `site_logo` if empty.
    "site_icon": "favicon.ico",
    # Logo filename.
    "site_logo": "logo_notext.svg",
    # CSS classes that are applied to the logo above, emptied to avoid class "img-circle"
    "site_logo_classes": "",
    # Sign-in form logo filename. Defaults to `site_logo` if empty.
    "login_logo": "img/opengis_powering_qfc.png",
    # Sign-in form welcome text.
    "welcome_sign": "Welcome to QFieldCloud",
    # Copyright on the footer.
    "copyright": "OPENGIS.ch",
    # Additional custom CSS file for the Django Admin pages.
    "custom_css": "css/admin.css",
}
