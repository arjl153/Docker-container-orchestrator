FROM python:3.6-alpine

# Define environment variable
ENV TEAM_ID=CC_030_049_056_057

# Creating working directory
RUN mkdir /code
WORKDIR /code

# Copying requirements
#COPY . /code/

ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

# Install any needed packages specified in requirements.txt
#RUN pip3 install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80
EXPOSE 22
EXPOSE 8000



CMD ["echo", "$ENV_VAR"]
