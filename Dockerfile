FROM python:3

ADD test.py /
COPY pokerbot.py db.py poker.db credentials.py requirements.txt /
RUN pip install -r requirements.txt

CMD [ "python", "./pokerbot.py" ]
