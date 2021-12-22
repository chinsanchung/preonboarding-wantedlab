# syntax=docker/dockerfile:1

FROM tiangolo/uwsgi-nginx-flask:python3.8

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]