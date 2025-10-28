[![Travis Build Status](https://travis-ci.org/refinitiv/ngx_http_websocket_stat_module.svg?branch=master)](https://travis-ci.org/refinitiv/ngx_http_websocket_stat_module.svg?branch=master)


# NGINX module websocket connection and traffic statistics

Nginx module developed for logging and displaying statistic of websocket proxy connections traffic, limiting number of websocket connections and closing long lasting websocket connections.

## Installation

   1. Configure nginx adding this module with:
   ```sh
          ./configure (...) --add-module=./ngx_http_websocket_stat_module
   ```
   2. Build nginx with make -j<n> command where n is number of cpu cores on your build machine

   Alternatively could be used build script shipped along with module:
   From module directory run
   ```sh
   test/build_helper.py build
   ```
   It would download and build nginx and all required libraries (openssl, pcre and zlib) and generate nginx configuration file.

## Usage

To enable websocket logging specify log file in server section of nginx config file with ws_log directibe.

You can specify your own websocket log format using ws_log_format directive in server section. To customize connection open and close log messages use "open" and "close" parameter for ws_log_format directive.

Maximum number of concurrent websocket connections could be specified with ws_max_connections on server section. This value applies to whole connections that are on nginx. Argument should be integer representing maximum connections. When client tries to open more connections it recevies close framee with 1013 error code and connection is closed on nginx side. If zero number of connections is given there would be no limit on websocket connections.

To set maximum single connection lifetime use ws_conn_age parameter. Argument is time given in nginx time format (e.g. 1s, 1m 1h and so on). When connection's lifetime is exceeding specified value there is close websocket packet with 4001 error code generated and connection is closed.


Here is a list of variables you can use in log format string:

 * $ws_opcode - websocket packet opcode. Look into https://tools.ietf.org/html/rfc6455 Section 5.2, Base Framing Protocol.
 * $ws_payload_size - Websocket packet size without protocol specific data. Only data that been sent or received by the client
 * $ws_packet_source - Could be "client" if packet has been sent by the user or "upstream" if it has been received from the server
 * $ws_conn_age - Number of seconds connection is alive
 * $time_local - Nginx local time, date and timezone
 * $request - Http reqeust string. Usual looks like "GET /uri HTTP/1.1"
 * $uri - Http request uri.
 * $request_id - unique random generated request id.
 * $remote_user - username if basic authentification is used
 * $remote_addr - Client's remote ip address
 * $remote_port - Client's remote port
 * $server_addr - Server's remote ip address
 * $server_port - Server's port
 * $upstream_addr - websocket backend address

To read websocket statistic there is GET request should be set up at "location" location of nginx config file with ws_stat command in it. The module now outputs metrics in Prometheus format by default.

For scenarios where you want to append WebSocket metrics to existing content (e.g., combining with other metrics endpoints), use the `ws_stat_append` directive instead. This will add the WebSocket metrics to the end of any existing response content.

Look into example section for details.

## Prometheus Metrics

The module exposes the following Prometheus metrics when you access the statistics endpoint:

### Available Metrics

* **nginx_websocket_connections_active** (gauge): Current number of active WebSocket connections
* **nginx_websocket_frames_total** (counter): Total number of WebSocket frames processed
  - Labels: `direction="in"` (from client) or `direction="out"` (to client)
* **nginx_websocket_payload_bytes_total** (counter): Total WebSocket payload bytes transferred
  - Labels: `direction="in"` (from client) or `direction="out"` (to client)
* **nginx_websocket_tcp_bytes_total** (counter): Total TCP bytes for WebSocket connections
  - Labels: `direction="in"` (from client) or `direction="out"` (to client)

### Example Prometheus Output

```
# HELP nginx_websocket_connections_active Current number of active WebSocket connections
# TYPE nginx_websocket_connections_active gauge
nginx_websocket_connections_active 42

# HELP nginx_websocket_frames_total Total number of WebSocket frames
# TYPE nginx_websocket_frames_total counter
nginx_websocket_frames_total{direction="in"} 12345
nginx_websocket_frames_total{direction="out"} 12301

# HELP nginx_websocket_payload_bytes_total Total WebSocket payload bytes
# TYPE nginx_websocket_payload_bytes_total counter
nginx_websocket_payload_bytes_total{direction="in"} 1048576
nginx_websocket_payload_bytes_total{direction="out"} 2097152

# HELP nginx_websocket_tcp_bytes_total Total TCP bytes for WebSocket connections
# TYPE nginx_websocket_tcp_bytes_total counter
nginx_websocket_tcp_bytes_total{direction="in"} 1148576
nginx_websocket_tcp_bytes_total{direction="out"} 2197152
```

### Prometheus Configuration

To scrape these metrics with Prometheus, add the following to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'nginx-websocket'
    static_configs:
      - targets: ['your-nginx-server:port']
    metrics_path: '/websocket_status'  # or your configured path
    scrape_interval: 15s
```

## Example of configuration

### Standalone WebSocket Metrics Endpoint

```nginx
server {
   ws_log /var/log/nginx/websocket.log;
   ws_log_format "$time_local: packet of type $ws_opcode received from $ws_packet_source, packet size is $ws_payload_size";
   ws_log_format open "$time_local: Connection opened";
   ws_log_format close "$time_local: Connection closed";
   ws_max_connections 200;
   ws_conn_age 12h;

   # Dedicated location for WebSocket Prometheus metrics
   location /websocket_status {
      ws_stat;
      # This will return only WebSocket Prometheus-formatted metrics
      # Content-Type: text/plain; version=0.0.4; charset=utf-8
   }

   # Your WebSocket proxy location
   location /websocket {
      proxy_pass http://backend;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_set_header Host $host;
   }
}
```

## Copyright

This document is licensed under BSD-2-Clause license. See LICENSE for details.

The code has been opened by (c) Thomson Reuters.
It is now maintained by (c) Refinitiv.
