FROM python:3.11-slim


RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    supervisor \
    nginx \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r nginx && useradd -r -g nginx nginx

RUN mkdir -p /etc/nginx/certs && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/certs/nginx.key \
    -out /etc/nginx/certs/nginx.crt \
    -subj "/C=UA/ST=State/L=City/O=Organization/OU=Unit/CN=localhost"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY nginx.conf /etc/nginx/sites-available/default

RUN mkdir -p /app/logs && chown nginx:nginx /app/logs

EXPOSE 80 443 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
