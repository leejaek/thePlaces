FROM python:3.8

WORKDIR /usr/sec/app 

COPY requirements.txt ./

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

# CMD ["python", "./manage.py", "runserver", "--host=0.0.0.0", "-p 8080"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "theplaces.wsgi:application"]

EXPOSE 8000
