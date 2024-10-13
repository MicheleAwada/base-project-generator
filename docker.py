def get_dockercompose(traefik_path_name, domain_name,):
    return \
f"""version: "3.4"
services:
  backend:
    restart: always
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file:
      - ./backend/config/.env
    expose:
      - 8080
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8080
    volumes:
      - media:/app/media
      - static:/app/static
    depends_on:
      - postgres
    networks:
      - internal
  postgres:
    image: postgres:alpine
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    env_file:
      - ./backend/config/.env
    networks:
      - internal
  nginx:
    image: nginx:alpine
    restart: always
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/dist:ro
      - media:/media:ro
      - static:/static:ro
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.{traefik_path_name}.middlewares=to-https@file"
      - "traefik.http.routers.{traefik_path_name}.rule=Host(`api.{domain_name}`) || Host(`{domain_name}`) || Host(`www.{domain_name}`)"
      - "traefik.http.routers.{traefik_path_name}.entrypoints=web"
      - "traefik.http.routers.{traefik_path_name}-secure.rule=Host(`api.{domain_name}`) || Host(`{domain_name}`) || Host(`www.{domain_name}`)"
      - "traefik.http.routers.{traefik_path_name}-secure.middlewares="
      - "traefik.http.routers.{traefik_path_name}-secure.tls.certresolver=letsencrypt"
      - "traefik.http.routers.{traefik_path_name}-secure.tls=true"
      - "traefik.http.routers.{traefik_path_name}-secure.entrypoints=web-secure"
    networks:
      - internal
      - traefikproxy
volumes:
  static:
  media:
  postgres_data:


networks:
  internal:
  traefikproxy:
    name: traefikproxy
    external: true"""