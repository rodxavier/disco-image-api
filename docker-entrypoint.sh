# Run the migrations
python manage.py migrate

python manage.py loaddata fixtures/initial_data.json

python manage.py runserver 0.0.0.0:${APP_PORT}
