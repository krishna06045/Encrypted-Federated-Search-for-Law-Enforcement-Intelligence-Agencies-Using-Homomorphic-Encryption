import json
import os
import hashlib
import time

class Blockchain:
    def __init__(self, filename="blockchain_log.json"):
        self.filename = filename
        self.chain = self.load_chain()

    def create_genesis_block(self):
        return {
            "index": 0,
            "timestamp": time.time(),
            "data": "Genesis Block",
            "prev_hash": "0",
            "hash": "0"
        }

    def load_chain(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        else:
            return [self.create_genesis_block()]

    def get_last_block(self):
        return self.chain[-1]

    def calculate_hash(self, block):
        block_str = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_str).hexdigest()

    def add_block(self, data):
        last_block = self.get_last_block()
        new_block = {
            "index": last_block["index"] + 1,
            "timestamp": time.time(),
            "data": data,
            "prev_hash": last_block["hash"]
        }
        new_block["hash"] = self.calculate_hash(new_block)
        self.chain.append(new_block)

    def persist_chain(self):
        with open(self.filename, "w") as f:
            json.dump(self.chain, f, indent=2)
