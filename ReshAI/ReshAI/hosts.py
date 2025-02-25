from django_hosts import patterns, host

host_patterns = patterns('',
                         # 1) Основной домен, например, "resh-ai.ru"
                         host(r'(www|)', 'ReshAI.urls_main', name='www'),

                         # 2) Поддомен "app.resh-ai.ru"
                         host(r'app', 'ReshAI.urls_app', name='app'),
                         )
