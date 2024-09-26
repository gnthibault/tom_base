FROM python:3.11

#EXPOSE 80
#ENTRYPOINT [ "/usr/local/bin/gunicorn", "tom_demo_base.wsgi", "-b", "0.0.0.0:80", "--access-logfile", "-", "--error-logfile", "-", "-k", "gevent", "--timeout", "300", "--workers", "2"]


WORKDIR /tom_deploy

# Install dependencies
COPY . /tom_deploy
RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false --local
RUN poetry install --no-interaction

# Install django app
WORKDIR /tom_deploy/mytom
RUN poetry run python manage.py migrate # Actually apply the migrations generated at the makemigrations step
RUN python manage.py collectstatic --noinput
#poetry run python manage.py runserver # Runs ...

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
