# Use the official Python image as a base image
FROM python:3.11-slim

# Set environment variables
ENV OW_API=your_openweathermap_api_key
ENV TG_BOT_API=your_telegram_bot_api_key
ENV CHAT_ID=your_telegram_chat_id

# Create and set the working directory
WORKDIR /app

# Copy the application files into the container
COPY main.py /app/
COPY birthdays.csv /app/
COPY icons.json /app/
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["python", "main.py"]
