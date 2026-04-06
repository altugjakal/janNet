from collections import defaultdict


class RobotsCache:
    def __init__(self, max_length):
        self.max_length = max_length
        self.allowance_dict = {}

    def add(self, domain, disallowed_pages, delay):
        if len(self.allowance_dict) == self.max_length:
            self.allowance_dict.pop(next(iter(self.allowance_dict)))
        self.allowance_dict[domain] = (disallowed_pages, delay)

    def check(self, domain, url):
        try:
            details = self.allowance_dict[domain]

            disallowed_pages = details[0]
            delay = details[1]
            if url not in disallowed_pages:
                return True, delay
            else:
                return False, delay
        except KeyError:
            raise KeyError




