FROM python:3.9

#EXPOSE 80
#ENTRYPOINT [ "/usr/local/bin/gunicorn", "tom_demo_base.wsgi", "-b", "0.0.0.0:80", "--access-logfile", "-", "--error-logfile", "-", "-k", "gevent", "--timeout", "300", "--workers", "2"]

WORKDIR /tom-demo

COPY . /tom-demo
RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false --local
RUN poetry install --no-interaction

WORKDIR /tom-demo

RUN python manage.py collectstatic --noinput

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
