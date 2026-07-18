import requests
from database.repository import insert_categories


def fetch_and_save_job_categories():

    url = "https://candidateapi.jobvision.ir/api/v1/JobPost/GetAllSearchFilters"


    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://jobvision.ir",
        "Referer": "https://jobvision.ir/"
    }


    response = requests.get(
        url,
        headers=headers
    )


    response.raise_for_status()


    data = response.json()
    job_categories = (
        data
        .get("data", {})
        .get("jobCategories", [])
    )


    insert_categories({
        "jobCategories": job_categories
    })


    print(
        f"[✓] {len(job_categories)} categories updated"
    )