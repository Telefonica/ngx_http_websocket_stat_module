ARG NGINX_VERSION=1.25.4

# Build stage
FROM nginx:${NGINX_VERSION}-alpine AS builder

ARG NGINX_VERSION=1.25.4

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    g++ \
    make \
    pcre-dev \
    libressl-dev \
    zlib-dev \
    linux-headers \
    curl \
    gnupg \
    libxslt-dev \
    gd-dev \
    geoip-dev

# Create source directories
RUN mkdir -p /usr/src/nginx /usr/src/module

# Download nginx source
RUN curl -fSL https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz -o nginx.tar.gz \
    && tar -xzC /usr/src/nginx -f nginx.tar.gz --strip-components=1

# Copy module source
COPY . /usr/src/module/

WORKDIR /usr/src/nginx

# Get nginx configure arguments from running nginx
RUN nginx -V 2>&1 | sed -n -e 's/^.*arguments: //p' > /tmp/nginx_args

# Configure nginx with the module
RUN eval "./configure $(cat /tmp/nginx_args) --add-dynamic-module=/usr/src/module" \
    && make \
    && make modules

# Production stage
FROM nginx:${NGINX_VERSION}-alpine

# Copy the compiled module
COPY --from=builder /usr/src/nginx/objs/ngx_http_websocket_stat_module.so /etc/nginx/modules/

# Add load_module directive to main nginx.conf
RUN sed -i '1i load_module modules/ngx_http_websocket_stat_module.so;' /etc/nginx/nginx.conf

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
