FROM python:3.7

ADD /requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -q -r requirements.txt

# Run the image as a non-root user
RUN useradd --create-home --shell /bin/bash webuser
USER webuser

ADD . /app

# CMD bash -c "alembic upgrade head && python run.py"
CMD flask run --host=0.0.0.0
#CMD bash -c "python create_database.py && flask run --host=0.0.0.0"
