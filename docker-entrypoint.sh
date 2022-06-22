# Run the migrations
python manage.py migrate

python manage.py loaddata

python manage.py runserver 0.0.0.0:${APP_PORT}
