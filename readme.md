# Сервис определения тональности
Для работы требуется python версии 2.7.

Команда для запуск сервиса:
	python start_servers.py

Команда для остановки сервиса:
	python stop_servers.py

После запуска сервис доступен по адресу http://127.0.0.1:8081/

# Список модулей в папке src/
- get_sentiment_server -- сервер для определения тональности одного документа
- request_processing -- сервер для обработки запроса
- web_ui -- веб интерфейс
- sql_model -- модуль базы данных