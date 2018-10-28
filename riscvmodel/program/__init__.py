
class Program(object):
    def __init__(self, insns = None):
        if insns is None:
            self.insns = []
        else:
            self.insns = insns

    def expects(self):
        pass
