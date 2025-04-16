import logging
import sys
import traceback


class CustomException(Exception):
    def __init__(self, message=None, status_code=None):
        if message is None:
            message = self.__format_error()
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __format_error(self):
        try:
            _, exc_value, exc_tb = sys.exc_info()
            out = traceback.extract_tb(exc_tb)

            if out:
                last_trace = out[-1]
                return (
                    f"\n\t --[Error]: {exc_value}"
                    f"\n\t --[Reason]: {last_trace.line}"
                    f"\n\t --[File]: {last_trace.filename}"
                    f"\n\t --[LOC]: {last_trace.lineno}"
                    f"\n\t --[Function]: {last_trace.name}\n"
                )
            else:
                return f"\n\t --[Error]: {exc_value}\n"

        except Exception as e:
            logging.error(f"Error formatting CustomException: {e}")
            return "Unknown error occurred"

    def __str__(self):
        return self.message
