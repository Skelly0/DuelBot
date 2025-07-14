import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')
DEFAULT_SETTINGS = {
    'chaurus_talent': False,
    'triple_stance_word': '',
    'moderators': []
}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = DEFAULT_SETTINGS.copy()
    else:
        data = DEFAULT_SETTINGS.copy()
    for key, value in DEFAULT_SETTINGS.items():
        data.setdefault(key, value)

    # Ensure moderators is a list of integers
    if isinstance(data.get('moderators'), list):
        data['moderators'] = [int(m) for m in data['moderators']]
    else:
        data['moderators'] = []

    return data

def save_settings(settings: dict) -> None:
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except OSError:
        pass
