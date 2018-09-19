FROM python:3.7
ENV PYTHONUNBUFFERED 1

# Use pipenv
RUN pip install -U pipenv

# Allows docker to cache installed dependencies between builds
COPY ./Pipfile ./Pipfile.lock /
RUN pipenv install --dev --system

# Adds our application code to the image
COPY . code

RUN cd /code && pip install -e .

WORKDIR code

EXPOSE 8000

RUN mkdir -p /root/.jupyter && \
    echo "c.NotebookApp.token = ''" > /root/.jupyter/jupyter_notebook_config.py

# Migrates the database, uploads staticfiles, and runs the production server
CMD ./manage.py migrate && \
    ./manage.py collectstatic --noinput && \
    gunicorn --bind 0.0.0.0:$PORT --access-logfile - django_luigi.wsgi:application
