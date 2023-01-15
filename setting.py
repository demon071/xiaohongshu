import os
import config
import json



def get_user_settings():
    settings = {}
    try:
        # log('Load user setting from', config.sett_folder)
        file = os.path.join(config.sett_folder, 'setting.cfg')
        with open(file, 'r') as f:
            settings = json.load(f)

    except FileNotFoundError:
        print('setting.cfg not found')
    except Exception as e:
        print('load_setting()> ', e)
    finally:
        if not isinstance(settings, dict):
            settings = {}

        return settings


def load_setting():

    # print('Load Application setting from', config.sett_folder)
    settings = get_user_settings()

    # update config module
    config.__dict__.update(settings)


def save_setting():
    # web authentication
    
    settings = {key: config.__dict__.get(key) for key in config.settings_keys}

    try:
        file = os.path.join(config.sett_folder, 'setting.cfg')
        with open(file, 'w') as f:
            json.dump(settings, f, indent=4)
            print('settings saved in:', file)
    except Exception as e:
        print('save_setting() > error', e)
