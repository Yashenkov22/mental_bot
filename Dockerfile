FROM python:3.10

EXPOSE 80

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt

COPY . .
