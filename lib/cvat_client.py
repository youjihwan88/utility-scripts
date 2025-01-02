import time
import logging
import requests
import itertools
from dotenv import dotenv_values
from dataclasses import dataclass
from requests.auth import HTTPBasicAuth


class CvatConfig:
    __config = dotenv_values("configs/cvat_config.env")

    CVAT_USERNAME = __config.get("CVAT_USERNAME")
    CVAT_PASSWORD = __config.get("CVAT_PASSWORD")
    CVAT_HOST = __config.get("CVAT_HOST")
    CVAT_PORT = __config.get("CVAT_PORT")
    CVAT_ORG_ID = int(__config.get("CVAT_ORG_ID"))
    WAIT_TIME_SEC = int(__config.get("WAIT_TIME_SEC"))


class CvatClient:
    auth = HTTPBasicAuth(
        username=CvatConfig.CVAT_USERNAME,
        password=CvatConfig.CVAT_PASSWORD,
    )
    url = f"http://{CvatConfig.CVAT_HOST}:{CvatConfig.CVAT_PORT}"

    class ProjectApi:
        @staticmethod
        def get_proejct(project_id: int) -> dict | None:
            response = requests.get(
                f"{CvatClient.url}/api/projects/{project_id}",
                auth=CvatClient.auth,
            )
            if response.status_code != 200:
                logging.error("API Exception: %s", response.text)
                return None

            return response.json()

        @staticmethod
        def get_project_list(
            sort: str | None = "id",
        ) -> list | None:
            project_list = []
            for page in itertools.count(start=1):
                params = {"page": page} | ({"sort": sort} if sort is not None else {})
                response = requests.get(
                    f"{CvatClient.url}/api/projects",
                    auth=CvatClient.auth,
                    params=params,
                )

                if response.status_code != 200:
                    logging.error("API Exception: %s", response.text)
                    return None

                response_data = response.json()
                project_list.extend(response_data["results"])
                if response_data["next"] is None:
                    break

            return project_list

    class JobApi:
        @staticmethod
        def get_job(job_id: int) -> dict | None:
            response = requests.get(
                f"{CvatClient.url}/api/jobs/{job_id}",
                auth=CvatClient.auth,
            )
            if response.status_code != 200:
                logging.error("API Exception: %s", response.text)
                return None

            return response.json()

        @staticmethod
        def get_job_list(
            sort: str | None = "id",
            project_id: int | None = None,
        ) -> list | None:
            job_list = []
            for page in itertools.count(start=1):
                params = (
                    {"page": page}
                    | ({"sort": sort} if sort is not None else {})
                    | ({"project_id": project_id} if project_id is not None else {})
                )
                response = requests.get(
                    f"{CvatClient.url}/api/jobs",
                    auth=CvatClient.auth,
                    params=params,
                )

                if response.status_code != 200:
                    logging.error("API Exception: %s", response.text)
                    return None

                response_data = response.json()
                job_list.extend(response_data["results"])
                if response_data["next"] is None:
                    break

            return job_list

        @staticmethod
        def download_job_annotation(
            id: int,
            filename: str | None = None,
            location: str = "local",
            _foramt: str = "YOLO 1.1",
        ) -> None:

            action = None
            while True:
                params = (
                    ({"action": action} if action is not None else {})
                    | ({"filename": filename} if filename is not None else {})
                    | ({"location": location} if location is not None else {})
                    | ({"format": _foramt})
                )

                response = requests.get(
                    f"{CvatClient.url}/api/jobs/{id}/annotations",
                    auth=CvatClient.auth,
                    params=params,
                )

                # Exporting has been started
                if response.status_code == 202:
                    pass
                # Output file is ready for downloading
                elif response.status_code == 201:
                    action = "download"
                # Download of file started
                elif response.status_code == 200:
                    break
                # Error Casese
                else:
                    logging.error("API Exception: %s", response.text)
                    return

                time.sleep(CvatConfig.WAIT_TIME_SEC)

            return response.content
