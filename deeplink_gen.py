import base64

class Deeplink:
    @staticmethod
    def encode(payload: str) -> str:
        return base64.urlsafe_b64encode(payload.encode()).decode()
    
    @staticmethod
    def decode(encode_str: str) -> str:
        return base64.urlsafe_b64decode(encode_str.encode()).decode()
    

    
    @classmethod
    def generate(cls, payload: str) -> str:
        encode_str = cls.encode(payload)
        return f'https://max.ru/id693800725647_bot?start={encode_str}'
    

    @classmethod
    def extract_link(cls, deep_link: str):
        parts = deep_link.split(maxsplit=1)
        if len(parts) > 1:
            return cls.decode(parts[1])


