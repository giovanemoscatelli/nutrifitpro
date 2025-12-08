from pathlib import Path
import os
import dj_database_url # Importante para o banco de dados na nuvem

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SEGURANÇA: Chave secreta (em produção real, isso ficaria em variável de ambiente)
SECRET_KEY = 'django-insecure-sua-chave-secreta-aqui'

# MODO DE DEBUG
# Se estiver no Render, vira False (Seguro). Se estiver no PC, vira True (Desenvolvimento).
RENDER = os.environ.get('RENDER')
DEBUG = not RENDER

# PERMISSÃO DE ACESSO
ALLOWED_HOSTS = ['*'] # Libera o acesso para o Render

# APLICATIVOS INSTALADOS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core', # Seu app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- NOVIDADE: Gerencia arquivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nutrifit_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nutrifit_backend.wsgi.application'

# BANCO DE DADOS
# Se tiver no Render (DATABASE_URL), usa PostgreSQL. Se não, usa SQLite.
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        conn_max_age=600
    )
}

# VALIDAÇÃO DE SENHA
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNACIONALIZAÇÃO
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ARQUIVOS ESTÁTICOS (CSS, Imagens, JS)
STATIC_URL = 'static/'

if not DEBUG:
    # Configuração para Produção (Render)
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# LOGIN E LOGOUT
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

# ID
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'