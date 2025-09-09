#
#  Copyright 2024 F5 Networks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

.PHONY: test-certs
test-certs:
	@echo "Generating self-signed certificates..."
	@mkdir -p ./services/otel_collector/ssl
	@openssl genpkey -algorithm RSA -out ./services/otel_collector/ssl/key.pem
	@openssl req -new -key ./services/otel_collector/ssl/key.pem -out ./services/otel_collector/ssl/cert.csr -subj "/CN=localhost"
	@openssl x509 -req -in ./services/otel_collector/ssl/cert.csr -signkey ./services/otel_collector/ssl/key.pem -out ./services/otel_collector/ssl/cert.pem
	@openssl genpkey -algorithm RSA -out ./services/otel_collector/ssl/ca.key
	@openssl req -x509 -new -key ./services/otel_collector/ssl/ca.key -out ./services/otel_collector/ssl/ca.pem -days 365 -subj "/CN=Test CA"
	@rm -f ./services/otel_collector/ssl/ca.key ./services/otel_collector/ssl/cert.csr
	@echo "Certificates generated at ./services/otel_collector/ssl/"