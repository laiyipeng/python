cd /home
#python manage.py
/usr/bin/gunicorn -c /home/gunicorn.conf deploy:app