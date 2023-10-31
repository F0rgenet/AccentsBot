FROM python:3.10

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y sqlite3
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "sqlite3 /projects/Accents/databases/database.db & python main.py"]