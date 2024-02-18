FROM python:3.11
# don't create .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# don't docker buffering
ENV PYTHONUNBUFFERED 1
# set work directory
WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
