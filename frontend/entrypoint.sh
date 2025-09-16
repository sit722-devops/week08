#!/bin/sh
# entrypoint.sh

ROOT_DIR=/usr/share/nginx/html
echo "Replacing API URL placeholders in main.js..."
sed -i "s|VITE_PRODUCT_API_URL|${PRODUCT_API_URL}|g" ${ROOT_DIR}/main.js
sed -i "s|VITE_ORDER_API_URL|${ORDER_API_URL}|g" ${ROOT_DIR}/main.js

echo "Starting Nginx..."
exec nginx -g 'daemon off;'