# frontend/entrypoint.sh

#!/bin/sh
# Exit immediately if a command exits with a non-zero status.
set -e

# Define the path to the main JavaScript file
JS_FILE="/usr/share/nginx/html/main.js"

echo "Replacing API URL placeholders in $JS_FILE..."

# Replace placeholders with values from environment variables
# The environment variables (PRODUCT_API_URL, ORDER_API_URL) will be supplied by the Kubernetes ConfigMap.
sed -i "s|PLACEHOLDER_PRODUCT_API_URL|${PRODUCT_API_URL}|g" $JS_FILE
sed -i "s|PLACEHOLDER_ORDER_API_URL|${ORDER_API_URL}|g" $JS_FILE

echo "Placeholders replaced. Starting Nginx..."

# Execute the original container command (nginx)
exec nginx -g 'daemon off;'