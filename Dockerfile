FROM python:alpine3.10
RUN mkdir /app
COPY main.py /app
COPY requirements.txt /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD python main.py
