import requests
import csv
import time
import re

BASE_PAGE_URL = "https://quera.org/magnet/jobs"
OUTPUT_FILE = "quera_jobs.csv"

def get_build_id():
    """استخراج build_id از صفحه اصلی کوئرا مگنت"""
    print("[*] Fetching main page to extract build_id...")
    
    try:
        response = requests.get(BASE_PAGE_URL, timeout=30)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"[!] Error fetching main page: {e}")
        return None
    
    # الگوی regex برای پیدا کردن build_id در تگ script
    pattern = r'/_next/static/([a-zA-Z0-9_-]+)/_buildManifest\.js'
    match = re.search(pattern, html)
    
    if match:
        build_id = match.group(1)
        print(f"[+] Build ID found: {build_id}")
        return build_id
    else:
        print("[!] Could not find build_id in the page source")
        return None

def fetch_jobs(build_id):
    """دریافت تمام آگهی‌ها با build_id داده شده"""
    base_api_url = f"https://quera.org/_next/data/{build_id}/fa/magnet/jobs.json"
    all_jobs = []
    page = 1
    
    while True:
        print(f"[*] Fetching page {page}...")
        
        try:
            response = requests.get(f"{base_api_url}?page={page}", timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"[!] Error on page {page}: {e}")
            break
        
        edges = data.get("pageProps", {}).get("jobs", {}).get("edges", [])
        
        if not edges:
            print(f"[*] No more jobs. Done!")
            break
        
        for edge in edges:
            node = edge["node"]
            
            # استخراج تکنولوژی‌ها
            technologies = [
                t["technology"]["name"]
                for t in node.get("jobtechnology_set", [])
            ]
            
            # هندل کردن city و company که ممکنه null باشن
            city = node.get("city") or {}
            company = node.get("company") or {}
            
            job = {
                "id": node.get("pk", ""),
                "title": node.get("title", ""),
                "level": node.get("level", ""),
                "collaboration_type": node.get("collaboration_type", ""),
                "salary": node.get("salary", ""),
                "offers_remote": node.get("offers_remote", False),
                "publish_time": node.get("publish_time", ""),
                "company_name": company.get("name", ""),
                "city_name": city.get("name", ""),
                "technologies": ", ".join(technologies)
            }
            
            all_jobs.append(job)
        
        print(f"[+] Page {page}: {len(edges)} jobs collected | Total: {len(all_jobs)}")
        page += 1
        time.sleep(0.1)
    
    return all_jobs

def save_to_csv(jobs, filename):
    """ذخیره آگهی‌ها در فایل CSV"""
    if not jobs:
        print("[!] No data to save!")
        return
    
    fieldnames = [
        "id", "title", "level", "collaboration_type", "salary",
        "offers_remote", "publish_time", "company_name", "city_name", "technologies"
    ]
    
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)
    
    print(f"[✓] Saved {len(jobs)} jobs to '{filename}'")

if __name__ == "__main__":
    print("=" * 50)
    print("Quera Job Scraper - Dynamic Build ID")
    print("=" * 50)
    
    # مرحله ۱: استخراج build_id
    build_id = get_build_id()
    
    if not build_id:
        print("[!] Cannot continue without build_id. Exiting.")
        exit(1)
    
    # مرحله ۲: دریافت آگهی‌ها
    jobs = fetch_jobs(build_id)
    
    # مرحله ۳: ذخیره‌سازی
    save_to_csv(jobs, OUTPUT_FILE)
    
    print("=" * 50)
    print("Done!")
    print("=" * 50)