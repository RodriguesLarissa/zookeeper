class Message:
    """ Creation of message class """

    def __init__(self, type: str, key: str, timestamp: int, value: str = None, hash_table = {}):
        self.type = type
        self.key = key
        self.timestamp = timestamp
        self.value = value
        self.hash_table = hash_table