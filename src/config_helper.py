"""
config_helper.py

A command-line tool for helping simplify application study tool configurations. It takes 2 input files,
one containing defaults that should be applied to each bigip receiver configuration, and a second with
the individual bigip targets and any non-default values to use as overrides.

The output is written to ./services/otel_collector/receivers.yaml (and pipelines.yaml) where the AST
Otel Instance merges them with the base configuration templates.

Key Features:
- Convert legacy JSON configurations to a new YAML format.
- Generate output configurations based on default settings and per-device inputs.
- Supports dry-run mode to preview changes without writing to files.

Command-Line Interface:
The tool can be executed from the command line with the following options:
- --convert-legacy-config: Convert the legacy configuration file to the new format.
- --generate-configs: Generate new configurations based on the input files.
- --dry-run: Preview changes without writing to files.

These additional flags can also be specified (but probably shouldn't be):
- --legacy-config-file: Specify the path to the legacy configuration file (default: ./config/big-ips.json).
- --default-config-file: Specify the path to the default settings file (default: ./config/ast_defaults.yaml).
- --receiver-input-file: Specify the path to the receiver input file (default: ./config/bigip_receivers.yaml).
- --receiver-output-file: Specify the output path for the receiver configuration file (default: ./services/otel_collector/receivers.yaml).
- --pipelines-output-file: Specify the output path for the pipeline configuration file (default: ./services/otel_collector/pipelines.yaml).

Usage Example:
To convert a legacy configuration in the default ./config/big-ips.json file:
    python ./src/config_helper.py --convert-legacy-config

To generate configurations:
    python ./src/config_helper.py --generate-configs

To re-generate configurations (e.g. after adding new devices or changing default settings), re-run the above command.
"""

import argparse
import json
import logging

import yaml
from copy import deepcopy


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_yaml(path):
    """Load a YAML file from the specified path.

    This function reads a YAML file and parses its content into a Python dictionary.
    It logs the status of the loading operation, including success and various error cases.

    Parameters:
        path (str): The file path to the YAML file to be loaded.

    Returns:
        dict or None: The content of the YAML file as a dictionary if loading is successful;
                      None if an error occurs (e.g., file not found, permission denied,
                      or invalid YAML format).
    """
    try:
        with open(path, "r") as f:
            content = yaml.safe_load(f)
            logging.info("Successfully loaded '%s'.", path)
            return content
    except FileNotFoundError:
        logging.error("Error: The file '%s' does not exist.", path)
        return None
    except PermissionError:
        logging.error("Error: Permission denied when trying to open '%s'.", path)
        return None
    except yaml.YAMLError as e:
        logging.error("Error reading YAML file '%s': %s", path, e)
        return None


def load_json(path):
    """Load a JSON file from the specified path.

    This function reads a JSON file and parses its content into a Python dictionary.
    It logs the status of the loading operation, including success and various error cases.

    Parameters:
        path (str): The file path to the JSON file to be loaded.

    Returns:
        dict or None: The content of the JSON file as a dictionary if loading is successful;
                      None if an error occurs (e.g., file not found, permission denied,
                      or invalid JSON format).
    """
    try:
        with open(path, "r") as f:
            content = json.loads(f.read())
            logging.info("Successfully loaded '%s'.", path)
            return content
    except FileNotFoundError:
        logging.error("Error: The file '%s' does not exist.", path)
        return None
    except PermissionError:
        logging.error("Error: Permission denied when trying to open '%s'.", path)
        return None
    except json.JSONDecodeError as e:
        logging.error("Error reading JSON file '%s': %s", path, e)
        return None


def write_yaml_to_file(data, path):
    """Write a dictionary to a YAML file.

    This function serializes a given dictionary and writes it to a specified YAML file.
    It logs the success or failure of the write operation.

    Parameters:
        data (dict): The dictionary to be written to the YAML file.
        path (str): The file path where the YAML data will be saved.

    Returns:
        None: This function does not return a value. It either successfully writes the data
              to the file or logs an error if the operation fails.
    """
    try:
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)  # Write data to YAML file
            logging.info("Successfully wrote data to '%s'.", path)
    except IOError as e:
        logging.error("Error writing to YAML file '%s': %s", path, e)


def load_default_config(args):
    """Load the default configuration settings from a YAML file.

    This function retrieves the default settings for the application study tool
    by loading a YAML configuration file specified in the command-line arguments.

    Parameters:
        args (argparse.Namespace): The command-line arguments that include the
                                   path to the default configuration file.

    Returns:
        dict or None: The content of the YAML file as a dictionary if loading is successful;
                      None if an error occurs while loading the file.
    """
    logging.info("Loading AST Default Settings in %s...", args.default_config_file)
    return load_yaml(args.default_config_file)


def load_receiver_config(args):
    """Load the per-receiver / bigip Device configuration settings from a YAML file.

    This function retrieves the receiver settings for the application study tool
    by loading a YAML configuration file specified in the command-line arguments.

    Parameters:
        args (argparse.Namespace): The command-line arguments that include the
                                   path to the default configuration file.

    Returns:
        dict or None: The content of the YAML file as a dictionary if loading is successful;
                      None if an error occurs while loading the file.
    """
    logging.info(
        "Loading Per-Receiver (BigIP) Settings in %s...", args.receiver_input_file
    )
    return load_yaml(args.receiver_input_file)


def load_legacy_config(args):
    """Load the legacy config from a JSON file.

    This function retrieves the legacy configuration for the application study tool
    by loading a JSON configuration file specified in the command-line arguments.

    Parameters:
        args (argparse.Namespace): The command-line arguments that include the
                                   path to the legacy configuration file.

    Returns:
        dict or None: The content of the JSON file as a dictionary if loading is successful;
                      None if an error occurs while loading the file.
    """
    logging.info("Loading legacy configuration in %s...", args.legacy_config_file)
    return load_json(args.legacy_config_file)


def convert_legacy_config(args):
    """Convert legacy configuration to the new format.

    This function loads the default configuration and legacy configuration files, then transforms
    the legacy configuration into a new format using the defaults specified in the default configuration.

    Args:
        args (argparse.Namespace): Command-line arguments containing paths to configuration files.

    Returns:
        dict or None: A dictionary representing the transformed receiver configurations, or None if any error occurs during loading or processing.
    """
    logging.info("Converting legacy configuration in %s...", args.legacy_config_file)

    default_config = load_default_config(args)
    if not default_config:
        return None

    default_receiver_configs = default_config.get("bigip_receiver_defaults")
    if not default_receiver_configs:
        logging.error(
            "Error: Default receiver configs not found in default settings file."
        )
        return None

    legacy_config = load_legacy_config(args)
    if not legacy_config:
        return None

    return transform_receiver_configs(legacy_config, default_receiver_configs)


def transform_receiver_configs(legacy_configs, default_configs):
    """Transform legacy receiver configurations into the new format.

    This function takes a list of legacy receiver configurations and transforms each configuration
    into a new format based on the provided default configurations. It generates a dictionary where
    each key is a unique identifier for a receiver (e.g., "bigip/1") and the value is the transformed
    receiver configuration.

    Args:
        legacy_configs (list): A list of legacy receiver configuration dictionaries.
        default_configs (dict): A dictionary containing default configuration values for the receivers.

    Returns:
        dict: A dictionary containing the transformed receiver configurations,
              where keys are formatted as "bigip/{index}" and values are the transformed configurations.
    """
    new_receiver_configs = {}
    for idx, receiver_config in enumerate(legacy_configs):
        new_receiver_configs[f"bigip/{idx + 1}"] = transform_single_receiver(
            receiver_config, default_configs
        )
    return new_receiver_configs


def handle_collection_interval(value, default_value):
    """Handle collection interval formatting."""
    with_seconds = f"{value}s"
    return with_seconds if with_seconds != default_value else None


def handle_password_env_ref(value, default_value):
    """Handle password environment reference formatting."""
    escaped_value = f"${{env:{value}}}"
    return escaped_value if escaped_value != default_value else None


def handle_tls_settings(new_receiver_config, key, value, default_configs):
    """Handle TLS settings for the receiver configuration."""
    if key == "tls_insecure_skip_verify":
        default_value = default_configs.get("tls", {}).get("insecure_skip_verify")
        key = "insecure_skip_verify"
    else:  # key == "ca_file"
        default_value = default_configs.get("tls", {}).get("ca_file")

    if value != default_value:
        if "tls" not in new_receiver_config:
            new_receiver_config["tls"] = {}
        new_receiver_config["tls"][key] = value


def transform_single_receiver(receiver_config, default_configs):
    """Transform a single receiver configuration.

    This function takes a legacy receiver configuration and transforms it into the new format
    based on the provided default configurations. It processes specific keys differently and
    incorporates logic for handling collection intervals, passwords, and TLS settings.

    Args:
        receiver_config (dict): A dictionary representing the legacy receiver configuration.
        default_configs (dict): A dictionary containing default configuration values for comparison.

    Returns:
        dict: A dictionary containing the transformed receiver configuration, including any updates
              based on the provided defaults and specific handling for certain keys.

    The following transformations are applied:
    - **collection_interval**: Formatted with seconds using the `handle_collection_interval` function.
    - **password_env_ref**: Processed using the `handle_password_env_ref` function.
    - **TLS settings**: Handled through the `handle_tls_settings` function.
    - If a key's value matches the default value, it is skipped.
    """
    new_receiver_config = {}
    for key, value in receiver_config.items():
        default_value = default_configs.get(key)

        if key == "collection_interval":
            interval = handle_collection_interval(value, default_value)
            if interval:
                new_receiver_config[key] = interval
        elif key == "password_env_ref":
            pw = handle_password_env_ref(value, default_value)
            if pw:
                new_receiver_config["password"] = pw
        elif key in ["tls_insecure_skip_verify", "ca_file"]:
            handle_tls_settings(new_receiver_config, key, value, default_configs)
        elif default_value and default_value == value:
            continue  # Skip if value is the same as the default
        else:
            new_receiver_config[key] = value

    return new_receiver_config


def deep_merge(dict1, dict2):
    """Deep merge two dictionaries."""
    for key, value in dict2.items():
        if key in dict1:
            # If both values are dicts, merge them
            if isinstance(dict1[key], dict) and isinstance(value, dict):
                deep_merge(dict1[key], value)
            else:
                dict1[key] = value  # Overwrite with dict2's value
        else:
            dict1[key] = value  # Add new key from dict2
    return dict1


def generate_receiver_configs(receiver_input_configs, default_config):
    """Generate merged receiver configurations from input and defaults.

    This function takes a dictionary of receiver input configurations and a default configuration,
    and generates a merged configuration for each receiver. It ensures that any specific receiver
    configurations override the default values while maintaining the overall structure defined by
    the defaults.

    Args:
        receiver_input_configs (dict): A dictionary where keys are receiver identifiers and values
                                       are their corresponding configurations.
        default_config (dict): A dictionary containing default configuration values, particularly
                               under the key 'bigip_receiver_defaults'.

    Returns:
        dict: A dictionary containing the merged receiver configurations, where each key corresponds
              to a receiver identifier and each value is the resulting merged configuration.

    The following operations are performed for each receiver:
    - Deep copies of the default configurations and the receiver-specific configurations are created.
    - If the receiver configuration contains a 'pipeline' key, it is removed.
    - The merged configuration is generated by deep merging the defaults with the specific receiver
      configuration, ensuring that specific values take precedence over defaults.
    """
    merged_config = {}
    for k, v in receiver_input_configs.items():
        defaults = deepcopy(default_config.get("bigip_receiver_defaults"))
        this_cfg = deepcopy(v)
        if this_cfg.get("pipeline"):
            del this_cfg["pipeline"]
        merged_config[k] = deep_merge(defaults, this_cfg)
    return merged_config


def assemble_pipelines(
    pipeline_key, default_pipeline, receiver_input_configs, pipelines, filename
):
    """
    Assembles pipeline configurations by linking receivers to their respective pipelines.

    This function iterates over the provided receiver input configurations and associates each receiver
    with its corresponding pipeline. If a specified pipeline is not found in the defined pipelines,
    an error is logged, and the function returns None.

    Parameters:
    - pipeline_key (str): The key used to retrieve the pipeline name from the receiver's configuration.
    - default_pipeline (str): The default pipeline to use if none is specified in the receiver's config.
    - receiver_input_configs (dict): A dictionary mapping receiver names to their configuration settings.
    - pipelines (dict): A dictionary of available pipelines, where each pipeline is identified by its name.
    - filename (str): The name of the configuration file being processed, used for logging errors.

    Returns:
    - None: If any specified pipeline is not found, the function logs an error and exits early.
    """
    for receiver, config in receiver_input_configs.items():
        pipeline = config.get(pipeline_key, default_pipeline)
        this_pipeline = pipelines.get(pipeline)
        if not this_pipeline:
            logging.error(
                "Pipeline %s on Receiver %s is not found in config pipelines section of %s...",
                pipeline,
                receiver,
                filename,
            )
            return None
        if not this_pipeline.get("receivers"):
            this_pipeline["receivers"] = []
        this_pipeline["receivers"].append(receiver)


def generate_pipeline_configs(receiver_input_configs, default_config, args):
    """Generate pipeline configurations based on receiver inputs and default settings.

    This function constructs pipeline configurations by associating receivers with their respective
    pipelines based on the provided receiver input configurations and default settings. It validates
    the existence of default pipelines and the pipelines specified in the default configuration.

    Args:
        receiver_input_configs (dict): A dictionary where keys are receiver identifiers and values
                                       are their corresponding configurations.
        default_config (dict): A dictionary containing default configuration values, particularly
                               under the keys 'pipeline_default' and 'pipelines'.
        args (argparse.Namespace): The parsed command-line arguments, used for logging context.

    Returns:
        dict or None: A dictionary containing the updated pipeline configurations, or None if
                      there are errors (e.g., missing default pipelines or pipelines for receivers).

    The function performs the following steps:
    - Retrieves the default pipeline from the default configuration.
    - Validates the existence of pipelines in the default configuration.
    - Iterates over each receiver in the input configurations to determine its associated pipeline.
    - If the specified pipeline does not exist, logs an error and returns None.
    - Appends the receiver to the appropriate pipeline's receivers list, creating the list if it does not exist.
    """
    pipelines = default_config.get("pipelines")
    if not pipelines:
        logging.error(
            "No pipelines set in default config file:\n\n%s", yaml.dump(default_config)
        )
        return None

    default_pipeline = default_config.get("pipeline_default")
    if not default_pipeline:
        logging.error(
            "No default pipeline set in default config file:\n\n%s",
            yaml.dump(default_config),
        )
        return None

    assemble_pipelines(
        "pipeline",
        default_pipeline,
        receiver_input_configs,
        pipelines,
        args.receiver_input_file,
    )

    f5_pipeline_default = default_config.get("f5_pipeline_default")
    enabled = default_config.get("f5_data_export", False)
    f5_export_enabled = f5_pipeline_default and enabled
    if not f5_export_enabled:
        logging.warning(
            "The f5_data_export=true and f5_pipeline_default fields are required to "
            "export metrics periodically to F5. Contact your F5 Sales Rep to provision a "
            "Sensor ID and Access Token.",
        )
    else:
        assemble_pipelines(
            "f5_pipeline",
            f5_pipeline_default,
            receiver_input_configs,
            pipelines,
            args.receiver_input_file,
        )

    final_pipelines = {}
    for pipeline, settings in pipelines.items():
        receivers = settings.get("receivers", [])
        if len(receivers) == 0:
            continue
        final_pipelines[pipeline] = settings
    return final_pipelines


def generate_configs(args):
    """Generate configuration files for receivers and pipelines.

    This function orchestrates the generation of configuration files by loading default settings and
    receiver-specific configurations. It logs the process of generating both receiver and pipeline
    configurations based on the provided arguments.

    Args:
        args (argparse.Namespace): The parsed command-line arguments containing file paths for
                                   default configurations and receiver inputs.

    Returns:
        tuple: A tuple containing two dictionaries:
            - receiver_output_configs (dict): The generated receiver configurations.
            - pipeline_output_configs (dict): The generated pipeline configurations.
    """
    logging.info(
        "Generating configs from  %s and %s...",
        args.default_config_file,
        args.receiver_input_file,
    )
    default_config = load_default_config(args)
    receiver_input_configs = load_receiver_config(args)
    logging.info("Generating receiver configs...")
    receiver_output_configs = generate_receiver_configs(
        receiver_input_configs, default_config
    )
    logging.info("Generating pipeline configs...")
    pipeline_output_configs = generate_pipeline_configs(
        receiver_input_configs, default_config, args
    )
    return receiver_output_configs, pipeline_output_configs


def get_args():
    """Initialize the argument parser.

    Returns:
        parser: argumentparser object with config_helper arguments specified.
    """
    parser = argparse.ArgumentParser(
        description="A tool for helping with application study tool configurations."
    )

    parser.add_argument(
        "--convert-legacy-config",
        action="store_true",
        help="Convert the legacy big-ips.json to the new format.",
    )

    parser.add_argument(
        "--legacy-config-file",
        type=str,
        default="./config/big-ips.json",
        help="Path to the legacy big-ips.json file to convert (default: ./config/big-ips.json).",
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Don't write output to files"
    )

    parser.add_argument(
        "--default-config-file",
        type=str,
        default="./config/ast_defaults.yaml",
        help="Path to the default settings file to generate configs from (default: ./config/ast_defaults.yaml).",
    )

    parser.add_argument(
        "--receiver-input-file",
        type=str,
        default="./config/bigip_receivers.yaml",
        help="Path to the receiver settings input file (bigIP Configs) to generate configs from (default: ./config/bigip_receivers.yaml).",
    )

    parser.add_argument(
        "--generate-configs",
        action="store_true",
        help="Read files in config directory and write AST Otel Config",
    )

    parser.add_argument(
        "--receiver-output-file",
        type=str,
        default="./services/otel_collector/receivers.yaml",
        help="Path to the receiver settings otel file (default: ./services/otel_collector/receivers.yaml).",
    )

    parser.add_argument(
        "--pipelines-output-file",
        type=str,
        default="./services/otel_collector/pipelines.yaml",
        help="Path to the pipeline settings otel config file (default: ./services/otel_collector/pipelines.yaml).",
    )
    return parser


def main():
    """Main entry point for the configuration management tool.

    This function orchestrates the command-line interface for the application, handling user input
    and executing the appropriate actions based on the specified command-line arguments. It supports
    converting legacy configurations and generating new configuration files.

    Steps performed by this function:
    - Parses command-line arguments using `get_args`.
    - If the `--convert-legacy-config` flag is provided:
        - Calls `convert_legacy_config` to convert the legacy configuration file.
        - Logs the converted output and writes it to a specified YAML file unless in dry-run mode.
    - If the `--generate-configs` flag is specified:
        - Calls `generate_configs` to create new receiver and pipeline configurations.
        - Logs the generated configurations and writes them to their respective output files unless in dry-run mode.
    - If neither action is specified, logs an informational message prompting the user to choose an action.
    """
    parser = get_args()

    args = parser.parse_args()

    if args.convert_legacy_config:
        new_receivers = convert_legacy_config(args)
        if not new_receivers:
            return
        logging.info(
            "Converted the legacy config to the following "
            "bigip_receivers.yaml output:\n\n%s",
            yaml.dump(new_receivers, default_flow_style=False),
        )
        if not args.dry_run:
            write_yaml_to_file(new_receivers, args.receiver_input_file)
        return

    if args.generate_configs:
        receiver_config, pipeline_config = generate_configs(args)
        if not receiver_config or not pipeline_config:
            return
        logging.info(
            "Built the following pipeline file:\n\n%s",
            yaml.dump(pipeline_config, default_flow_style=False),
        )
        logging.info(
            "Built the following receiver file:\n\n%s",
            yaml.dump(receiver_config, default_flow_style=False),
        )
        if not args.dry_run:
            write_yaml_to_file(pipeline_config, args.pipelines_output_file)
            write_yaml_to_file(receiver_config, args.receiver_output_file)
        return

    logging.info(
        "Found nothing to do... Try running with --convert-legacy-config or --generate-configs..."
    )


if __name__ == "__main__":
    main()
