FROM python:3.12-rc-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY http_proxy.py http_proxy.py

EXPOSE 3000

CMD [ "python3", "http_proxy.py" ]
