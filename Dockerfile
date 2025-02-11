FROM python:3.10-buster

# Ensure Python doesn't buffer output (useful for debugging)
ENV PYTHONUNBUFFERED=1
RUN /usr/local/bin/python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple

# Install MySQL client
RUN apt-get update && apt-get install -y default-mysql-client

# Create and set the working directory
RUN mkdir /code
WORKDIR /code

COPY requirements-prd.txt /code/
COPY requirements-dev.txt /code/   

RUN pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements-prd.txt
RUN pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements-dev.txt 

COPY . /code/

