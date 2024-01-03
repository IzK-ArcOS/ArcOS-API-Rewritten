# start with ubuntu
FROM python:3.11.7

# install python3 and pip3
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

# copy ./orig into the container
COPY ./orig /

# switch to the cloned directory
WORKDIR /ArcOS-API-Rewritten

# list version
RUN python3 --version

# create venv
RUN python3 -m venv venv

# activate venv
RUN . venv/bin/activate

# install requirements
RUN pip3 install -r requirements.txt

# expose port 3333
EXPOSE 3333

# run the app
CMD ["python3", "./main.py"]