from database.connection import get_connection



def category_converter(categories):
    conn = get_connection()
    cursor = conn.cursor()

    result = []

    for category in categories:
        cursor.execute("""
            SELECT url_title
            FROM categories
            WHERE title_fa LIKE ?
        """, (f"%{category}%",))

        row = cursor.fetchone()

        if row:
            result.append(row[0])

    conn.close()
    return result