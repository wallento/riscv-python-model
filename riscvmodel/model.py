from .variant import Variant

class Model(object):
    def __init__(self, variant: Variant):
        self.variant = variant
        self.intreg = []