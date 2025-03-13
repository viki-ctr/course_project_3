import requests


class HeadHunterAPI:
    """
    Класс для работы с API HeadHunter.
    """

    def __init__(self) -> None:
        """
        Инициализация экземпляра класса, атрибутов для подключения к API HH.
        """
        self.__url = "https://api.hh.ru/"
        self.__headers = {"User-Agent": "HH-User-Agent"}
        self.__params = {}

    def __get_response(self) -> bool:
        """
        Метод получения ответа от HH, проверка статуса ответа.
        """
        self.__params["page"] = 0
        response = requests.get("https://api.hh.ru/", headers=self.__headers, params=self.__params)
        self.__status_code = response.status_code
        if self.__status_code == 200:
            # print("Ответ от HH.ru успешно получен.")
            return True
        else:
            print(f"Ошибка подключения к HH.ru. Status code: {self.__status_code}")
            return False

    def get_vacancies(self, company_id: str, per_page: int = 100) -> list[dict]:
        """
        Метод загружает вакансии по id компании.
        """
        vacancies = []

        if self.__get_response():
            self.__url = "https://api.hh.ru/vacancies"
            self.__params["employer_id"] = company_id
            self.__params["per_page"] = per_page
            response = requests.get(self.__url, headers=self.__headers, params=self.__params)
            vacancies.extend(response.json()["items"])
        return vacancies

    def get_companies(self, company_names: list[str]) -> list[dict]:
        """
        Метод получения информации о компаниях по ключевым словам.
        Возвращает список id компаний.
        """
        companies = []

        if self.__get_response():
            self.__url = "https://api.hh.ru/employers"
            self.__params["per_page"] = 100
            self.__params["sort_by"] = "by_vacancies_open"
        for company in company_names:
            self.__params["text"] = company
            response = requests.get(self.__url, headers=self.__headers, params=self.__params)
            if response.json()["found"] >= 1:
                id_ = response.json()["items"][0]["id"]
                name = response.json()["items"][0]["name"]
                url = response.json()["items"][0]["alternate_url"]
                companies.append({"company_id": id_, "company_name": name, "company_url": url})
            else:
                continue
        return companies

    @staticmethod
    def get_price(currency: str) -> float:
        """
        Метод получает курс валюты.
        """
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        courses = response.json()
        if courses["Valute"].get(currency):
            price = courses["Valute"][currency].get("Value")
        else:
            price = 1
        return price

    @classmethod
    def transfom_data(cls, vacancy: dict) -> dict:
        """
        Метод преобразовывает вакансии в формат, с которым удобно работать.
        """
        salary = 0
        if type(vacancy.get("salary")) == dict:
            from_ = vacancy["salary"].get("from", 0)
            to = vacancy["salary"].get("to", 0)
            if (from_ is not None and from_ != 0) and (to is not None and to != 0):
                salary = (from_ + to) // 2
            elif from_ is not None and from_ != 0:
                salary = from_
            elif to is not None and to != 0:
                salary = to

            if salary != 0 and vacancy["salary"]["currency"] != "RUR":
                salary = salary * cls.get_price(vacancy["salary"]["currency"])

        transformed_vacancy = {
            "vacancy_id": vacancy["id"],
            "company_id": vacancy["employer"]["id"],
            "name": vacancy["name"],
            "salary": salary,
            "url": vacancy.get("alternate_url", ""),
            "description": f"Обязанности: {vacancy['snippet'].get('responsibility', '')} "
            f"Требования: {vacancy['snippet'].get('requirement', '')}",
        }
        return transformed_vacancy


# if __name__ == "__main__":
#     print(HeadHunterAPI().get_companies(["Хэдхантер", "СОГАЗ"]))
