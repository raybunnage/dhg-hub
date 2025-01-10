import logging
import logging.config
import os
import yaml


def verify_logging_setup():
    try:
        # Create config directory if it doesn't exist
        config_dir = "config"
        logs_dir = "logs"
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)

        # Check if logging config file exists
        config_path = "config/logging.yaml"  # adjust path as needed
        if not os.path.exists(config_path):
            print("❌ Logging configuration file not found")
            return False

        # Try to load and apply logging configuration
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)

        # Test logging to different handlers
        logger = logging.getLogger(__name__)
        logger.info("Test info message")
        logger.error("Test error message")

        # Verify log files were created
        log_files = config.get("handlers", {})
        for handler in log_files.values():
            if "filename" in handler:
                if os.path.exists(handler["filename"]):
                    print(f"✅ Log file created: {handler['filename']}")
                else:
                    print(f"❌ Log file missing: {handler['filename']}")

        return True

    except Exception as e:
        print(f"❌ Logging setup verification failed: {str(e)}")
        return False


if __name__ == "__main__":
    verify_logging_setup()
