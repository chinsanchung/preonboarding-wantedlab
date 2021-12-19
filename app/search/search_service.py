from ..models import Language, CompanyName


class SearchService:
    @staticmethod
    def search_company(args):
        try:
            company_name_list = (
                CompanyName.query.join(Language)
                .filter(
                    Language.lang_tag == args["x-wanted-language"],
                    CompanyName.company_name.like("%{}%".format(args["query"])),
                )
                .all()
            )

            result = list()
            for val in company_name_list:
                # 출처: https://stackoverflow.com/a/1960546
                company_name = str(getattr(val, val.__table__.columns[3].name))
                result.append({"company_name": company_name})

            return {"ok": True, "data": result}
        except Exception:
            return {"ok": False, "http_status": 500, "error": "에러가 발생했습니다."}
