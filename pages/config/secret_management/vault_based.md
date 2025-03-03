---
layout: page
title: Via Vault Provider
parent: Secrets Management
grandparent: Configuration Management
nav_order: 2
---

## Configure Device Secrets Via Vault Provider

Integration with a vault provider to inject secrets into the container environment can
be used to avoid storing secrets on disk.

Implementation specifics will vary, but at a high level:

* Device credentials are stored in the vault.
* A vault agent (or script, or similar) running on the AST host reads the keys from the vault and injects them into the
environment directly, or into file on a ramdisk.
* The configuration files for AST point devices at the appropriate environment variables
through the same mechanism as the static file based approach (e.g. ${env:BIGIP_PASSWORD_1}).

For more, see e.g.:

* [Hashicorp Vault Agent - secrets as environment variables](https://developer.hashicorp.com/vault/tutorials/vault-agent/agent-env-vars)
* [GCP Secret Manager](https://cloud.google.com/secret-manager/docs/create-secret-quickstart#secretmanager-quickstart-gcloud)
* [Azure Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-cli)
* [AWS Secret Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_cli.html)

An extremely simplified example might look like:
```shell
$ sudo mkdir /mnt/secrets
$ sudo mount -o size=10M -t tmpfs none /mnt/secrets
$ echo -n "password1_value" | gcloud secrets create BIGIP_PASSWORD_1     --replication-policy="automatic"     --data-file=-
$ echo -n "password2_value" | gcloud secrets create BIGIP_PASSWORD_2     --replication-policy="automatic"     --data-file=-

$ ./secretfetcher.sh 
Secrets have been written to /mnt/secrets/.env.device-secrets

$ cat /mnt/secrets/.env.device-secrets
BIGIP_PASSWORD_1=password1_value
BIGIP_PASSWORD_2=password2_value
```

And the shell script might look like:
```bash
#!/usr/bin/env bash

# List of secret names
secret_names=("BIGIP_PASSWORD_1" "BIGIP_PASSWORD_2")

# Output file
output_file="/mnt/secrets/.env.device-secrets"

# Clear the output file if it already exists
> "$output_file"

for secret in "${secret_names[@]}"; do
    # Access the secret value
    secret_value=$(gcloud secrets versions access 1 --secret="$secret" 2>/dev/null)

    # Check if the secret value was retrieved successfully
    if [[ $? -eq 0 ]]; then
        # Output in .env style format
        echo "$secret=$secret_value" >> "$output_file"
    else
        echo "Failed to access secret: $secret"
    fi
done
echo "Secrets have been written to $output_file"
```

You'd also need to point to the tmpfs secret file in the `docker-compose.yaml` file:
```yaml
  otel-collector:
    #...
    env_file:
      - ".env"
      - "/mnt/secrets/.env.device-secrets"
```