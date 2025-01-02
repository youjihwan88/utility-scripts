from dotenv import load_dotenv

load_dotenv()

import os
import logging
from lib.cvat_client import CvatClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


def save_content(content: bytes, filename: str) -> None:
    if not os.path.exists(".tmp/"):
        os.makedirs(".tmp")

    with open(f".tmp/{filename}", "wb") as f:
        f.write(content)

    return


def main():
    project_li = [18, 21, 30]
    for project_id in project_li:
        job_li = CvatClient.JobApi.get_job_list(project_id=project_id)

        for job in job_li:
            content = CvatClient.JobApi.download_job_annotation(id=job["id"])
            save_content(content, f"{job['id']}.zip")
            logging.info(f"Downloaded job {job['id']}")

    return


if __name__ == "__main__":
    main()
