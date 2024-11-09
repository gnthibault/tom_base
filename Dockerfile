FROM python:3.11
#ARG PORT=8000
ENV PORT $PORT
EXPOSE ${PORT}

WORKDIR /tom

COPY requirements.txt .

RUN pip install \
	--no-cache \
	--disable-pip-version-check \
	--requirement requirements.txt

COPY . .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 myproject.wsgi:application
# docker run -it -e PORT=8080 -p 8080:8080 --rm europe-west1-docker.pkg.dev/tom-toolkit-dev-hxm/remote-observatory-tom-repo/tom-demo:test

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
