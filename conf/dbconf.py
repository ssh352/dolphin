dbconf = {
    'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
    'NAME': 'tf2',                      # Or path to database file if using sqlite3.
    # The following settings are not used with sqlite3:
    'USER': 'root',
    'PASSWORD': '',
    'HOST': 'localhost',                     # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
    'PORT': '',                     # Set to empty string for default.
    'OPTIONS': { 'init_command': 'SET storage_engine=INNODB,character_set_connection=utf8,collation_connection=utf8_unicode_ci' },
}
