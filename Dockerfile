FROM python:3

WORKDIR /app 
COPY . /app 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uncomment the line below if you want to install the sumologic-cse package from PyPI rather than the local directory
#RUN pip install sumologic-cse
