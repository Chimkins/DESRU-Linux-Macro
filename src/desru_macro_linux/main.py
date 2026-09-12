from evdev import InputDevice, list_devices, ecodes, UInput
import time
import select
from importlib.resources import files
import json

###### Acquiring Input Devices ######

def fetch_input_devices(): #Returns all valid mouse and keyboard input devices
    keyboards = []
    mice = []

    for path in list_devices():
        try:
            device = InputDevice(path)
            capabilities = device.capabilities()

            rel = capabilities.get(ecodes.EV_REL, []) 
            keys = capabilities.get(ecodes.EV_KEY, [])

            if ecodes.KEY_A in keys and ecodes.KEY_ENTER in keys: #Checks if it has the A key and the ENTER key as if it does it is probably a keyboard
                keyboards.append(device)
            
            elif ecodes.REL_X in rel and ecodes.REL_Y in rel: #Checks if it can move like a mouse as if it can move like a mouse it is probably a mouse
                mice.append(device)
        
        except PermissionError:
            print(f"Permission Denied {path} (Is your user in the input group?)")
        except OSError as e:
            print(f"Could not open {path}: {e}")

    return keyboards, mice

def get_keybinds(): #Gets keybinds from config.json and returns them as key codes !not a good implementation yet as a malformed config.json will result in a crash!
    config_file = files("desru_macro_linux").joinpath("config.json")
    keybinds = json.loads(config_file.read_text())
        
    try:
        scroll_up_key_codes = {
            ecodes.ecodes[key]
            for key in keybinds["scroll_up_keybinds"]
        }

        scroll_down_key_codes = {
            ecodes.ecodes[key]
            for key in keybinds["scroll_down_keybinds"]
        }
    except KeyError as e:
        raise ValueError(f"Unknown key in config.json: {e.args[0]!r}") from e

    overlapping_keys = set(scroll_up_key_codes) & set(scroll_down_key_codes)

    if overlapping_keys:
        raise ValueError(
            f"Please do not bind a key to both scroll directions: "
            f"{overlapping_keys}"
        )

    return scroll_down_key_codes, scroll_up_key_codes

##### Macro Stuff #####

INPUT_INTERVAL = 0.010 #10ms delay between scroll inputs

def get_wheel_direction(press_order, scroll_up_key_codes, scroll_down_key_codes): #handles wether mouse wheel up or down should be the macro'd input based on what the last pressed key is

    if not press_order:
        return None

    latest_key = max(press_order, key=press_order.get)

    if latest_key in scroll_up_key_codes:
        return 1

    if latest_key in scroll_down_key_codes:
        return -1

    return None

##### Main Loop #####

def main():
    keyboard, mice = fetch_input_devices()
    devices = keyboard + mice
    if not devices:
        raise RuntimeError("No keyboard or mouse found")

    scroll_down_key_codes, scroll_up_key_codes = get_keybinds()

    press_order = {}
    press_counter = 0

    ui = None #ui is the emulated free scroll mouse used to send the inputs to the kernel

    try:
        ui = UInput({
            ecodes.EV_REL: [
                ecodes.REL_WHEEL,
            ],
        }, name="Emulated Free Scroll Mouse") #sets the fake mouse to have a mouse wheel

        for device in devices:
            print(
                f"Listening to: "
                f"{device.name} ({device.path})"
            )

        next_scroll = time.monotonic()

        while True:
            now = time.monotonic()

            direction = get_wheel_direction(
                press_order,
                scroll_up_key_codes,
                scroll_down_key_codes
            )

            if direction is not None and now >= next_scroll:
                ui.write(
                    ecodes.EV_REL,
                    ecodes.REL_WHEEL,
                    direction
                )
                ui.syn()

                next_scroll += INPUT_INTERVAL #this keeps the 10ms delay from drifting

                if next_scroll < now:
                    next_scroll = now + INPUT_INTERVAL

            if direction is not None:
                timeout = max(0, next_scroll - time.monotonic())
            else:
                timeout = None

            readable, _, _ = select.select(
                devices,
                [],
                [],
                timeout
            ) #handles when to read input devices

            for device in readable: #This is a massive filter so only keys specified in the config.json get read and handled
                try:
                    for event in device.read():
                        if event.type == ecodes.EV_KEY:
                            if event.value == 2:
                                continue

                            if (
                                event.code not in scroll_up_key_codes
                                and event.code not in scroll_down_key_codes
                            ):
                                continue

                            if event.value == 1: #a macro key is being pressed
                                press_counter += 1
                                press_order[event.code] = press_counter

                            elif event.value == 0: #a macro key has been released
                                press_order.pop(event.code, None)
                        
                except OSError as e:
                    print(
                        f"Input device error ({device.path}): {e}"
                    )

    finally: #This just makes sure everything exits nicely when the macro is closed
        if ui is not None:
            ui.close()

        for device in devices:
            device.close()

if __name__ == "__main__":
    main()
