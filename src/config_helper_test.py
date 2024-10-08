import unittest
from unittest.mock import patch, MagicMock
import logging
import yaml

# Assuming the convert_legacy_config function is in a module named my_module
from config_helper import (
    convert_legacy_config,
    deep_merge,
    generate_receiver_configs,
    generate_pipeline_configs,
    generate_configs,
)


class TestConvertLegacyConfig(unittest.TestCase):

    @patch("config_helper.load_default_config")
    @patch("config_helper.load_legacy_config")
    def test_convert_legacy_config_success(self, mock_load_legacy, mock_load_defaults):
        # Setup mock return values
        mock_load_defaults.return_value = {
            "bigip_receiver_defaults": {
                "collection_interval": "10s",
                "password": "${env:default_password}",
                "tls": {"insecure_skip_verify": False, "ca_file": "/path/to/ca.crt"},
            }
        }
        mock_load_legacy.return_value = [
            {
                "collection_interval": 10,
                "password_env_ref": "secret_password",
                "tls_insecure_skip_verify": True,
            },
            {"collection_interval": 15, "ca_file": "/path/to/new_ca.crt"},
        ]

        # Mock args
        class Args:
            legacy_config_file = "path/to/legacy_config.json"
            default_config_file = "path/to/default_config.yaml"

        args = Args()

        result = convert_legacy_config(args)

        expected_output = {
            "bigip/1": {
                "password": "${env:secret_password}",
                "tls": {"insecure_skip_verify": True},
            },
            "bigip/2": {
                "collection_interval": "15s",
                "tls": {"ca_file": "/path/to/new_ca.crt"},
            },
        }

        self.assertEqual(result, expected_output)

    @patch("config_helper.load_default_config")
    @patch("config_helper.load_legacy_config")
    def test_convert_legacy_config_no_default(
        self, mock_load_legacy, mock_load_defaults
    ):
        mock_load_defaults.return_value = None
        mock_load_legacy.return_value = []

        class Args:
            legacy_config_file = "path/to/legacy_config.json"
            default_config_file = "path/to/default_config.yaml"

        args = Args()

        result = convert_legacy_config(args)

        self.assertIsNone(result)

    @patch("config_helper.load_default_config")
    @patch("config_helper.load_legacy_config")
    def test_convert_legacy_config_no_receiver_defaults(
        self, mock_load_legacy, mock_load_defaults
    ):
        mock_load_defaults.return_value = {}
        mock_load_legacy.return_value = []

        class Args:
            legacy_config_file = "path/to/legacy_config.json"
            default_config_file = "path/to/default_config.yaml"

        args = Args()

        result = convert_legacy_config(args)

        self.assertIsNone(result)

    @patch("config_helper.load_default_config")
    @patch("config_helper.load_legacy_config")
    def test_convert_legacy_config_no_legacy_config(
        self, mock_load_legacy, mock_load_defaults
    ):
        mock_load_defaults.return_value = {
            "bigip_receiver_defaults": {
                "collection_interval": "10s",
                "password": "${env:default_password}",
            }
        }
        mock_load_legacy.return_value = None

        class Args:
            legacy_config_file = "path/to/legacy_config.json"
            default_config_file = "path/to/default_config.yaml"

        args = Args()

        result = convert_legacy_config(args)

        self.assertIsNone(result)


class TestConfigFunctions(unittest.TestCase):

    def test_deep_merge(self):
        dict1 = {"key1": {"subkey1": "value1", "subkey2": "value2"}, "key2": "value3"}
        dict2 = {
            "key1": {"subkey2": "new_value2", "subkey3": "value4"},
            "key3": "value5",
        }

        expected_merged = {
            "key1": {"subkey1": "value1", "subkey2": "new_value2", "subkey3": "value4"},
            "key2": "value3",
            "key3": "value5",
        }

        result = deep_merge(dict1, dict2)
        self.assertEqual(result, expected_merged)

    def test_generate_receiver_configs(self):
        receiver_input_configs = {
            "receiver1": {"setting1": "value1", "pipeline": "some_pipeline"},
            "receiver2": {"setting2": "value2"},
        }

        default_config = {
            "bigip_receiver_defaults": {
                "setting1": "default_value1",
                "setting2": "default_value2",
            }
        }

        expected_output = {
            "receiver1": {"setting1": "value1", "setting2": "default_value2"},
            "receiver2": {"setting2": "value2", "setting1": "default_value1"},
        }

        result = generate_receiver_configs(receiver_input_configs, default_config)
        self.assertEqual(result, expected_output)

    @patch("config_helper.logging.error")
    def test_generate_pipeline_configs_no_pipeline(self, mock_error):
        receiver_input_configs = {"receiver1": {"pipeline": "pipeline1"}}
        default_config = {}
        args = MagicMock()
        args.receiver_input_file = "dummy_file.yaml"

        result = generate_pipeline_configs(receiver_input_configs, default_config, args)
        self.assertIsNone(result)
        mock_error.assert_called_once()

    @patch("config_helper.load_default_config")
    @patch("config_helper.load_receiver_config")
    @patch("config_helper.logging.info")
    def test_generate_configs(self, mock_info, mock_load_receiver, mock_load_default):
        mock_load_default.return_value = {
            "bigip_receiver_defaults": {},
            "pipeline_default": "default_pipeline",
            "pipelines": {"default_pipeline": {"receivers": []}},
        }

        mock_load_receiver.return_value = {
            "receiver1": {"pipeline": "default_pipeline"}
        }

        args = MagicMock()
        args.default_config_file = "default.yaml"
        args.receiver_input_file = "input.yaml"

        receiver_output, pipeline_output = generate_configs(args)

        self.assertIsNotNone(receiver_output)
        self.assertIsNotNone(pipeline_output)
        self.assertIn("receiver1", pipeline_output["default_pipeline"]["receivers"])
        mock_info.assert_any_call(
            "Generating configs from  %s and %s...",
            args.default_config_file,
            args.receiver_input_file,
        )

    @patch("config_helper.load_default_config")
    @patch("config_helper.load_receiver_config")
    @patch("config_helper.logging.info")
    def test_generate_configs_f5_export(
        self, mock_info, mock_load_receiver, mock_load_default
    ):
        mock_load_default.return_value = {
            "bigip_receiver_defaults": {},
            "f5_data_export": True,
            "pipeline_default": "default_pipeline",
            "f5_pipeline_default": "default_pipeline2",
            "pipelines": {
                "default_pipeline": {"receivers": []},
                "default_pipeline2": {"receivers": []},
            },
        }

        mock_load_receiver.return_value = {
            "receiver1": {
                "pipeline": "default_pipeline",
                "f5_pipeline": "default_pipeline2",
            },
            "receiver2": {"pipeline": "default_pipeline"},
        }

        args = MagicMock()
        args.default_config_file = "default.yaml"
        args.receiver_input_file = "input.yaml"

        receiver_output, pipeline_output = generate_configs(args)

        self.assertIsNotNone(receiver_output)
        self.assertIsNotNone(pipeline_output)
        self.assertIn("receiver1", pipeline_output["default_pipeline"]["receivers"])
        self.assertIn("receiver1", pipeline_output["default_pipeline2"]["receivers"])
        self.assertIn("receiver2", pipeline_output["default_pipeline2"]["receivers"])
        mock_info.assert_any_call(
            "Generating configs from  %s and %s...",
            args.default_config_file,
            args.receiver_input_file,
        )

    @patch("config_helper.load_default_config")
    @patch("config_helper.load_receiver_config")
    @patch("config_helper.logging.info")
    def test_generate_configs_f5_export_not_true(
        self, mock_info, mock_load_receiver, mock_load_default
    ):
        mock_load_default.return_value = {
            "bigip_receiver_defaults": {},
            "pipeline_default": "default_pipeline",
            "f5_pipeline_default": "default_pipeline2",
            "pipelines": {
                "default_pipeline": {"receivers": []},
                "default_pipeline2": {"receivers": []},
            },
        }

        mock_load_receiver.return_value = {
            "receiver1": {
                "pipeline": "default_pipeline",
                "f5_pipeline": "default_pipeline2",
            },
            "receiver2": {"pipeline": "default_pipeline"},
        }

        args = MagicMock()
        args.default_config_file = "default.yaml"
        args.receiver_input_file = "input.yaml"

        receiver_output, pipeline_output = generate_configs(args)

        self.assertIsNotNone(receiver_output)
        self.assertIsNotNone(pipeline_output)
        self.assertIn("receiver1", pipeline_output["default_pipeline"]["receivers"])
        self.assertNotIn("default_pipeline2", pipeline_output)
        mock_info.assert_any_call(
            "Generating configs from  %s and %s...",
            args.default_config_file,
            args.receiver_input_file,
        )


if __name__ == "__main__":
    unittest.main()
