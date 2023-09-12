FROM python:3.8-slim

RUN apt-get update && apt-get install -y libpq-dev postgresql-client gcc 

WORKDIR /src

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

ENTRYPOINT ["streamlit", "run", "streamlit/Main.py", "--server.port=8501", "--server.address=0.0.0.0"]

EXPOSE 8501