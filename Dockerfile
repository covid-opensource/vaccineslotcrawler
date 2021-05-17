FROM python:3

# Creating Application Source Code Directory
RUN mkdir -p /cowin

# Setting Home Directory for containers
WORKDIR /cowin

# Installing python dependencies
COPY requirements.txt /cowin
RUN pip install --no-cache-dir -r /cowin/requirements.txt

# Copying src code to Container
COPY /src /cowin

# Application Environment variables
# ENV APP_ENV development

# Exposing Ports
EXPOSE 5035

# Setting Persistent data
VOLUME ["/cowin-data"]

# Running Python Application
# CMD ["python", "app.py"]
