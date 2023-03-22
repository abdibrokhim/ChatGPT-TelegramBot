# Base image
FROM python:3.9-slim-buster

# Set the working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/abdibrokhim/chatgptbot.git
RUN pip install -r chatgptbot/requirements.txt

# Expose the ports that the web server and bot will use
EXPOSE 8000 8443

# Set the entrypoint
CMD ["bash", "-c", "python chatgptbot/manage.py runserver 0.0.0.0:8000 & python chatgptbot/bot.py"]
