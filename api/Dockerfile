FROM python:3.9.2-slim

WORKDIR /app

COPY requirements.txt $WORKDIR
RUN pip install -r requirements.txt

COPY . $WORKDIR

EXPOSE 5000
CMD ["./start.sh"]
