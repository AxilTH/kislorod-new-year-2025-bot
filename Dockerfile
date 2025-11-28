FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# install build deps for some packages if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy project
COPY . /app

# default command is overridden by docker-compose for api and bot
CMD ["python", "run.py"]
