from .connection import get_connection


def remote_salary_by_categories(categories):

    conn = get_connection()
    cursor = conn.cursor()

    result = {}


    for category in categories:

        cursor.execute("""
            SELECT
                remote,
                salary_min,
                salary_max
            FROM jobs
            WHERE categories LIKE ?
        """, (f"%{category}%",))


        rows = cursor.fetchall()


        remote_count = 0
        onsite_count = 0

        remote_salaries = []
        onsite_salaries = []


        for row in rows:

            salary = None

            if row["salary_min"] is not None and row["salary_max"] is not None:
                salary = (
                    row["salary_min"] + row["salary_max"]
                ) / 2


            if row["remote"] == 1:

                remote_count += 1

                if salary is not None:
                    remote_salaries.append(salary)


            elif row["remote"] == 0:

                onsite_count += 1

                if salary is not None:
                    onsite_salaries.append(salary)



        result[category] = {

            "remote": {
                "count": remote_count,
                "salary_count": len(remote_salaries),
                "average_salary": round(
                    sum(remote_salaries) / len(remote_salaries)
                ) if remote_salaries else 0
            },


            "onsite": {
                "count": onsite_count,
                "salary_count": len(onsite_salaries),
                "average_salary": round(
                    sum(onsite_salaries) / len(onsite_salaries)
                ) if onsite_salaries else 0
            }
        }


    conn.close()

    return result

def work_type_by_categories(categories):

    conn = get_connection()
    cursor = conn.cursor()

    result = {}

    for category in categories:
        cursor.execute("""
            SELECT work_type, salary_min, salary_max
            FROM jobs
            WHERE categories LIKE ?
        """, (f"%{category}%",))

        rows = cursor.fetchall()

        work_type_data = {}

        for row in rows:
            work_type = row["work_type"] if row["work_type"] else "نامشخص"

            if work_type not in work_type_data:
                work_type_data[work_type] = {"count": 0, "salaries": []}

            work_type_data[work_type]["count"] += 1

            if row["salary_min"] is not None and row["salary_max"] is not None:
                job_average_salary = (row["salary_min"] + row["salary_max"]) / 2
                work_type_data[work_type]["salaries"].append(job_average_salary)

        work_type_summary = {}

        for work_type, data in work_type_data.items():
            salaries = data["salaries"]
            work_type_summary[work_type] = {
                "count": data["count"],
                "jobs_with_salary": len(salaries),
                "average_salary": round(sum(salaries) / len(salaries)) if salaries else 0
            }

        result[category] = work_type_summary

    conn.close()

    return result

def average_salary_by_categories(categories):

    conn = get_connection()
    cursor = conn.cursor()

    result = {}

    for category in categories:
        cursor.execute("""
            SELECT 
                salary_min,
                salary_max
            FROM jobs
            WHERE categories LIKE ?
        """, (f"%{category}%",))

        rows = cursor.fetchall()

        salaries = []


        for row in rows:

            if row["salary_min"] is None or row["salary_max"] is None:
                continue


            job_average_salary = (
                row["salary_min"] + row["salary_max"]
            ) / 2


            salaries.append(job_average_salary)



        result[category] = {
            "total_jobs": len(rows),
            "jobs_with_salary": len(salaries),
            "average_salary": round(
                sum(salaries) / len(salaries)
            ) if salaries else 0
        }


    conn.close()

    return result

def gender_distribution_by_categories(categories):

    conn = get_connection()
    cursor = conn.cursor()

    result = {}

    for category in categories:
        cursor.execute("""
            SELECT gender
            FROM jobs
            WHERE categories LIKE ?
        """, (f"%{category}%",))

        rows = cursor.fetchall()

        gender_counts = {}

        for row in rows:
            gender = row["gender"] if row["gender"] else "نامشخص"
            gender_counts[gender] = gender_counts.get(gender, 0) + 1

        result[category] = {
            "total_jobs": len(rows),
            "gender_distribution": gender_counts
        }

    conn.close()

    return result

def experience_years_by_categories(categories):

    conn = get_connection()
    cursor = conn.cursor()

    result = {}

    for category in categories:
        cursor.execute("""
            SELECT experience_years, salary_min, salary_max
            FROM jobs
            WHERE categories LIKE ?
        """, (f"%{category}%",))

        rows = cursor.fetchall()

        experience_data = {}

        for row in rows:
            years = row["experience_years"] if row["experience_years"] is not None else "نامشخص"

            if years not in experience_data:
                experience_data[years] = {"count": 0, "salaries": []}

            experience_data[years]["count"] += 1

            if row["salary_min"] is not None and row["salary_max"] is not None:
                job_average_salary = (row["salary_min"] + row["salary_max"]) / 2
                experience_data[years]["salaries"].append(job_average_salary)

        experience_summary = {}

        for years, data in experience_data.items():
            salaries = data["salaries"]
            experience_summary[years] = {
                "count": data["count"],
                "jobs_with_salary": len(salaries),
                "average_salary": round(sum(salaries) / len(salaries)) if salaries else 0
            }

        result[category] = experience_summary

    conn.close()

    return result

def count_backend_frontend_jobs():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            title,
            salary_min,
            salary_max
        FROM jobs
        WHERE categories LIKE ?
    """, (f"%{"توسعه نرم افزار و برنامه نویسی"}%",))


    rows = cursor.fetchall()


    backend_keywords = [
        "back-end",
        "backend",
        "back end",
        "بک اند",
        "بک‌اند",
        "api",
        "django",
        "python",
        "java",
        "spring",
        ".net",
        "php",
        "laravel",
        "node",
        "node.js"
    ]


    frontend_keywords = [
        "front-end",
        "frontend",
        "front end",
        "فرانت اند",
        "فرانت‌اند",
        "react",
        "vue",
        "angular",
        "javascript",
        "typescript",
        "next.js"
    ]


    backend_count = 0
    frontend_count = 0

    backend_salaries = []
    frontend_salaries = []


    for row in rows:

        title = (row["title"] or "").lower()


        # اگر حقوق ندارد، برای میانگین حقوق حساب نشود
        salary = None

        if row["salary_min"] is not None and row["salary_max"] is not None:
            salary = (row["salary_min"] + row["salary_max"]) / 2



        # Backend
        if any(keyword.lower() in title for keyword in backend_keywords):

            backend_count += 1

            if salary is not None:
                backend_salaries.append(salary)



        # Frontend
        if any(keyword.lower() in title for keyword in frontend_keywords):

            frontend_count += 1

            if salary is not None:
                frontend_salaries.append(salary)



    conn.close()


    backend_avg_salary = (
        sum(backend_salaries) / len(backend_salaries)
        if backend_salaries
        else 0
    )


    frontend_avg_salary = (
        sum(frontend_salaries) / len(frontend_salaries)
        if frontend_salaries
        else 0
    )


    return {
        "backend": {
            "count": backend_count,
            "salary_count": len(backend_salaries),
            "average_salary": round(backend_avg_salary)
        },

        "frontend": {
            "count": frontend_count,
            "salary_count": len(frontend_salaries),
            "average_salary": round(frontend_avg_salary)
        }
    }
    
    
