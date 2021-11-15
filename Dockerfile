# set base image (host OS)
FROM python:3

# copy the dependencies file to the working directory
COPY requirements.txt /app/

# set the working directory in the container
WORKDIR /app

# install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# copy the content to the working directory
COPY . .

# command to run on container start
CMD [ "python", "./excelLoading.py" ]