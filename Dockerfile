FROM python:2.7

LABEL maintainer="Sanchit Jaiswal"

WORKDIR /app

COPY ./techtrends .

RUN pip install -r requirement.txt

RUN python init_db.py

EXPOSE 3111

CMD [ "python", "app.py"]