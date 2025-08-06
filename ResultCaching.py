class ResultCache:
    def __init__(self):
        self.cache = {}
        self.ttl = 3600  # 1 hour
    
    def get_cached_result(self, data_hash, agent_type):
        key = f"{agent_type}:{data_hash}"
        if key in self.cache:
            timestamp, result = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return result
        return None
