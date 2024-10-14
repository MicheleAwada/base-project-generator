def get_nginx(frontend_domain_name, backend_domain_name, opposite_frontend_domain_name,):
    return \
"""events{}
http {
include mime.types;

upstream to_backend {
    server backend:8080;
}

server {
    listen 80;
    server_name """+frontend_domain_name+""";


    root /dist;
    location / {
        try_files $uri /index.html;
    }

}
server {
    listen 80;
    server_name """+frontend_domain_name+""";


    return 301 https://"""+opposite_frontend_domain_name+"""$uri;
}
server {
    listen 80;
    server_name """+backend_domain_name+""";
    client_max_body_size 100M;

    location / {
        proxy_pass http://to_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /media/ {
        alias /media/;
    }
    location /static/ {
        alias /static/;
    }

}
}"""