import requests
import math
import enlighten

# Fetch JSON data from the URL for devices
response_devices = requests.get("https://api.ipsw.me/v4/devices")
data_devices = response_devices.json()

# Parse the JSON data to extract identifier and name of all devices
devices = [(device["identifier"], device["name"]) for device in data_devices]

print("IPSW Downloader by evelynndev")

# Print the identifier and name of all devices
for identifier, name in devices:
    print(f"{identifier} - {name}")

print("")
identifier1 = input("iDevice Identifier: ")

# Fetch JSON data from the URL for firmwares of the selected device
response_firmwares = requests.get(f"https://api.ipsw.me/v4/device/{identifier1}")
try:
    response_firmwares.raise_for_status()  # Raise an exception for bad responses
    response_json = response_firmwares.json()
    firmwares = response_json["firmwares"]  # Access firmwares from the response
except requests.exceptions.HTTPError as err:
    print(f"HTTP error occurred: {err}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except ValueError as ve:
    print(f"Error parsing JSON: {ve}")
else:
    # Parse the JSON data to extract version, signed status, and buildid of all firmwares
    for firmware in firmwares:
        version = firmware["version"]
        signed = firmware["signed"]
        buildid = firmware["buildid"]
        url = firmware["url"]
        print(f"Version: {version}, Signed: {signed}, Build ID: {buildid}")

    print("\n")
    selected_version = input("Choose which firmware version you want to download: ")
    selected_firmware = next((fw for fw in firmwares if fw["version"] == selected_version), None)
    if selected_firmware:
        download_url = selected_firmware["url"]
        print(f"Downloading {selected_version} from URL: {download_url}")
        # Should be one global variable
        MANAGER = enlighten.get_manager()

        r = requests.get(f"{download_url}", stream=True)
        assert r.status_code == 200, r.status_code
        dlen = int(r.headers.get('Content-Length', '0')) or None

        with MANAGER.counter(color='purple', total=dlen and math.ceil(dlen / 2 ** 20), unit='MiB', leave=False) as ctr, \
                open(f"{identifier1}-{selected_version}.ipsw", 'wb', buffering=2 ** 24) as f:
            for chunk in r.iter_content(chunk_size=2 ** 20):
                print(chunk[-16:].hex().upper())
                f.write(chunk)
                ctr.update()
        # urllib.request.urlretrieve(f"{download_url}", f"{identifier1}-{selected_version}.ipsw", reporthook=download_progress_hook)
    else:
        print("Invalid firmware version selected.")
