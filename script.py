import os

# Generate default Dockerfile
def generate_dockerfile():
    with open("Dockerfile", "w") as f:
        f.write("""
FROM python:3.9-alpine

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the rest of the application code
COPY . .

# Run the command to start the Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
        """)

# Generate default docker-compose
def generate_docker_compose():
    with open("docker-compose.yml", "w") as f:
        f.write("""
version: '3'

services:
  db:
    image: postgres:12
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: mydbuser
      POSTGRES_PASSWORD: mysecretpassword
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
        """)

# Generate default Nginx script
def generate_nginx_script():
    with open("nginx.conf", "w") as f:
        f.write("""
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
        """)

if __name__ == "__main__":
    generate_dockerfile()
    generate_docker_compose()
    generate_nginx_script()
