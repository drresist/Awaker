FROM python:3.11-slim-buster
LABEL authors="maximfesenko"


WORKDIR /app
COPY . .

RUN make install-requirements


ENTRYPOINT ["python3", "src/main.py"]