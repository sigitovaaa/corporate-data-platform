import duckdb
from pathlib import Path

con = duckdb.connect()
con.execute("""
    CREATE VIEW companies AS
    SELECT *
    FROM read_csv_auto('data/raw/companies.csv')
""")
print("Данные подключены")

query = """
    SELECT
        city,
        COUNT(*) AS company_count,
        SUM(employees) AS total_employees,
        ROUND(AVG(employees), 2) AS avg_employees,
        MAX(employees) AS max_employees
    FROM companies
    GROUP BY city
    ORDER BY total_employees DESC
"""
result = con.execute(query).fetchdf()
print("\nИтоговый аналитический отчет:")
print(result.to_string(index=False))

output_dir = Path("analytics/reports")
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "city_analytics.csv"
result.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"\nОтчет сохранен: {output_file}")

# 1. Отрасль с наибольшим количеством организаций
query = """
    SELECT
        industry,
        COUNT(*) AS company_count
    FROM companies
    GROUP BY industry
    ORDER BY company_count DESC
    LIMIT 1
"""
result = con.execute(query).fetchdf()
print("\n1. Отрасль с наибольшим количеством организаций:")
print(result.to_string(index=False))

# 2. Город с наибольшим числом сотрудников
query = """
    SELECT
        city,
        SUM(employees) AS total_employees
    FROM companies
    GROUP BY city
    ORDER BY total_employees DESC
    LIMIT 1
"""
result = con.execute(query).fetchdf()
print("\n2. Город с наибольшим числом сотрудников:")
print(result.to_string(index=False))

# 3. Крупнейшая организация по численности персонала
query = """
    SELECT
        name,
        industry,
        city,
        employees
    FROM companies
    ORDER BY employees DESC
    LIMIT 1
"""
result = con.execute(query).fetchdf()
print("\n3. Крупнейшая организация по численности персонала:")
print(result.to_string(index=False))

# 4. Города с не менее чем двумя организациями
query = """
    SELECT
        city,
        COUNT(*) AS company_count
    FROM companies
    GROUP BY city
    HAVING COUNT(*) >= 2
    ORDER BY company_count DESC
"""
result = con.execute(query).fetchdf()
print("\n4. Города с не менее чем двумя организациями:")
print(result.to_string(index=False))

# 5. Отрасль с максимальной средней численностью сотрудников
query = """
    SELECT
        industry,
        ROUND(AVG(employees), 2) AS avg_employees
    FROM companies
    GROUP BY industry
    ORDER BY avg_employees DESC
    LIMIT 1
"""
result = con.execute(query).fetchdf()
print("\n5. Отрасль с максимальной средней численностью сотрудников:")
print(result.to_string(index=False))

con.close()