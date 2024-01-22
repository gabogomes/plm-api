from typing import List, Union

from fastapi import HTTPException


class _MessageWithProperties:
    message: str
    properties: List[str]

    def __init__(self, message: str, properties: List[str]):
        self.message = message

        if properties:
            if type(properties) == list:
                self.properties = properties
            else:
                self.properties = [properties]
        else:
            self.properties = None


def _format_error(error: _MessageWithProperties):
    if error.properties:
        return {"message": error.message, "properties": error.properties}
    else:
        return {"message": error.message}


def raise_validation_exception(
    message_or_messages: Union[str, List[str]],
    property_or_properties: Union[str, List[str]] = None,
):
    messages = (
        message_or_messages
        if type(message_or_messages) == list
        else [message_or_messages]
    )

    raise HTTPException(
        400,
        [
            _format_error(_MessageWithProperties(message, property_or_properties))
            for message in messages
        ],
    )


class ValidationExceptionCollector:
    def __init__(self):
        self.errors: List[_MessageWithProperties] = []

    def add_error(self, message: str, properties: Union[str, List[str]] = None):
        """
        Add an error to the collection.
        """
        self.errors.append(_MessageWithProperties(message, properties))

    def errors_exist(self) -> bool:
        """
        Returns True if at least one error has been added.
        """
        return len(self.errors) > 0

    def raise_if_needed(self):
        """
        Raise a 400 exception if any errors were found.
        """
        if len(self.errors) > 0:
            raise HTTPException(400, [_format_error(error) for error in self.errors])
