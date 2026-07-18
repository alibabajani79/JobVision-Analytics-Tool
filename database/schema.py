import sqlite3

DB_NAME = "jobs.db"


def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT,
        source TEXT,

        title TEXT,
        company TEXT,
        company_en TEXT,
        company_logo TEXT,

        location TEXT,

        remote INTEGER,
        urgent INTEGER,
        internship INTEGER,

        experience_years INTEGER,
        work_type TEXT,
        seniority TEXT,
        industry TEXT,
        gender TEXT,

        salary_id TEXT,
        salary_title TEXT,
        salary_titleFa TEXT,
        salary_titleEn TEXT,
        salary_max INTEGER,
        salary_min INTEGER,

        benefits TEXT,
        categories TEXT,

        publish_time TEXT,
        publish_date TEXT,
        expire_date TEXT,

        job_url TEXT,

        raw_data TEXT,

        PRIMARY KEY (job_id, source)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,

        url_title TEXT UNIQUE,

        title TEXT,
        title_fa TEXT,
        title_en TEXT
    )
    
    """)
    conn.commit()
    conn.close()

    print("[✓] Database initialized")
    
