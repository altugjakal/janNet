python main.py &


exec gunicorn --bind 0.0.0.0:8080 --workers 4 wsgi:app