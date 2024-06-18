FROM python

RUN apt-get update &&\
    apt-get -y install cmake &&\
    pip install flask

WORKDIR /app

COPY app.py /app/

CMD exec python -u app.py