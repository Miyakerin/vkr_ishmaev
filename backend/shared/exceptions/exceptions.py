from typing import Optional, Any, Dict

from fastapi import HTTPException
from typing_extensions import Annotated, Doc


class CustomException(HTTPException):
    """
    Кастомная ошибка, к которой можно прикрутить логику логгирования или еще что
    """

    def __init__(
            self,
            status_code: Annotated[
                int,
                Doc(
                    """
                    HTTP status code to send to the client.
                    """
                ),
            ],
            detail: Annotated[
                Any,
                Doc(
                    """
                    Any data to be sent to the client in the `detail` key of the JSON
                    response.
                    """
                ),
            ] = None,
            headers: Annotated[
                Optional[Dict[str, str]],
                Doc(
                    """
                    Any headers to send to the client in the response.
                    """
                ),
            ] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
