class UnexpectedDataFormatException(Exception):
    """Custom exception for unexpected data format errors."""

    def __init__(self, message=None, code=None):
        self.message = message or "Data queried is in an unexpected format."
        self.code = code
        super().__init__(self.message)