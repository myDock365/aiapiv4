FROM python:3.10.0

WORKDIR /apps

ADD . /apps

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python","main.py"]

