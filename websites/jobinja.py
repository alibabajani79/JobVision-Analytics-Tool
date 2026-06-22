import requests
from bs4 import BeautifulSoup
import csv
import time
import random

BASE_URL = (
    "https://jobinja.ir/jobs?"
    "filters%5Bjob_categories%5D%5B0%5D="
    "%D9%88%D8%A8%D8%8C%E2%80%8C%20%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87%E2%80%8C"
    "%D9%86%D9%88%DB%8C%D8%B3%DB%8C%20%D9%88%20%D9%86%D8%B1%D9%85%E2%80%8C"
    "%D8%A7%D9%81%D8%B2%D8%A7%D8%B1&"
    "filters%5Bjob_categories%5D%5B2%5D="
    "IT%20%2F%20DevOps%20%2F%20Server&"
    "filters%5Bkeywords%5D%5B0%5D=&"
    "sort_by=published_at_desc"
)

OUTPUT_FILE = "jobinja_jobs.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
}


def extract_job_id(url):
    try:
        return url.split("/jobs/")[1].split("/")[0]
    except:
        return ""


def parse_job(job):

    title = ""
    job_url = ""
    job_id = ""
    company = ""
    city = ""
    contract = ""
    salary = ""
    publish_time = ""
    logo_url = ""

    title_tag = job.select_one(".c-jobListView__titleLink")

    if title_tag:
        title = title_tag.get_text(strip=True)
        job_url = title_tag.get("href", "")
        job_id = extract_job_id(job_url)

    logo_tag = job.select_one(".o-listView__itemIndicatorImage")
    if logo_tag:
        logo_url = logo_tag.get("src", "")

    publish_tag = job.select_one(".c-jobListView__passedDays")
    if publish_tag:
        publish_time = publish_tag.get_text(strip=True)

    meta_items = job.select(".c-jobListView__metaItem")

    if len(meta_items) >= 1:
        company = meta_items[0].get_text(" ", strip=True)

    if len(meta_items) >= 2:
        city = meta_items[1].get_text(" ", strip=True)

    if len(meta_items) >= 3:

        spans = meta_items[2].find_all("span")

        clean_spans = []

        for span in spans:
            text = span.get_text(" ", strip=True)

            if text:
                clean_spans.append(text)

        if len(clean_spans) >= 1:
            contract = clean_spans[0]

        if len(clean_spans) >= 2:
            salary = clean_spans[1]

    premium = (
        "c-jobListView__item--premium"
        in job.get("class", [])
    )

    return {
        "job_id": job_id,
        "title": title,
        "company": company,
        "city": city,
        "contract": contract,
        "salary": salary,
        "publish_time": publish_time,
        "premium": premium,
        "job_url": job_url,
        "logo_url": logo_url,
    }


def fetch_page(page):

    url = f"{BASE_URL}&page={page}"

    print(f"[*] Fetching page {page}")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    jobs = soup.select("li.c-jobListView__item")

    return jobs


def save_csv(data):

    fieldnames = [
        "job_id",
        "title",
        "company",
        "city",
        "contract",
        "salary",
        "publish_time",
        "premium",
        "job_url",
        "logo_url",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(data)

    print(f"[✓] Saved {len(data)} jobs to {OUTPUT_FILE}")


def main():

    all_jobs = []

    for page in range(1, 11):

        try:
            jobs_html = fetch_page(page)

            print(
                f"[+] Found {len(jobs_html)} jobs "
                f"on page {page}"
            )

            for job in jobs_html:
                all_jobs.append(parse_job(job))

        except Exception as e:
            print(f"[!] Error on page {page}: {e}")

        delay = random.randint(1, 4)

        print(f"[*] Sleeping {delay} seconds...\n")

        time.sleep(delay)

    save_csv(all_jobs)

    print("=" * 50)
    print(f"Done! Total jobs: {len(all_jobs)}")
    print("=" * 50)


if __name__ == "__main__":
    main()