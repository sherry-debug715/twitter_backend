FROM python:3.10-buster
ENV PYTHONUNBUFFERED=1
RUN /usr/local/bin/python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple
RUN apt-get update && apt-get install -y default-mysql-client
RUN mkdir /code
WORKDIR /code
COPY requirements-prd.txt /code/
RUN pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements-prd.txt
COPY . /code/

