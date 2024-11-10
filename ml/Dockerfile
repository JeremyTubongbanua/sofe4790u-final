FROM ubuntu:18.04

RUN apt-get update && apt-get upgrade -y

WORKDIR /app

COPY . .

RUN apt-get install -y python3 python3-pip

RUN pip3 install -r requirements.txt

CMD ["/bin/bash"]