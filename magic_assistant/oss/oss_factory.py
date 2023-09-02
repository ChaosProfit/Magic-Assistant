from magic_assistant.oss.minio_adapter import MinioAdapter
from magic_assistant.config.oss_config import OssConfig


class OssFactory:
    def __init__(self):
        self._storage_adapter = None

    def init(self, oss_config: OssConfig) -> int:
        if oss_config.type == "minio":
            self._storage_adapter = MinioAdapter()
            self._storage_adapter.init(oss_config)
        else:
            return -1

        if self._storage_adapter.has_bucket(oss_config.default_bucket) is False:
            self._storage_adapter.add_bucket(oss_config.default_bucket)

        return 0

    def has_bucket(self, bucket_name: str) -> bool:
        return self._storage_adapter.hasBucket(bucket_name)

    def add_bucket(self, bucket_name: str) -> int:
        return self._storage_adapter.addBucket(bucket_name)

    def add_file(self, file_id: str, file_bytes: bytes, bucket_name: str= "default") -> int:

        return self._storage_adapter.add_file(file_id, file_bytes, bucket_name)

    def get_file(self, file_id: str, bucket_name: str) -> (bytes, int):
        return self._storage_adapter.get_file(bucket_name, file_id)

    def del_file(self, file_id: str, bucket_name: str) -> int:
        return self._storage_adapter.delFile(bucket_name, file_id)
