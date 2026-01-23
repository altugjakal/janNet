
class MaxSim():
    def __init__(self, final_count):
        self.final_count = final_count

    def calculate(self, term, contents):

        tokenized_contents = {}
        for url, content in contents.items():
            pass