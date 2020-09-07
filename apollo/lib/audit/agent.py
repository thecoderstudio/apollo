import io
import logging

BACKSPACE = 127


class AgentSessionLogger:
    input_array = bytearray()
    cursor = 0

    def register_input(self, input: str):
        input_byte = int.from_bytes(input.encode('utf-8'), byteorder='big')
        logging.info(input_byte)

        if (input_byte == BACKSPACE):
            self._backspace()
        else:
            self._add_byte(input_byte)

        logging.info(self.input_array)

    def _backspace(self):
        new_cursor = self.cursor - 1
        try:
            del self.input_array[new_cursor]
        except IndexError:
            return

        self._move_cursor(new_cursor)

    def _add_byte(self, input: bytes):
        try:
            self.input_array[self.cursor] = input
        except IndexError:
            self.input_array.append(input)
        self._move_cursor(self.cursor + 1)

    def _move_cursor(self, new_cursor: int):
        max_cursor = len(self.input_array)
        if new_cursor < 0:
            new_cursor = 0
        elif new_cursor > max_cursor:
            new_cursor = max_cursor

        self.cursor = new_cursor
