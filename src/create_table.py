import psycopg2
from typing import Any


def create_database(dbname, parameters):
    """Создает базу данных, если она не существует."""
    conn = psycopg2.connect(dbname="postgres", **parameters)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE {dbname}")
    cur.close()
    conn.close()

    conn = psycopg2.connect(dbname=dbname, **parameters)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE employers (
            employer_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            website VARCHAR(255)
        )
    """)

    cur.execute("""
        CREATE TABLE vacancies (
            vacancy_id SERIAL PRIMARY KEY,
            employer_id INT REFERENCES employers(employer_id),
            title VARCHAR(255) NOT NULL,
            salary_from INT,
            salary_to INT,
            currency VARCHAR(10),
            url VARCHAR(255) NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


def save_data_to_database(
    companies_data: list[dict[str, Any]], vacancies_data: list[dict], params: dict, database_name: str = "headhunter"
) -> None:
    """
    Сохранение данных о компаниях и вакансиях в базу данных.
    """

    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        for company in companies_data:
            cur.execute(
                """
                INSERT INTO companies (company_id, company_name, company_url)
                VALUES (%s, %s, %s)
                """,
                (company["company_id"], company["company_name"], company["company_url"]),
            )

        for vacancy in vacancies_data:
            cur.execute(
                """
                INSERT INTO vacancies (vacancy_id, company_id, vacancy_name, salary, vacancy_url, description)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    vacancy["vacancy_id"],
                    vacancy["company_id"],
                    vacancy["name"],
                    vacancy["salary"],
                    vacancy["url"],
                    vacancy["description"],
                ),
            )

    conn.commit()
    conn.close()
