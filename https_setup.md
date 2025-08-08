### Enabling HTTPS for Grafana

This section outlines the steps required to enable HTTPS for Grafana when deployed using Docker Compose.

#### 1. Generate SSL Certificate and Key

To enable HTTPS, you need a certificate `(cert.pem)` and a private key `(key.pem)`. For local development, you can generate self-signed certificates using OpenSSL with the following commands:

```sh
mkdir -p ./services/grafana/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ./services/grafana/ssl/key.pem -out ./services/grafana/ssl/cert.pem \
  -subj "/CN=localhost"
```

> **Note:** In production environments, always use certificates from a trusted Certificate Authority (CA).
> It is recommended to rotate these certificates regularly before they expire to minimize the risk of security breaches.

> **Reference:** For more detailed guidance on configuring HTTPS, refer to the [official Grafana documentation](https://grafana.com/docs/grafana/latest/setup-grafana/set-up-https/).

#### 2. Modify the Docker Compose Configuration

Update your `docker-compose.yaml` file with the necessary configurations to enable HTTPS for Grafana. Below is an example snippet for the Grafana service:

```yaml
grafana:
  image: grafana/grafana:11.6.3
  container_name: grafana
  restart: unless-stopped
  ports:
    - 3000:3000
    - 3001:3001 # HTTPS port
  volumes:
    - grafana:/var/lib/grafana
    - ./services/grafana/provisioning/:/etc/grafana/provisioning
    - ./services/grafana/ssl/cert.pem:/etc/grafana/cert.pem:ro
    - ./services/grafana/ssl/key.pem:/etc/grafana/key.pem:ro
  env_file: ".env"
  environment:
    - GF_SERVER_PROTOCOL=https
    - GF_SERVER_CERT_FILE=/etc/grafana/cert.pem
    - GF_SERVER_CERT_KEY=/etc/grafana/key.pem
    - GF_SERVER_HTTP_PORT=3001
```

By following these steps, you will successfully enable HTTPS for your Grafana deployment. Ensure you test your configuration in both development and production environments to verify functionality and security compliance.