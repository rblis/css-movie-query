FROM python:3.13-slim

WORKDIR /app

# Install  dependencies
RUN pip install --no-cache-dir \
    pydantic==2.11.4

COPY movie_query.py imdb_top_1000.csv ./

ENTRYPOINT ["python", "movie_query.py"]