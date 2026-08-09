#!/bin/sh
set -eu

PORT=${PORT:-8088}
MODE=${1:-setup}
NGINX_CONF=/etc/nginx/nginx.conf
NGINX_BACKUP=/etc/nginx/nginx.conf.linux-daily-interop.bak
DOCROOT=/var/www/linux-daily-interop

require_lab_host() {
    if [ "${LAB_HOST:-}" != "YES" ]; then
        echo "Refusing to modify this host. Run only on a dedicated lab VM with LAB_HOST=YES." >&2
        exit 2
    fi
    if [ "$(id -u)" -ne 0 ]; then
        echo "Run as root on the dedicated lab VM." >&2
        exit 2
    fi
}

install_packages() {
    . /etc/os-release
    case "${ID:-}" in
        ubuntu|debian)
            apt-get update
            DEBIAN_FRONTEND=noninteractive apt-get install -y nginx curl
            ;;
        fedora)
            dnf install -y nginx curl
            ;;
        *)
            echo "Unsupported Linux distro for this lab: ${ID:-unknown}" >&2
            exit 3
            ;;
    esac
}

write_config() {
    mkdir -p "$DOCROOT"
    printf '%s\n' 'linux-peer: linux-daily interoperability ok' > "$DOCROOT/index.html"
    if [ -f "$NGINX_CONF" ] && [ ! -f "$NGINX_BACKUP" ]; then
        cp -p "$NGINX_CONF" "$NGINX_BACKUP"
    fi
    cat > "$NGINX_CONF" <<EOF
worker_processes  1;
events { worker_connections  64; }
http {
    access_log /var/log/nginx/linux-daily-interop-access.log;
    error_log  /var/log/nginx/linux-daily-interop-error.log notice;
    server {
        listen ${PORT};
        server_name _;
        root ${DOCROOT};
        location / { try_files \$uri /index.html; }
    }
}
EOF
    nginx -t
    systemctl enable --now nginx
    systemctl reload nginx
}

verify_local() {
    curl --fail --silent --show-error "http://127.0.0.1:${PORT}/"
    systemctl is-active nginx
}

verify_peer() {
    : "${PEER_IP:?Set PEER_IP to the FreeBSD lab peer address}"
    curl --fail --silent --show-error "http://${PEER_IP}:${PORT}/"
}

inject_stop() {
    systemctl stop nginx
    if curl --fail --silent --max-time 2 "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
        echo "Negative test failed: HTTP still responds after nginx stop." >&2
        exit 4
    fi
    echo "Negative evidence: nginx is stopped and HTTP probe fails as expected."
}

recover() {
    systemctl start nginx
    verify_local
    echo "Recovery evidence: nginx is active and HTTP responds again."
}

cleanup() {
    if [ -f "$NGINX_BACKUP" ]; then
        cp -p "$NGINX_BACKUP" "$NGINX_CONF"
        rm -f "$NGINX_BACKUP"
        nginx -t
        systemctl reload nginx
    else
        systemctl stop nginx || true
    fi
    rm -rf "$DOCROOT"
    rm -f /var/log/nginx/linux-daily-interop-access.log /var/log/nginx/linux-daily-interop-error.log
    echo "Cleanup complete; packages are intentionally left installed."
}

require_lab_host
case "$MODE" in
    setup) install_packages; write_config; verify_local ;;
    verify-local) verify_local ;;
    verify-peer) verify_peer ;;
    inject-stop) inject_stop ;;
    recover) recover ;;
    cleanup) cleanup ;;
    *)
        echo "Usage: $0 {setup|verify-local|verify-peer|inject-stop|recover|cleanup}" >&2
        exit 2
        ;;
esac
