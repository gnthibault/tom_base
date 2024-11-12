FROM python:3.11

#EXPOSE 80
#ENTRYPOINT [ "/usr/local/bin/gunicorn", "tom_demo_base.wsgi", "-b", "0.0.0.0:80", "--access-logfile", "-", "--error-logfile", "-", "-k", "gevent", "--timeout", "300", "--workers", "2"]

ARG PORT=8000
ARG GOOGLE_CLOUD_PROJECT="tom-toolkit-dev-hxm"

ENV GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT
ENV PORT=$PORT
EXPOSE ${PORT}

WORKDIR /tom

# Install dependencies
COPY . /tom
RUN pip install --upgrade pip && pip install \
  poetry \
	--no-cache \
	--disable-pip-version-check
RUN poetry config virtualenvs.create false --local
RUN poetry install --no-interaction

# Install django app
WORKDIR /tom/mytom

# This has to be run manually, or using Procfile somewhere ...
# RUN poetry run python manage.py migrate
# This has to be run manually, or using Procfile somewhere ...
# RUN python manage.py collectstatic --noinput
# poetry run python manage.py runserver # Runs ...
RUN rm -f ./.env

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app


#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 myproject.wsgi:application

# gcloud auth login --update-adc
# echo "$(gcloud --project tom-toolkit-dev-hxm secrets versions access latest --secret django_settings)" > .env
# docker buildx build --build-arg GOOGLE_CLOUD_PROJECT="tom-toolkit-dev-hxm" --build-arg SETTINGS_NAME=django_settings -t europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app .
# docker buildx build --platform linux/arm64/v8,linux/amd64 --build-arg GOOGLE_CLOUD_PROJECT="tom-toolkit-dev-hxm" --build-arg SETTINGS_NAME=django_settings -t europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app .

# docker tag europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app:test1
# docker run -it -e PORT=8080 -e GOOGLE_CLOUD_PROJECT="tom-toolkit-dev-hxm" -p 8080:8080 --rm europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app

# docker push europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app:test
# docker run -it -e PORT=8080 -p 8080:8080 --rm europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app:test


#CMD [ \
#	"gunicorn", \
#	"--bind=0.0.0.0:${PORT}", \
#	"--worker-class=gevent", \
#	"--workers=1", \
#       "--threads=8", \
#	"--timeout=300", \
#	"--access-logfile=-", \
#	"--error-logfile=-", \
#	"myproject.wsgi:application" \
#	]
