FROM python:3.11

#EXPOSE 80
#ENTRYPOINT [ "/usr/local/bin/gunicorn", "tom_demo_base.wsgi", "-b", "0.0.0.0:80", "--access-logfile", "-", "--error-logfile", "-", "-k", "gevent", "--timeout", "300", "--workers", "2"]

ARG PORT=8000
# ARG GOOGLE_CLOUD_PROJECT="tom-toolkit-dev-hxm"
#
# ENV GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT
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

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 mytom.wsgi:application


#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app

# gcloud auth login --update-adc
# gcloud auth configure-docker europe-west1-docker.pkg.dev
# echo "$(gcloud --project tom-toolkit-dev-hxm secrets versions access latest --secret django_settings)" > .env
# docker buildx build --build-arg GOOGLE_CLOUD_PROJECT="tom-toolkit-dev-hxm" --build-arg SETTINGS_NAME=django_settings -t europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app .
# docker buildx build -t europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app .

# docker buildx [Errno 28] No space left on device
# If you are using Docker Desktop on Mac, go to Preferences and increase the Disk image size

# docker tag europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app:test1
# docker run -it -e PORT=8080 -e GOOGLE_CLOUD_PROJECT="tom-toolkit-dev-hxm" -p 8080:8080 --rm europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app

# docker push europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app:test
# docker run -it -e PORT=8080 -p 8080:8080 --rm europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app:test

## Cloudrun deployment sample
# gcloud run deploy tom-toolkit-instance-dev-b614bde8 --image europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom_app:test1 --update-labels ^,^managed-by=manual_deploy,commit-sha=XXXXXXXXXXXXXXX --format json --region europe-west1 --project tom-toolkit-dev-hxm
# gcloud run services proxy tom-toolkit-instance-dev-b614bde8 --port=8080 --project=tom-toolkit-dev-hxm --region=europe-west1
# cloud-sql-proxy --auto-iam-authn tom-toolkit-dev-hxm:europe-west1:tom-toolkit-instance-dev-ae78f371


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



# # Generate workable requirements.txt from Poetry dependencies
# FROM​ python:3-slim as requirements
#
# RUN​ apt-get install -y --no-install-recommends build-essential gcc
# RUN​ python -m pip install --no-cache-dir --upgrade poetry
#
# COPY​ pyproject.toml poetry.lock ./
# RUN​ poetry export -f requirements.txt --without-hashes -o /src/requirements.txt
#
# #​ Final app image
# FROM​ python:3-slim as webapp
#
# #​ Switching to non-root user appuser
# RUN​ adduser appuser
# WORKDIR​ /home/appuser
# USER​ appuser:appuser
#
# #​ Install requirements
# COPY​ --from=requirements /src/requirements.txt .
# RUN​ pip install --no-cache-dir --user -r requirements.txt
# I highly recommend learning more about multi stage builds like this. Everything installed in the requirements layer is erased afterward, including all of Poetry's dependencies, leading to a smaller image size. And, you can run the program in the final image using simpler python commands, with all your requirements installed to the "system" python in the container.
#
# Edit: for those interested, Poetry discussion on Docker best practices can be found here: https://github.com/python-poetry/poetry/discussions/1879
