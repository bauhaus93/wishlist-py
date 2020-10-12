FROM python:rc-slim-buster

RUN useradd wishlist

WORKDIR /home/wishlist
COPY requirements.txt ./
RUN python -mvenv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn
RUN mkdir db

COPY app app
COPY migrations migrations
COPY config.py wishlist.py scripts/run.sh .env ./

RUN chmod +x run.sh
RUN chown -R wishlist:wishlist ./
USER wishlist

EXPOSE 5000
ENTRYPOINT ./run.sh
