FROM python:3.12-slim

WORKDIR /app

COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m" , "src.main"]
