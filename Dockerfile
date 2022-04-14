FROM python:3.9.6-slim-buster
ENV . /app
WORKDIR /app
COPY . .

# Install production dependencies.
RUN pip install -r requirements.txt