FROM python:3
MAINTAINER Chen Alkabets "chenchuk@gmail.com"

COPY ./app/requirements.txt /requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app
CMD [ "python", "./pokerbot.py" ]

