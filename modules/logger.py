
import logging
from flask import request

def setup_logger(app):
    """
    Sets up a file and stream logger for the application.
    Logs each request to `app.log` and the console.
    """
    # Create logger
    logger = logging.getLogger('api_logger')
    logger.setLevel(logging.INFO)

    # File Handler
    file_handler = logging.FileHandler('app.log')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Stream Handler (Console)
    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter('%(levelname)s: %(message)s')
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    @app.before_request
    def log_request():
        # You can log headers, body, etc.
        logger.info(f"REQUEST: {request.method} {request.path} - Remote: {request.remote_addr}")

    @app.after_request
    def log_response(response):
        logger.info(f"RESPONSE: {response.status} - Size: {response.content_length}")
        return response
