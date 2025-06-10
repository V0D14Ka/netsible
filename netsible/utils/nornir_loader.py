from nornir import InitNornir
from pathlib import Path

def load_nornir(config_path: Path):
    """
    Инициализирует Nornir с конфигурацией из config.yaml
    """
    return InitNornir(config_file=str(config_path.resolve()))
