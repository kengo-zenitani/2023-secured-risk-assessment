

class AssumedError(Exception):
    def __init__(self, stream: 'Stream', message: str):
        super().__init__(message)
        self.pos = stream.pos
        self.shift = stream.shift


class Stream:
    def __init__(self, data: str):
        self._data: str = data.replace("\r\n", "\n").replace("\r", "\n")

        self._pos: int = 0
        self._pos_stack: list[tuple[int, int]] = []

        self._shift: int = 0
        self._prev_letter: str = ""

    @property
    def pos(self) -> int:
        return self._pos

    @property
    def shift(self) -> int:
        return self._shift

    def at_end(self) -> bool:
        return self._pos >= len(self._data)

    def next(self) -> str:
        if self.at_end():
            return ""
        else:
            letter = self._data[self._pos]
            self._pos += 1
            if self._prev_letter == "\n":
                self._shift = 0
                self._prev_letter = letter
            else:
                self._shift += 1
            return letter

    def stepback(self):
        assert self.pos > 0
        self._pos -= 1

    def save(self):
        self._pos_stack.append((self.pos, self.shift))

    def restore(self):
        self._pos, self._shift = self._pos_stack.pop()

    def commit(self):
        self._pos_stack.pop()

    def rewind(self):
        self.restore()
        self.save()

    def __enter__(self):
        self.save()
        return self

    def __exit__(self, exc_type, exc_value, trace):
        if isinstance(exc_value, AssumedError):
            self.restore()
        else:
            self.commit()


