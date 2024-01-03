# start with a base image
FROM python:3.11.7-alpine

# copy the main directory into the container
COPY ./ /ArcOS

# switch to the copied directory
WORKDIR /ArcOS

# create venv
RUN python3 -m venv venv

# activate venv
RUN . venv/bin/activate

# install requirements
RUN pip3 install -r requirements.txt

# expose port 3333
EXPOSE 3333

# launch the backend
CMD ["python3", "./main.py"]