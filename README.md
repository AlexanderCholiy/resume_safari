# Resume Safari

**Resume Safari** — pet-проект на Django, представляющий собой платформу для размещения и просмотра резюме.\
Основной функционал реализован через REST API с возможностью интеграции с любыми frontend-решениями.


## О проекте

Проект создан для практики и углубления навыков работы с Django, Django REST Framework, авторизацией, Docker, CI/CD, а также фронтендом на HTML/CSS и JavaScript.

- 📄 Пользователи могут публиковать, редактировать и удалять свои резюме.
- 🔐 Аутентификация через JWT, активация по email.
- 🔍 Поиск и фильтрация по позициям, городам, категориям.
- ⚙️ API-доступ для управления личными данными.
- 📚 Документация API в формате Swagger и Redoc.


## Технологический стек

- **Backend**: Python, Django, Django REST Framework
- **Frontend**: HTML, CSS, JavaScript (минимально)
- **БД**: PostgreSQL
- **API-документация**: Swagger, Redoc
- **Аутентификация**: JWT (Djoser)
- **Тестирование**: Pytest
- **CI/CD**: GitHub Actions
- **Контейнеризация**: Docker, Docker Compose
- **Reverse Proxy**: Nginx

  
## Установка и запуск

### 1. Клонируйте репозиторий
```
git clone https://github.com/AlexanderCholiy/api_yamdb.git
```
> bash
### 2. Перейдите в корневую папку
```
cd resume_safari
```
> bash
### 3. Установите и активируйте виртуальное окружение и зависимости
- Установка виртуального окружения (версия python 3.13):
```
python3.13 -m venv venv
```
- Активация виртуального окружения для Windows:
```
. .\venv\Scripts\activate
```
- Активация виртуального окружения для Linux или MacOS:
```
. ./venv/bin/activate
```
- Установите зависимости:
```
pip install -r requirements.txt
```
> bash
### 4. Создайте и отредактируйте файл с переменными окружения
- Создайте .env файл в корне проекта:
```
touch .env
```
- Отредактируйте .env файл и добавьте туда WEB_SECRET_KEY, WEB_EMAIL_LOGIN, WEB_EMAIL_PSWD:
```
nano .env
```
> bash
### 5. Отредактируйте config файл под ваш проект
```
nano resume\core\config.py
```
> bash
### 7. Временная база данных SQLite вместо PostgreSQL
- В файле settings.py отредактируйте DATABASES:
```
nano resume\resume\settings.py
```
> bash
### 6. Примените миграции и создайте суперпользователя
```
cd resume
```
```
python manage.py migrate
```
```
python manage.py createsuperuser
```
> bash
### 7. Добавьте данные в БД с помощью managment команды
```
python.exe manage.py data_2_db
```
> bash
### 8. Запустите сервер
```
python manage.py runserver
```
> bash
### 9. В новом терминале активируйте виртуальное окружение и запустите отправку email
```
python.exe manage.py send_email_queue
```
> bash

## Запуск с помощью Docker
```
docker-compose up --build
```


## Доступ
- Главная страница: http://localhost/
- Swagger UI: http://localhost/resume-safari/swagger/
- ReDoc: http://localhost/resume-safari/redoc/
- Администрирование: http://localhost/admin/


## Управление данными через API

### 🛠 Хард скиллы
GET /api/v1/hard-skills/ — Список скиллов c фильтрацией по названию
_CRUD операции только staff-пользователи могут добавлять/изменять/удалять_

### 🌿 Софт скиллы
GET /api/v1/soft-skills/ — Список скиллов c фильтрацией по названию
_CRUD операции только staff-пользователи могут добавлять/изменять/удалять_

### 🌍 Геолокации
GET /api/v1/locations/ — Список локаций с фильтрацией по странам и городам
_CRUD операции только staff-пользователи могут добавлять/изменять/удалять_

### 💼 Должности
GET /api/v1/positions/ — Список должностей с фильтрацией по категориям и названиям
_CRUD операции только staff-пользователи могут добавлять/изменять/удалять_

### 📧 Регистрация
POST /api/v1/auth/register/ — Регистрация нового пользователя.
_На почту отправляется ссылка для активации аккаунта._

### 🔐 Авторизация
POST /api/v1/token/ — Получение JWT-токена по username и паролю.

POST /api/token/refresh/ — Обновление access токена по refresh токену.

### 👤 Управление текущим пользователем
GET	/api/v1/me/ — Получение информации о себе (id, username, email).

PATCH	/api/v1/me/ — Частичное обновление профиля (username, email).

DELETE	/api/v1/me/ — Удаление аккаунта.

POST /api/v1/password/change/ — Смена пароля текущим авторизованным пользователем.

GET	/api/v1/users/<id>/ — Получение данных авторизованного пользователя по его ID.

PATCH	/api/v1/users/<id>/ — Частичное обновление данных авторизованного пользователя по его ID.

### 📃 Резюме
GET /api/v1/resumes/ — список доступных резюме
_Анонимные пользователи видят только опубликованные._\
_Авторизованные — свои черновики и активные._

POST /api/v1/resumes/ — создать резюме

PATCH /api/v1/resumes/<slug>/ — обновить резюме

DELETE /api/v1/resumes/<slug>/ — удалить резюме


## Рекомендации
_Проверять и отлаживать работу API удобно через **Postman**._\
_Эта программа умеет отправлять запросы, анализировать ответы и сохранять запросы для повторного применения в будущем._


### Автор
**Чолий Александр** [[Telegram](https://t.me/alexander_choliy)]
