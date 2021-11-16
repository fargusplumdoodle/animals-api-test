from typing import Optional, List, Any, Union

import requests
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class AnimalsAPI:
    SERVER = "http://localhost:3123"
    MAX_TIMEOUT = 20
    MAXIMUM_RETRIES = 10

    class APIException(Exception):
        def __init__(
            self, msg: str, response: requests.Response, method: str, uri: str, **kwargs
        ):
            logger.error(
                msg,
                extra={
                    "status_code": response.status_code,
                    "response_content": response.content,
                    "method": method,
                    "uri": uri,
                    **kwargs,
                },
            )
            super().__init__()

    @classmethod
    def _paginated_request(cls, method: str, uri: str) -> List[Any]:
        page = 0
        total_pages: Optional[int] = None
        items = []
        while not total_pages or page <= total_pages:
            params = {"page": page}
            r = cls._request(method, uri, params=params, expected_status=200)

            data = r.json()
            page += 1
            total_pages = data["total_pages"]
            items += data["items"]

        return items

    @classmethod
    def _request(
        cls,
        method: str,
        uri: str,
        params: Optional[dict] = None,
        data: Optional[Union[list, dict]] = None,
        expected_status=200,
    ) -> requests.Response:
        request_kwargs = {"json": data} if method == "post" else {"params": params}
        for x in range(cls.MAXIMUM_RETRIES):
            r = getattr(requests, method)(
                f"{cls.SERVER}{uri}", timeout=cls.MAX_TIMEOUT, **request_kwargs
            )

            if r.status_code >= 500:
                # Trying again due to server issues
                logger.warning("Received 5xx status code, retrying")
                continue
            if r.status_code != expected_status:
                raise cls.APIException(
                    f"Unexpected status code: {r.status_code}",
                    r,
                    method,
                    uri,
                    params=params,
                    expected_status=expected_status,
                )

            return r

        raise cls.APIException(
            f"Maximum retries hit: {cls.MAXIMUM_RETRIES}",
            r,
            method,
            uri,
            params=params,
            expected_status=expected_status,
        )

    @classmethod
    def list(cls):
        return cls._paginated_request("get", "/animals/v1/animals")

    @classmethod
    def detail(cls, animal_id: int):
        r = cls._request("get", f"/animals/v1/animals/{animal_id}")
        return r.json()

    @classmethod
    def send_home(cls, animals: list) -> None:
        start_pos = 0
        count = 0
        while start_pos < len(animals):
            end_pos = start_pos + 100

            cls._request(
                "post",
                f"/animals/v1/home",
                data=animals[start_pos:end_pos],
                expected_status=200,
            )
            start_pos = end_pos
            count += 1


if __name__ == "__main__":
    logger.info("Getting animals list")
    animals_list = AnimalsAPI.list()

    logger.info("Getting animal details")
    animals = [AnimalsAPI.detail(animal["id"]) for animal in animals_list]
    for animal in animals:
        animal["friends"] = animal["friends"].split(",")

    logger.info("Sending animals home")
    AnimalsAPI.send_home(animals)
