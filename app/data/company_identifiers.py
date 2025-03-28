"""
Base de données des identifiants de fabricants Bluetooth.
Source: https://www.bluetooth.com/specifications/assigned-numbers/company-identifiers/
"""

# Dictionnaire des noms de compagnies basé sur les codes Bluetooth SIG
COMPANY_IDENTIFIERS = {
    # Fabricants majeurs
    0x004C: "Apple, Inc.",
    0x0006: "Microsoft",
    0x000F: "Broadcom Corporation",
    0x0075: "Samsung Electronics Co. Ltd.",
    0x0001: "Ericsson Technology Licensing",
    0x00E0: "Google Inc.",
    0x008A: "Bose Corporation",
    0x000A: "Nokia",
    0x00D2: "Seiko Epson Corporation",
    0x004D: "Motorola Mobility LLC",
    0x0002: "Intel Corp.",
    0x00E8: "Fitbit, Inc.",
    0x00D7: "Continental Automotive Systems",
    0x00D6: "Hewlett-Packard Company",
    0x0197: "Huawei Technologies Co., Ltd.",
    0x038F: "XIAOMI Inc.",
    0x0499: "Ruuvi Innovations Ltd.",
    0x0157: "Anhui Huami Information Technology Co., Ltd.",
    0x0030: "ST Microelectronics",
    0x0059: "Nordic Semiconductor ASA",
    0x0131: "Cypress Semiconductor",
    0x02D5: "Spotify AB",
    0x0047: "Plantronics, Inc.",
    0x0078: "Sony Corporation",
    0x0301: "Sony Mobile Communications Inc.",
    0x0080: "Toshiba Corporation",
    0x0046: "Bang & Olufsen A/S",
    
    # Audio et écouteurs
    0x01D7: "Jabra",
    0x00C6: "Beats Electronics, LLC",
    0x0310: "Realtek Semiconductor Corp.",
    0x004E: "Razer Inc.",
    0x0177: "Jaybird LLC",
    0x0126: "SOL REPUBLIC",
    0x0362: "HARMAN International Industries, Inc.",
    0x0111: "Logitech International SA",
    0x00F0: "JVCKENWOOD Corporation",
    
    # Domotique et IoT
    0x0186: "Signify Netherlands B.V. (formerly Philips Lighting B.V.)",
    0x0057: "Garmin International, Inc.",
    0x029F: "Tile, Inc.",
    0x0107: "Belkin International, Inc.",
    0x000B: "Sonos Inc.",
    0x01D9: "Flic",
    0x05D7: "LEDVANCE GmbH",
    0x0276: "IKEA of Sweden AB",
    0x026A: "Ilumi Solutions Inc.",
    0x025A: "Roku, Inc.",

    # Gaming
    0x0154: "Nintendo Co., Ltd.",
    0x0012: "Sony Interactive Entertainment Inc.",
    0x01A4: "Valve Corporation",
    
    # Mobilité
    0x0036: "TomTom International BV",
    0x00E9: "Visteon Corporation",
    
    # Fabricants français
    0x01E5: "Parrot SA",
    0x019A: "Arcadyan Corporation",
    0x012A: "INGENICO",
    0x0060: "SiRF Technology, Inc.",
    
    # Freebox spécifique
    0x3213: "FREEBOX SAS",
    0x07CB: "FREEBOX SA",
    0x24D4: "FREEBOX SAS",
    
    # Identifiants moins communs mais utiles
    0x01FF: "Facebook, Inc.",
    0x00F2: "Ubiquitous Computing Technology Corporation",
    0x0560: "Withings",
    0x013E: "Nod, Inc.",
    0x0052: "Tesla, Inc.",
    0x021A: "Bookie Corporation",
    0x034C: "GoPro, Inc.",
    0x02C4: "Procter & Gamble",
    0x0188: "Clover Network, Inc.",
    0x0500: "Wiliot LTD.",
    0x02CA: "Dyson Technology Limited",
    0x0201: "Polar Electro Oy",
    0x0352: "Snapchat Inc",
    0x0387: "ESET, spol. s r.o.",
    0x0225: "Nestlé Nespresso S.A.",
    0x03DA: "CRESCO Wireless, Inc",
    0x02A9: "Sonova AG",
    0x0626: "Audio-Technica Corporation",
    0x0520: "OPPO Electronics Co., Ltd.",
    0x06D6: "Instacart",
    0x0529: "Honor Device Co., Ltd.",
    0x0602: "OnePlus Technology (Shenzhen) Co., Ltd",
    0x0614: "DJI Innovations",
    0x0717: "Canon Inc.",
    0x0822: "Skullcandy Inc.",
    0x0831: "Sennheiser electronic GmbH & Co. KG"
}

def get_company_name(company_id: int) -> str:
    """
    Récupère le nom de l'entreprise à partir de son identifiant Bluetooth.
    
    Args:
        company_id: L'identifiant de l'entreprise au format hexadécimal
        
    Returns:
        Le nom de l'entreprise ou None si non trouvé
    """
    return COMPANY_IDENTIFIERS.get(company_id)