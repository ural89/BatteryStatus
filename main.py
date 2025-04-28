from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
import subprocess
import re


def run_upower_command(args):
    """ Helper to run a UPower command and return output lines """
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip().splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error running {' '.join(args)}: {e}")
        return []

def get_upower_devices():
    """ Get list of UPower device paths """
    return run_upower_command(['upower', '-e'])

def get_device_info(device):
    """ Get (model name, battery percentage) for a device """
    lines = run_upower_command(['upower', '-i', device])
    model = None
    percentage = None

    for line in lines:
        if 'model' in line:
            model = line.split(':', 1)[1].strip()
        elif 'percentage' in line:
            percentage = line.split(':', 1)[1].strip()

    return model, percentage


class BatteryStatusExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = []
        devices = get_upower_devices()

        for device in devices:
            model, percentage_str = get_device_info(device)
            if model and percentage_str:
                digits = ''.join(c for c in percentage_str if c.isdigit())
                if digits:
                    percentage = int(digits)
                    if percentage >= 70:
                        icon = 'images/battfull.png'
                    elif percentage >= 20:
                        icon = 'images/batthalf.png'
                    else:
                        icon = 'images/battlow.png'
                    items.append(
                    ExtensionResultItem(
                        icon= icon,
                        name=model,
                        description=f"{percentage}%",
                        on_enter=HideWindowAction()
                    )
                )

        return RenderResultListAction(items)


if __name__ == '__main__':
    BatteryStatusExtension().run()

