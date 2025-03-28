"""
Base de données des préfixes d'adresses MAC connus pour les fabricants.
Ces préfixes permettent d'identifier le fabricant d'un appareil à partir de son adresse MAC.
"""

# Base de données des préfixes d'adresses MAC connues pour les fabricants
MAC_PREFIX_DATABASE = {
    # Freebox
    "14:0C:76": {"company": "Freebox SA", "device_type": "Freebox", "model": "Freebox Player", "friendly_name": "Freebox Player"},
    "E4:F0:42": {"company": "Freebox SA", "device_type": "Freebox", "model": "Freebox Revolution", "friendly_name": "Freebox Revolution"},
    "DC:F5:05": {"company": "Freebox SA", "device_type": "Freebox", "model": "Freebox Delta", "friendly_name": "Freebox Delta"},
    "38:17:E3": {"company": "Freebox SA", "device_type": "Freebox", "model": "Freebox Mini 4K", "friendly_name": "Freebox Mini 4K"},
    "F4:CA:E5": {"company": "Freebox SA", "device_type": "Freebox", "model": "Freebox", "friendly_name": "Freebox"},
    "54:B8:0A": {"company": "Freebox SA", "device_type": "Freebox", "model": "Freebox Pop", "friendly_name": "Freebox Pop"},
    "00:07:CB": {"company": "FREEBOX SA", "device_type": "Freebox", "model": "Freebox", "friendly_name": "Freebox"},
    "00:24:D4": {"company": "FREEBOX SAS", "device_type": "Freebox", "model": "Freebox", "friendly_name": "Freebox"},
    "70:FC:8F": {"company": "Freebox SA", "device_type": "Freebox", "model": "Freebox Server", "friendly_name": "Freebox Server"},
    "14:A7:2B": {"company": "Freebox SA", "device_type": "Freebox", "model": "Freebox Server Mini", "friendly_name": "Freebox Server Mini"},
    "F4:CA:E5": {"company": "Freebox SA", "device_type": "Freebox", "model": "Freebox Player Mini", "friendly_name": "Freebox Player Mini"},
    
    # Apple
    "00:03:93": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:0A:27": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:0A:95": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:0D:93": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:10:FA": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:11:24": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:14:51": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:16:CB": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:17:F2": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:19:E3": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:1C:B3": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:1D:4F": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:1E:52": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:1E:C2": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:1F:5B": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:1F:F3": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:21:E9": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:22:41": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:23:12": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:23:32": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:23:6C": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:23:DF": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:24:36": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:25:00": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:25:4B": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:25:BC": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:26:08": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:26:4A": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:26:B0": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:26:BB": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:30:65": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "00:3E:E1": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "04:0C:CE": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "04:15:52": {"company": "Apple, Inc.", "device_type": "Mobile", "model": "iPhone", "friendly_name": "iPhone"},
    "04:1E:64": {"company": "Apple, Inc.", "device_type": "Mobile", "model": "iPhone", "friendly_name": "iPhone"},
    "04:26:65": {"company": "Apple, Inc.", "device_type": "Mobile", "model": "iPhone", "friendly_name": "iPhone"},
    "04:48:9A": {"company": "Apple, Inc.", "device_type": "Mobile", "model": "iPhone", "friendly_name": "iPhone"},
    "04:4B:ED": {"company": "Apple, Inc.", "device_type": "Mobile", "model": "iPhone", "friendly_name": "iPhone"},
    "04:52:F7": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "04:54:53": {"company": "Apple, Inc.", "device_type": "Mobile", "model": "iPhone", "friendly_name": "iPhone"},
    "04:69:F8": {"company": "Apple, Inc.", "device_type": "Mobile", "model": "iPhone", "friendly_name": "iPhone"},
    "04:D3:CF": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "04:E5:36": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "04:F1:3E": {"company": "Apple, Inc.", "device_type": "Ordinateur", "model": "Mac", "friendly_name": "Mac"},
    "04:F7:E4": {"company": "Apple, Inc.", "device_type": "Audio", "model": "AirPods", "friendly_name": "AirPods"},
    
    # Samsung
    "00:1A:8A": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "00:21:19": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "00:23:39": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "00:25:67": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "00:E0:64": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "08:08:C2": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "14:49:E0": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "14:7D:DA": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "14:89:FD": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "14:9F:3C": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "14:A3:64": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "1C:3A:DE": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "1C:62:B8": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "1C:66:AA": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    "1C:AF:05": {"company": "Samsung Electronics Co.,Ltd", "device_type": "Mobile", "model": "Galaxy", "friendly_name": "Samsung Galaxy"},
    
    # Google
    "00:1A:11": {"company": "Google, Inc.", "device_type": "Domotique", "model": "Home", "friendly_name": "Google Home"},
    "08:9E:08": {"company": "Google, Inc.", "device_type": "Domotique", "model": "Chromecast", "friendly_name": "Google Chromecast"},
    "20:DF:B9": {"company": "Google, Inc.", "device_type": "Domotique", "model": "Home", "friendly_name": "Google Home"},
    "3C:5A:B4": {"company": "Google, Inc.", "device_type": "Domotique", "model": "Chromecast", "friendly_name": "Google Chromecast"},
    "54:60:09": {"company": "Google, Inc.", "device_type": "Mobile", "model": "Pixel", "friendly_name": "Google Pixel"},
    "94:95:A0": {"company": "Google, Inc.", "device_type": "Mobile", "model": "Pixel", "friendly_name": "Google Pixel"},
    "F4:F5:D8": {"company": "Google, Inc.", "device_type": "Domotique", "model": "Chromecast", "friendly_name": "Google Chromecast"},
    "F4:F5:E8": {"company": "Google, Inc.", "device_type": "Domotique", "model": "Chromecast", "friendly_name": "Google Chromecast"},
    "F8:8F:CA": {"company": "Google, Inc.", "device_type": "Domotique", "model": "Chromecast", "friendly_name": "Google Chromecast"},
    
    # Sony
    "00:01:4A": {"company": "Sony Corporation", "device_type": "Audio", "model": "Unknown", "friendly_name": "Sony Device"},
    "00:24:BE": {"company": "Sony Corporation", "device_type": "Audio", "model": "Unknown", "friendly_name": "Sony Device"},
    "30:F9:ED": {"company": "Sony Corporation", "device_type": "Audio", "model": "WH-1000XM", "friendly_name": "Sony Headphones"},
    "40:2B:A1": {"company": "Sony Corporation", "device_type": "Audio", "model": "WH-1000XM", "friendly_name": "Sony Headphones"},
    "58:48:22": {"company": "Sony Corporation", "device_type": "Audio", "model": "WH-1000XM", "friendly_name": "Sony Headphones"},
    "D8:D4:3C": {"company": "Sony Corporation", "device_type": "Audio", "model": "WH-1000XM", "friendly_name": "Sony Headphones"},
    
    # Microsoft
    "00:15:5D": {"company": "Microsoft Corporation", "device_type": "Ordinateur", "model": "Surface", "friendly_name": "Microsoft Surface"},
    "28:18:78": {"company": "Microsoft Corporation", "device_type": "Ordinateur", "model": "Surface", "friendly_name": "Microsoft Surface"},
    "3C:A3:15": {"company": "Microsoft Corporation", "device_type": "Ordinateur", "model": "Surface", "friendly_name": "Microsoft Surface"},
    "58:82:A8": {"company": "Microsoft Corporation", "device_type": "Ordinateur", "model": "Surface", "friendly_name": "Microsoft Surface"},
    "60:45:BD": {"company": "Microsoft Corporation", "device_type": "Ordinateur", "model": "Surface", "friendly_name": "Microsoft Surface"},
    "7C:1E:52": {"company": "Microsoft Corporation", "device_type": "Ordinateur", "model": "Surface", "friendly_name": "Microsoft Surface"},
    "7C:ED:8D": {"company": "Microsoft Corporation", "device_type": "Ordinateur", "model": "Surface", "friendly_name": "Microsoft Surface"},
    
    # Xiaomi
    "00:EC:0A": {"company": "Xiaomi Communications Co Ltd", "device_type": "Mobile", "model": "Mi", "friendly_name": "Xiaomi Mi"},
    "0C:1D:AF": {"company": "Xiaomi Communications Co Ltd", "device_type": "Mobile", "model": "Redmi", "friendly_name": "Xiaomi Redmi"},
    "10:2A:B3": {"company": "Xiaomi Communications Co Ltd", "device_type": "Mobile", "model": "Mi", "friendly_name": "Xiaomi Mi"},
    "14:F6:5A": {"company": "Xiaomi Communications Co Ltd", "device_type": "Mobile", "model": "Mi", "friendly_name": "Xiaomi Mi"},
    "18:59:36": {"company": "Xiaomi Communications Co Ltd", "device_type": "Mobile", "model": "Mi", "friendly_name": "Xiaomi Mi"},
    "20:A7:83": {"company": "Xiaomi Communications Co Ltd", "device_type": "Mobile", "model": "Mi", "friendly_name": "Xiaomi Mi"},
    "28:6C:07": {"company": "Xiaomi Communications Co Ltd", "device_type": "Mobile", "model": "Mi", "friendly_name": "Xiaomi Mi"},
    "28:E3:1F": {"company": "Xiaomi Communications Co Ltd", "device_type": "Mobile", "model": "Mi", "friendly_name": "Xiaomi Mi"},
    "3C:BD:D8": {"company": "Xiaomi Communications Co Ltd", "device_type": "Mobile", "model": "Mi", "friendly_name": "Xiaomi Mi"},
    "40:31:3C": {"company": "Xiaomi Communications Co Ltd", "device_type": "Mobile", "model": "Redmi", "friendly_name": "Xiaomi Redmi"},
    
    # Écouteurs et audio
    "00:02:EE": {"company": "Nokia Denmark A/S", "device_type": "Audio", "model": "Bluetooth Audio", "friendly_name": "Nokia Audio"},
    "00:09:A7": {"company": "Bang & Olufsen A/S", "device_type": "Audio", "model": "Beoplay", "friendly_name": "B&O Beoplay"},
    "00:0D:3C": {"company": "i.Tech Dynamic Ltd", "device_type": "Audio", "model": "Bluetooth Audio", "friendly_name": "i.Tech Audio"},
    "00:0E:9F": {"company": "Temic SDS GmbH", "device_type": "Audio", "model": "Car Audio", "friendly_name": "Vehicle Audio System"},
    "00:11:67": {"company": "Integrated System Solution Corp.", "device_type": "Audio", "model": "Bluetooth Audio", "friendly_name": "ISSC Audio"},
    "00:12:A1": {"company": "BlueRadios, Inc.", "device_type": "Audio", "model": "Bluetooth Audio", "friendly_name": "BlueRadios Audio"},
    "00:13:17": {"company": "GN Netcom A/S", "device_type": "Audio", "model": "Jabra", "friendly_name": "Jabra Headset"},
    "00:14:A4": {"company": "Motorola Mobility, Inc.", "device_type": "Audio", "model": "Headset", "friendly_name": "Motorola Headset"},
    "00:16:94": {"company": "Sennheiser Communications A/S", "device_type": "Audio", "model": "Headset", "friendly_name": "Sennheiser Headset"},
    "00:17:00": {"company": "Kobe Steel, Ltd.", "device_type": "Audio", "model": "Bluetooth Audio", "friendly_name": "Bluetooth Audio"},
    "00:18:09": {"company": "CRESYN", "device_type": "Audio", "model": "Bluetooth Audio", "friendly_name": "CRESYN Audio"},
    "00:18:91": {"company": "Zhongshan General K-mate Electronics Co., Ltd", "device_type": "Audio", "model": "Bluetooth Audio", "friendly_name": "K-mate Audio"},
    "00:19:1D": {"company": "Nintendo Co.,Ltd.", "device_type": "Gaming", "model": "Nintendo Switch", "friendly_name": "Nintendo Switch"}
}

def get_device_info(mac_address: str) -> dict:
    """
    Récupère les informations du dispositif à partir de son adresse MAC.
    
    Args:
        mac_address: L'adresse MAC du dispositif
        
    Returns:
        Un dictionnaire contenant les informations du dispositif, ou None si non trouvé
    """
    if not mac_address:
        return None
        
    # Normalisation de l'adresse MAC pour la comparaison
    normalized_mac = mac_address.upper().replace(':', '')
    
    # Tente de trouver le préfixe exact
    for prefix, info in MAC_PREFIX_DATABASE.items():
        if normalized_mac.startswith(prefix.upper().replace(':', '')):
            return info
    
    return None