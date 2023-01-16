# Foodgram - Продуктовый помощник
Продуктовый помощник, с помощью которого вы можете публиковать рецепты, смотреть рецепты других авторов, добавлять рецепты в избранное и формировать "список покупок" со всеми ингредиентами выбранных рецептов.


Данные для подключения для проверки (будет изменено после принятия проекта)

- [Адрес тест сервера]: (http://51.250.91.216/)
```
Тестовый пользователь   
Логин: testadmin@gmail.com
Пароль: testadmin
```

![workflow](https://github.com/memphis94/foodgram-project-react/actions/workflows/foodgram_project_workflow.yml/badge.svg)



## Подготовка сервера и деплой проекта:
- Склонировать репозиторий себе:
```
git clone git@github.com:memphis94/foodgram-project-react.git
```
- Установить Docker на сервер
```
sudo apt install docker.io 
```
- Установить docker-compose с помощью оффициальной документации
```
https://docs.docker.com/compose/install/linux/
```
- Скопировать файлы docker-compose.yml и nginx.conf (Из папки infra, не забудьте поменять server_name на адрес ip вашего сервера)
```
scp docker-compose.yml nginx.conf username@ПУБЛИЧНЫЙ_IP_ВАШЕГО_СЕРВЕРА:/home/username/
- username - ваше имя на сервере
```
- Зарегистрироваться на DockerHub
```
https://hub.docker.com/
```
- Добавить в Github Actions репозитория с проектом следующие переменные (Settings --> Secrets and variables --> Actions):
```
DOCKER_USERNAME - логин на https://hub.docker.com/
DOCKER_PASSWORD - пароль на https://hub.docker.com/
HOST - публичный ip сервера
USER - имя на сервере
SSH_KEY - приватный ssh ключ (cat ~/.ssh/id_rsa)
PASSPHRASE - пароль, если ssh ключ им защищён
SECRET_KEY - секретный ключ от Django-проекта
DB_ENGINE - django.db.backends.postgresql
DB_NAME - postgres
POSTGRES_USER - postgres
POSTGRES_PASSWORD - postgres
DB_HOST - db
DB_PORT - 5432
```
- Если есть телеграм бот и нужны оповещения об отработке:
```
TELEGRAM_TO - id пользователя в телеграм (узнать у @userinfobot /start)
TELEGRAM_TOKEN - токен телеграм бота (@BotFather /mybots /API token)
```
- Если нет телеграм бота, то удалить из jobs - send message
```
  send_message:
    runs-on: ubuntu-latest
    needs: deploy
    steps:
    - name: send message
      uses: appleboy/telegram-action@master
      with:
        to: ${{ secrets.TELEGRAM_TO }}
        token: ${{ secrets.TELEGRAM_TOKEN }}
        message: ${{ github.workflow }} успешно выполнен!
```
- Сделать push репозитория и дождаться отработки workflow

- После успешной отработки выполнить миграции:
```
sudo docker-compose exec backend python manage.py migrate
```
- Создать суперпользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
```
- Создать статику:
```
sudo docker-compose exec backend python manage.py collectstatic --noinput
```
- Наполнить базу данных:
```
sudo docker compose exec backend python manage.py loaddata dump.json
```
