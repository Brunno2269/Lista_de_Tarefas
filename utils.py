import os
import signal
import logging

def shutdown_server():
    """Encerra o servidor Flask."""
    os.kill(os.getpid(), signal.SIGINT)

def validate_task_data(data):
    """Valida os dados de uma tarefa."""
    if not data or 'title' not in data:
        return False
    if len(data['title'].strip()) < 1 or len(data['title'].strip()) > 200:
        return False
    return True

def setup_logging(app):
    """Configura o sistema de logs."""
    logging.basicConfig(level=logging.INFO)
    handler = logging.FileHandler('app.log')
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)