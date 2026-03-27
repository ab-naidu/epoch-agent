import aerospike, os, json
from datetime import datetime

class AerospikeMemory:
    def __init__(self):
        config = {
            "hosts": [(os.getenv("AEROSPIKE_HOST", "localhost"), int(os.getenv("AEROSPIKE_PORT", 3000)))]
        }
        self.client = aerospike.client(config).connect()
        self.ns = os.getenv("AEROSPIKE_NAMESPACE", "epoch")

    def write(self, set_name: str, key: str, data: dict):
        k = (self.ns, set_name, key)
        data["_updated_at"] = datetime.utcnow().isoformat()
        self.client.put(k, data)

    def read(self, set_name: str, key: str) -> dict | None:
        try:
            k = (self.ns, set_name, key)
            _, _, record = self.client.get(k)
            return record
        except aerospike.exception.RecordNotFound:
            return None

    def delete(self, set_name: str, key: str):
        k = (self.ns, set_name, key)
        self.client.remove(k)

    def scan_all(self, set_name: str) -> list[dict]:
        results = []
        scan = self.client.scan(self.ns, set_name)
        scan.foreach(lambda _, __, record: results.append(record))
        return results
