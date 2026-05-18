import uuid


class Trace:

    @staticmethod
    def generate() -> str:

        return str(uuid.uuid4())