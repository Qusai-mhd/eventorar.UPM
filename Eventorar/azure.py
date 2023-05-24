from .settings import *

# this is so we can generate URLs for routes hosted by our app when it is hosted
# on Azure or any other reverse proxy.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# replace this with your deployed app's public URL
ALLOWED_HOSTS = ['eventorar-prod.azurewebsites.net']
# don't allow debug on prod
# DEBUG = False
# SSL
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
