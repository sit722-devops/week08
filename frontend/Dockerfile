# frontend/Dockerfile

FROM nginx:alpine

# Copy the Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the static web content
COPY . /usr/share/nginx/html

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

EXPOSE 80

# Set the entrypoint to our script
ENTRYPOINT ["/entrypoint.sh"]

# The original CMD is now executed by the entrypoint script
# CMD ["nginx", "-g", "daemon off;"]