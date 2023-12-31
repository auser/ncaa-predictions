from pathlib import Path
import os

PARENT_DIR = Path(__file__).parent.resolve().parent
DATA_DIR = PARENT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
TRANSFORMED_DATA_DIR = DATA_DIR / "transformed"
MODELS_DIR = PARENT_DIR / "models"

SEASONS_DIR = RAW_DATA_DIR / "seasons"

if not Path(DATA_DIR).exists():
    os.mkdir(DATA_DIR)

if not Path(RAW_DATA_DIR).exists():
    os.mkdir(RAW_DATA_DIR)

if not Path(TRANSFORMED_DATA_DIR).exists():
    os.mkdir(TRANSFORMED_DATA_DIR)

if not Path(MODELS_DIR).exists():
    os.mkdir(MODELS_DIR)

if not Path(SEASONS_DIR).exists():
    os.mkdir(SEASONS_DIR)


def team_save_dir(team_name: str, year: int = 2023) -> Path:
    """
    Get the team save directory
    """
    save_dir = Path(SEASONS_DIR / str(year) / team_name)
    if not save_dir.exists():
        save_dir.mkdir(exist_ok=True, parents=True)
    return save_dir
