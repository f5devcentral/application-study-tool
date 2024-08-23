#! /usr/bin/env python
"""
Generate a 7LC Collector Configuration for use with default stack.

This file should typically be run from inside the docker-compose init container for otel-collector,
but you can run it manually by setting env:

OTEL_CONFIG_OUT_FILE=/tmp/config.yaml
OTEL_CONFIG_IN_FILE=./config/big-ips.json
OTEL_CONFIG_TEMPLATE_DIR=./slc/data/templates

python3 ./slc/bin/generate_otel_config.py

You'll also need to point to the docker-compose config volume for the generated file at
the config location in the otel-collector stanza and disable the init container.
"""
import os
import sys
import json

import validators

from jinja2 import Environment, FileSystemLoader

OUT_FILE = os.environ.get(
    "OTEL_CONFIG_OUT_FILE", "/app/otel-collector-config/config.yaml"
)
IN_FILE = os.environ.get("OTEL_CONFIG_IN_FILE", "/app/config.json")
TEMPLATE_DIR = os.environ.get("OTEL_CONFIG_TEMPLATE_DIR", "/app/templates")


def validate_config_json(config_file):
    """
    Validate BIG-IP JSON data
    """

    with open(config_file, "r") as infile:
        try:
            big_ip_data = json.load(infile)
        except json.decoder.JSONDecodeError as e:
            print(f"Invalid JSON in {config_file}: {e}")
            sys.exit(1)
        try:
            assert len(big_ip_data) > 0
            for big_ip in big_ip_data:
                big_ip["tls_insecure_skip_verify"] = big_ip.get("tls_insecure_skip_verify", False)
                big_ip["ca_file"] = big_ip.get("ca_file", "")
                if not big_ip["tls_insecure_skip_verify"] and big_ip["ca_file"] == "":
                    raise ValueError('A CA File is required if tls_insecure_skip_verify is not true.')
                endpoint = big_ip.get("endpoint")
                assert validators.url(endpoint) is True
                assert len(big_ip.get("username")) > 0
                assert len(big_ip.get("password_env_ref")) > 0
        except Exception as ex:
            print("BIG-IP JSON config is invalid")
            print(ex)
            sys.exit(1)

        print("Your BIG-IP JSON config is valid")


def gen_collector_config(template_config, out_file, templates):
    """
    Generate the collector's configuration YAML file
    """
    environment = Environment(loader=FileSystemLoader(templates))
    template = environment.get_template("otel_config.jinja")
    content = template.render(template_config)

    with open(out_file, mode="w", encoding="utf-8") as outfile:
        outfile.write(content)
        print(f"... wrote {out_file}")


def gen_json_config(input_file, template_dir):
    """
    Generate the JSON config needed to generate the OTEL config from ENV VARS:
    """
    environment = Environment(loader=FileSystemLoader(template_dir))
    template = environment.get_template("otel_config.json.jinja")

    with open(input_file, "r") as infile:
        devices = json.load(infile)
    try:
        env_vars = {"devices": devices}
        try:
            return json.loads(template.render(env_vars))
        except Exception as e:
            print(f"Error rendering configuration template: {e}")
            sys.exit(1)

    except KeyError as ex:
        print("Your ENV VARS for SLC_BIG_IP** are not set")
        print(ex)
        sys.exit(1)


if __name__ == "__main__":
    validate_config_json(IN_FILE)
    # Create JSON config from env vars and write to disk
    generator_config = gen_json_config(IN_FILE, TEMPLATE_DIR)
    gen_collector_config(generator_config, OUT_FILE, TEMPLATE_DIR)
