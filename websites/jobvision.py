import requests
import csv
import time
import random

API_URL = "https://candidateapi.jobvision.ir/api/v1/JobPost/List"

CATEGORIES = [
    "developer",
    "data-science",
    "ui-ux",
    "digital-marketing"
]

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137 Safari/537.36"
    )
}

OUTPUT_FILE = "jobvision_jobs.csv"


# ----------------------------
# Parse job
# ----------------------------
def parse_job(job):

    company = job.get("company", {})
    location = job.get("location", {})
    props = job.get("properties", {})

    city = location.get("city", {})
    region = location.get("region", {})

    benefits = ", ".join(
        b.get("titleFa", "")
        for b in job.get("benefits", [])
    )

    categories = ", ".join(
        c.get("titleFa", "")
        for c in job.get("jobCategories", [])
    )

    location_text = city.get("titleFa", "") or ""
    if region:
        location_text += " - " + region.get("titleFa", "")

    return {
        "job_id": job.get("id"),
        "title": job.get("title"),

        "company": company.get("nameFa"),
        "company_en": company.get("nameEn"),
        "company_logo": company.get("logoUrl"),

        "location": location_text,

        "remote": props.get("isRemote"),
        "urgent": props.get("isUrgent"),
        "internship": props.get("isInternship"),

        "experience_years": props.get("requiredRelatedExperienceYears"),

        "work_type": job.get("workType", {}).get("titleFa"),
        "seniority": job.get("seniorityLevel", {}).get("titleFa"),
        "industry": job.get("industry", {}).get("titleFa"),
        "gender": job.get("gender", {}).get("titleFa"),

        "salary": job.get("salary"),

        "benefits": benefits,
        "categories": categories,

        "publish_time": job.get("activationTime", {}).get("beautifyFa"),
        "publish_date": job.get("activationTime", {}).get("date"),

        "expire_date": job.get("expireTime", {}).get("date"),

        "job_url": f"https://jobvision.ir/jobs/{job.get('id')}"
    }


# ----------------------------
# Fetch page
# ----------------------------
def fetch_page(category, page):

    payload = {
        "pageSize": 30,
        "requestedPage": page,
        "sortBy": 1,
        "searchTimeRange": 4,
        "jobCategoryUrlTitle": category,
    }

    response = requests.post(
        API_URL,
        json=payload,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ----------------------------
# Main
# ----------------------------
def main():

    all_jobs = []
    seen = set()

    for category in CATEGORIES:

        print(f"\n===== CATEGORY: {category} =====")

        page = 1

        while True:

            print(f"[*] Page {page}")

            try:
                data = fetch_page(category, page)
                jobs = data.get("data", {}).get("jobPosts", [])

                if not jobs:
                    print("[✓] No more jobs, moving next category")
                    break

                for job in jobs:

                    job_id = job.get("id")

                    if job_id in seen:
                        continue

                    seen.add(job_id)

                    all_jobs.append(parse_job(job))

                print(f"[+] Collected: {len(jobs)} jobs")

            except Exception as e:
                print(f"[!] Error: {e}")
                break

            page += 1

            delay = random.randint(1, 4)
            print(f"[*] Sleeping {delay}s...\n")
            time.sleep(delay)

    # ----------------------------
    # Save CSV
    # ----------------------------
    if all_jobs:

        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:

            writer = csv.DictWriter(
                f,
                fieldnames=all_jobs[0].keys()
            )

            writer.writeheader()
            writer.writerows(all_jobs)

        print(f"\n[✓] Saved {len(all_jobs)} jobs to {OUTPUT_FILE}")

    else:
        print("[!] No data collected")


if __name__ == "__main__":
    main()