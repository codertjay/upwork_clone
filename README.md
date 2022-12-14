### Activation Virtualenv

`pip -h`
`pip install virtualenv`
`virtualenv env`

## if you are using windows

`env\Scripts\activate.bat`

### else

`source env/bin/activate`

### installing packages ( make sure you are in the root folder)

`pip install -r requirements.txt`

### Run Task on Windows

- (If on Mac ) celery -A instasaw_api worker --loglevel=info
- (If on Windows) celery -A instasaw_api worker -l info --pool=solo

### open another tab

- `celery -A instasaw_api beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler`

## Set up the environment variables

-`Use the env--sample to create your .env file and set it up`

## Run the Django server

Make migrations

- `python manage.py makemigrations`

Migrate

- `python manage.py migrate`

Run the redis server .If you are on windows you have to use wsl to install redis
after install redis you run but make sure you run this in another tab

- `redis-server`

Run the Django server

- `python manage.py runserver`


Or Use docker instead of the

- `docker-compose up`