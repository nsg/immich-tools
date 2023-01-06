
class ImmichAsset():
    def __init__(self) -> None:
        self.asset_uuid = None
        self.asset_name = None
        self.asset_path = None

class LocalAsset():
    def __init__(self) -> None:
        self.asset_hash = None
        self.asset_name = None
        self.asset_path = None

class AssetPair():
    def __init__(self) -> None:
        self.immich_asset = None
        self.local_asset = None
