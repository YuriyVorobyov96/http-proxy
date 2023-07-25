Установка зависимостей:
- pip3 install -r requirements.txt

Запуск серверной утилиты для разбора (парсинга) HTTP-запросов напрямую:
- python3 http_proxy.py

Запуск серверной утилиты для разбора (парсинга) HTTP-запросов с помощью Docker:
- docker build -t http_proxy .
- docker run -p 3000:3000 http_proxy

Роутинг:
- GET /help - получение информации по работе утилиты
- GET /send-request - отправка запроса для обработки

Инструкция:
Для отправки запроса используется маршрут GET "/send-request" с JSON телом

Поля в JSON теле:
target - маршрут - ОБЯЗАТЕЛЬНЫЙ ПАРАМЕТР
method - метод запроса (GET|POST|PUT|PATCH|DELETE) - ОБЯЗАТЕЛЬНЫЙ ПАРАМЕТР
headers - заголовки - ОПЦИОНАЛЬНЫЙ ПАРАМЕТР
payload - тело запроса - ОПЦИОНАЛЬНЫЙ ПАРАМЕТР
param - имя параметра из тела запроса для замены на рандомное значение и модификации запроса - ОПЦИОНАЛЬНЫЙ ПАРАМЕТР

Пример формата JSON тела:
```
{
    "target": "https://blabla.free.beeceptor.com/my/api/path",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json"
    },
    "payload": {
        "data": "Hello Beeceptor"
    },
    "param": "data"
}
```

Пример запроса:
```
curl --location --request GET 'localhost:3000/send-request' \
--header 'Content-Type: application/json' \
--data '{
    "target": "https://blabla.free.beeceptor.com/my/api/path",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json"
    },
    "payload": {
        "data": "Hello Beeceptor",
        "data2": 123,
        "data3": true,
        "data4": 123.2344,
        "data5": {
            "key1": "value1",
            "key2": "value2"
        },
        "data6": [
            1,
            "value",
            123.45,
            true,
            [
                1,
                2,
                3
            ],
            {
                "key1": "value1",
                "key2": "value2"
            }
        ]
    },
    "param": "data6"
}'
```
