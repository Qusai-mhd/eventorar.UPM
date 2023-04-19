"""
Django settings for Eventorar project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os
# import certifi
# import ssl


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-aa9a8fv^_-b)@_dtd#(xn7+g%*b9t(zg)e8^aku3&)z-r7-8y#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'event',
    'authentication',
    'celery',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Eventorar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Eventorar.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eventorar',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': '',
        'PORT':'3306',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'bd2gghjmsxdjhsaalruq',
#         'HOST': 'bd2gghjmsxdjhsaalruq-mysql.services.clever-cloud.com',
#         'USER': 'uwqk25hpyivbvxyy',
#         'PASSWORD': 'cVxEc8G7rT2fhoDIABZY',
#         'PORT':'3306',
#     }
# }

MAILJET_API_KEY ='a65adf0e9cca920b641f1be4b970942b'
MAILJET_API_SECRET ='f794fe9f60febe1155b252e6caf03c69'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'in-v3.mailjet.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = MAILJET_API_KEY
EMAIL_HOST_PASSWORD = MAILJET_API_SECRET

# EMAIL_USE_SSL = False
# ssl._create_default_https_context = ssl._create_unverified_context

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = (
  os.path.join(BASE_DIR, 'event/static/'),
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL='authentication.CustomUser'

AUTHENTICATION_BACKENDS = [    'authentication.authentication.EmailBackend',]


#LOGIN_REDIRECT_URL = 'eventorar/event'


# # Set the directory where the QR code images will be saved
# QR_CODE_DIR = os.path.join(BASE_DIR, 'event/qr_codes')

# # Set the base URL for accessing the QR code images
# QR_CODE_URL = '/media/qr_codes/'

# Set the secret key used for encrypting and decrypting the QR code data
QR_CODE_KEY = 'e-oql5VK5n8wUOtbeYtxCWcAdCQQVHWkWViilOJC29A='


# Celery settings

# set the celery broker url
CELERY_BROKER_URL = 'redis://localhost:6379/0'
# set the celery result backend
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
# set the celery timezone
CELERY_TIMEZONE = 'UTC'