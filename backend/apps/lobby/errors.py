class LobbyError(Exception):

    def __init__(self, text: str):
        self.message = text


