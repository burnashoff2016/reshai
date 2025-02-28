from django_hosts import patterns, host

host_patterns = patterns('',
    # Основной домен – mainapp
    host(r'www', 'ReshAI.urls_app', name='www'),
    host(r'^$', 'ReshAI.urls_app', name='root'),  # для голого resh-ai.ru, если нужно
    # Поддомен – chatapp
    host(r'app', 'ReshAI.urls_main', name='app'),
)
