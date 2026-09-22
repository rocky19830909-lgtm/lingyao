from abc import ABC, abstractmethod
from pathlib import Path
import os
import uuid


class BlobStorage(ABC):
    @abstractmethod
    def save(self, data: bytes, filename: str) -> tuple[str, int]: ...

    @abstractmethod
    def path(self, key: str) -> Path: ...


class LocalBlobStorage(BlobStorage):
    """Filesystem implementation. Replace with an S3Storage implementing this interface."""

    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, data: bytes, filename: str) -> tuple[str, int]:
        suffix = Path(filename).suffix.lower()
        key = f"{uuid.uuid4().hex}{suffix}"
        (self.root / key).write_bytes(data)
        return key, len(data)

    def path(self, key: str) -> Path:
        return self.root / Path(key).name


class TencentCOSStorage(BlobStorage):
    """Tencent COS implementation with a local read-through cache."""

    def __init__(self, root: str, region: str, bucket: str, secret_id: str, secret_key: str):
        from qcloud_cos import CosConfig, CosS3Client
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.bucket = bucket
        self.prefix = os.getenv("COS_PREFIX", "lingyao-ats/").strip("/") + "/"
        self.client = CosS3Client(CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Scheme="https"))

    def save(self, data: bytes, filename: str) -> tuple[str, int]:
        suffix = Path(filename).suffix.lower()
        key = f"{uuid.uuid4().hex}{suffix}"
        self.client.put_object(Bucket=self.bucket, Body=data, Key=self.prefix + key)
        (self.root / key).write_bytes(data)
        return key, len(data)

    def path(self, key: str) -> Path:
        safe_key = Path(key).name
        cached = self.root / safe_key
        if not cached.exists():
            response = self.client.get_object(Bucket=self.bucket, Key=self.prefix + safe_key)
            cached.write_bytes(response["Body"].get_raw_stream().read())
        return cached


def create_storage(root: str) -> BlobStorage:
    if os.getenv("STORAGE_BACKEND", "local").lower() == "cos":
        required = {name: os.getenv(name) for name in ("COS_REGION", "COS_BUCKET", "COS_SECRET_ID", "COS_SECRET_KEY")}
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError("COS configuration missing: " + ", ".join(missing))
        return TencentCOSStorage(root, required["COS_REGION"], required["COS_BUCKET"], required["COS_SECRET_ID"], required["COS_SECRET_KEY"])
    return LocalBlobStorage(root)
