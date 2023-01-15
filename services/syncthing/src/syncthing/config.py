import xml.etree.ElementTree as ET

class SyncthingConfig:

    def __init__(self, syncthing_config_file) -> None:
        tree = ET.parse(syncthing_config_file)
        self.root = tree.getroot()

    def apikey(self):
        return self.root.find("gui").find("apikey").text
