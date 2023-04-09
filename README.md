# Тестовое задание Баланс Пользователей
В данном репозитории представлен тестовый API сервиса по работе с балансами.
## Примеры использования API 
- Create User: Создать пользователя с именем Artem.
    ```
    curl -X POST -H "Content-Type: application/json" -d '{"name": "Artem"}' 'http://localhost:8000/v1/user'
    ```
- Get User: Получить данные о пользователе с id `1`.
    ```
    curl -X GET 'http://localhost:8000/v1/user/1'
    ```
- Get User Balance: Узнать какой был баланс у пользователя в дату `2023-10-30T00:00:00.00000000`
    ```
    curl -X GET 'http://localhost:8000/v1/user/1/balance?date=2023-10-30T00:00:00.00000000'
    ```
- Add Transaction (Deposit): Пополнить баланс пользователя с id `1` на сумму `100`.
    ```
    curl -X POST -H "Content-Type: application/json" -d '{"uuid": "$(uuidgen)", "type": "DEPOSIT", "amount": "100", "user_id": "1", "timestamp": "$(date +%FT%H-%M-%S)"}' 'http://localhost:8000/v1/transaction' 
    ```
- Add Transaction (Withdraw): Снять с баланса пользователя с id = `1` сумму равную `50`.
    ```
    curl -X POST -H "Content-Type: application/json" -d '{"uuid": "$(uuidgen)", "type": "WITHDRAW", "amount": "50", "user_id": "1", "timestamp": "$(date +%FT%H-%M-%S)"}' 'http://localhost:8000/v1/transaction' 
    ```
- Get Transaction: Получить данные о транзакции с id `ea3015b1-c25c-47e5-beb7-2679ac7c89a7`
    ```
    curl -X GET 'http://localhost:8000/v1/transaction/ea3015b1-c25c-47e5-beb7-2679ac7c89a7'
    ```

## Setup
Следуйте шагам описанными ниже, чтобы поднять окружение на локальной машине.

### Dependencies
- python 3.10
- uvloop 0.17.0
- aiohttp 3.8+
- SQLAlchemy 2.0+
- asyncpg 0.27.0
- pydantic
- Все python зависимости содержатся в [`app/requirements.txt`](https://github.com/0105artem/test-balance/blob/main/app/requirements.txt)
            

## Запуск без Docker
Для работы данной установки понадобятся ссылка для подключения к базе данных PostgreSQL.
1. В терминале откройте директорию `./app`
2. Создайте `.env` файл, скопировав в него содержимое файла `app/.env.sample`. Измените переменную DATABASE_URI в соответствии с учетными данными вашей БД:
3. Создайте виртуальное окружение, используя следующую команду
    ```shell script
    $ python3 -m venv venv
    ```
4. Активируйте виртуальное окружение
    Linux:
    ```shell script
    $ source /venv/bin/active
    ```
    Windows:
    ```shell script
    > ./venv/bin/active
    ```
5. Убедитесь что ваше виртуальное окружение активно и установите все необходимые зависимости следующей командой:
    ```shell script
    $ pip install -r requirements.txt
    ```
6. Запустите API из директории `test-balance` командой ниже:
    ```shell script
    $ python -m app
    ```
7. Запустите тесты, находясь в директории `test-balance`
    ```shell script
    $ pytest -V
    ```

## Дополнительно
 - Учесть, что сервис будет запускаться в k8s — Написаны `Docker` и `docker-compose.yml` файлы
 - Учтено, что архитектура гарантирует обработку транзакции ровно 1 раз. Это реализовано проверкой нахождения текущего ID транзакции в базе данных. Если оно найдено, то транзакция не будет выполнена. Но это накладывает дополнительное время и ресурсы, затраченные на поиск в базе данных. В будущем, при таком способе необходимо будет сделать индексацию таблицы с транзакциями для более быстрого поиска.
 - Реализовать уведомление других сервисов при изменении баланса пользователя можно с помощью очередей, например, RabbitMQ.
 - Можно применить Prometheus и Grafana для контроля качества сервиса. Например, можно отследить, если запросы пользователя стали выполняться медленнее.
 - гарантировано, что баланс пользователя не может быть отрицательным

## Обратная связь
- 0105artem@gmail.com
- https://t.me/artemk0rn1lov
