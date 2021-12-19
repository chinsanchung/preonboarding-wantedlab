import csv, requests, json

# 출처: https://medium.com/@hannah15198/convert-csv-to-json-with-python-b8899c722f6d
csv_path = "wanted_temp_data.csv"

company_list = list()


def get_tag_list(tag_ko, tag_en, tag_ja):
    tag_ko_list = tag_ko.split("|")
    tag_en_list = tag_en.split("|")
    tag_ja_list = tag_ja.split("|")
    result = list()
    for i in range(len(tag_ko_list)):
        tag_name = dict()
        tag_name["ko"] = tag_ko_list[i]
        tag_name["en"] = tag_en_list[i]
        tag_name["ja"] = tag_ja_list[i]
        result.append({"tag_name": tag_name})
    return result


def create_company(data):
    try:
        # 출처: https://docs.python-requests.org/en/latest/user/quickstart/
        r = requests.post(
            "http://127.0.0.1:5000/companies",
            data=json.dumps(data),
            headers={"x-wanted-language": "ko", "Content-Type": "application/json"},
        )
        return
    except Exception as err:
        print(err)
        return


with open(csv_path) as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        row_dict = {"company_name": dict(), "tags": list()}
        if row["company_ko"] != "":
            row_dict["company_name"]["ko"] = row["company_ko"]
        if row["company_en"] != "":
            row_dict["company_name"]["en"] = row["company_en"]
        if row["company_ja"] != "":
            row_dict["company_name"]["ja"] = row["company_ko"]
        row_dict["tags"] = get_tag_list(row["tag_ko"], row["tag_en"], row["tag_ja"])
        create_company(row_dict)
