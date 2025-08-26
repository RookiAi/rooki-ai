# tiny, zero-dependency decorator
def schema_id(value: str):
    def deco(cls):
        setattr(cls, "__schema_id__", value)
        return cls

    return deco
