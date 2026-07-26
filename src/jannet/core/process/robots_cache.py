

class RobotsCache:
    def __init__(self, max_length):
        self.max_length = max_length
        self.allowance_dict = {}

    def add(
    self,
    domain: str,
    disallowed_pages: set[str],
    delay: float
    ) -> None:
        if len(self.allowance_dict) == self.max_length:
            self.allowance_dict.pop(next(iter(self.allowance_dict)))
        self.allowance_dict[domain] = (disallowed_pages, delay)

    def check(
    self,
    domain: str,
    url: str
    ) -> tuple[bool, float]:

        details = self.allowance_dict.get(domain)
        if details is None:
            return None

        disallowed_pages, delay = details

        return url not in disallowed_pages, delay





