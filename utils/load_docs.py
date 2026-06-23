def load_company_info():
    with open("data/company_info.txt", "r", encoding="utf-8") as file:
        return file.read()