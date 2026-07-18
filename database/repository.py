import json
from .connection import get_connection


def insert_job(jobs, source):

    conn = get_connection()
    cursor = conn.cursor()

    for job in jobs:

        salary = job.get("salary") or {}

        cursor.execute("""
        INSERT OR IGNORE INTO jobs (
            job_id, source,
            title, company, company_en, company_logo,
            location,
            remote, urgent, internship,
            experience_years, work_type, seniority, industry, gender,
            salary_id, salary_title, salary_titleFa, salary_titleEn, salary_max, salary_min,
            benefits, categories,
            publish_time, publish_date, expire_date,
            job_url,
            raw_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.get("job_id"),
            source,

            job.get("title"),
            job.get("company"),
            job.get("company_en"),
            job.get("company_logo"),

            job.get("location"),

            int(job.get("remote")) if job.get("remote") is not None else 0,
            int(job.get("urgent")) if job.get("urgent") is not None else 0,
            int(job.get("internship")) if job.get("internship") is not None else 0,

            job.get("experience_years"),
            job.get("work_type"),
            job.get("seniority"),
            job.get("industry"),
            job.get("gender"),

            salary.get("id"),
            salary.get("title"),
            salary.get("titleFa"),
            salary.get("titleEn"),
            salary.get("max"),
            salary.get("min"),

            json.dumps(job.get("benefits"), ensure_ascii=False),
            json.dumps(job.get("categories"), ensure_ascii=False),

            job.get("publish_time"),
            job.get("publish_date"),
            job.get("expire_date"),

            job.get("job_url"),

            json.dumps(job, ensure_ascii=False)
        ))

    conn.commit()
    conn.close()

def get_all_jobs(limit=100):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM jobs
    ORDER BY publish_date DESC
    LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def get_all_category_titles():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title_fa
        FROM categories
        ORDER BY title_fa
    """)

    result = [row[0] for row in cursor.fetchall()]

    conn.close()
    return result


def insert_categories(data):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
        DELETE FROM categories
    """)


    for category in data["jobCategories"]:

        cursor.execute("""
        INSERT INTO categories
        (
            id,
            url_title,
            title,
            title_fa,
            title_en
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            category.get("id"),
            category.get("urlTitle"),
            category.get("title"),
            category.get("titleFa"),
            category.get("titleEn")
        ))


    conn.commit()
    conn.close()


    print(f"[✓] {len(data['jobCategories'])} categories replaced")