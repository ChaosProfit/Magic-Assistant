
class BaseLlm():
    def init(self):
        raise NotImplementedError("this method should be implemented")

    def run(self, input: str):
        raise NotImplementedError("this method should be implemented")