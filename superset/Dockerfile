FROM apache/superset:latest

USER root

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir psycopg2-binary

USER superset