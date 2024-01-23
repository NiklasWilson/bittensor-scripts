import logging

# Configure logging
logging.basicConfig(
    # filename="command_log.txt",
    level=logging.INFO,
    format="%(asctime)s:%(filename)s:%(lineno)d - %(levelname)s - %(message)s",
)
