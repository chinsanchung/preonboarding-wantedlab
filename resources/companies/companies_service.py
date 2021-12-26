from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from ..models import Company, Language, CompanyName, CompanyTag
import config


def find_or_create_language(keyword, session):
    exist_lang = Language.query.filter_by(lang_tag=keyword).first()
    if exist_lang is None:
        new_language = Language(lang_tag=keyword)
        session.add(new_language)
        return new_language
    else:
        return exist_lang


def check_and_create_company_name(keyword, company, lang_id, session):
    exist_name = CompanyName.query.filter_by(
        company_name=keyword, lang_id=lang_id
    ).first()
    if exist_name is None:
        new_name = CompanyName(
            company=company,
            lang_id=lang_id,
            company_name=keyword,
        )
        session.add(new_name)
        return {"ok": True}
    else:
        return {"ok": False}


def create_company_tag(keyword, company, lang_id, session):
    new_tag = CompanyTag(tag_name=keyword, company=company, lang_id=lang_id)
    session.add(new_tag)
    return None


def convert_orm_to_dict(row):
    # 출처: https://stackoverflow.com/a/37350445
    return {
        column.key: getattr(row, column.key)
        for column in inspect(row).mapper.column_attrs
    }


class CompaniesService:
    @staticmethod
    def create_company(args):
        http_status = 500
        error = "생성 과정에서 에러가 발생했습니다."
        languages_cache = dict()
        names_cache = dict()
        tags_cache = list()

        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        session = Session(engine)

        try:
            new_company = Company(created_at=datetime.now())
            session.add(new_company)
            session.flush()

            for name_key, name_val in args.company_name.items():
                language = find_or_create_language(name_key, session)
                session.flush()
                languages_cache[name_key] = language
                is_succeed_to_create_name = check_and_create_company_name(
                    keyword=name_val,
                    company=new_company,
                    lang_id=language.id,
                    session=session,
                )
                if not is_succeed_to_create_name["ok"]:
                    http_status = 400
                    error = "이미 존재하는 이름입니다."
                    raise Exception()
                names_cache[name_key] = name_val

            for tag in args.tags:
                for tag_key, tag_val in tag["tag_name"].items():
                    if tag_key not in languages_cache:
                        language = find_or_create_language(tag_key, session)
                        session.flush()
                        languages_cache[tag_key] = language
                    create_company_tag(
                        keyword=tag_val,
                        company=new_company,
                        lang_id=languages_cache[tag_key].id,
                        session=session,
                    )
                    tags_cache.append({"lang_tag": tag_key, "tag_name": tag_val})

            requested_language = args["x-wanted-language"]
            result = {
                "company_name": names_cache[requested_language],
                "tags": [
                    tag["tag_name"]
                    for tag in tags_cache
                    if tag["lang_tag"] == requested_language
                ],
            }
            # commit
            session.commit()
            return {"ok": True, "http_status": 200, "data": result}
        except Exception:
            session.rollback()
            return {"ok": False, "http_status": http_status, "error": error}
        finally:
            session.close()

    @staticmethod
    def get_company(args):
        try:
            keyword = args["keyword"]
            lang_tag = args["x-wanted-language"]
            target_company = CompanyName.query.filter_by(company_name=keyword).first()

            if target_company is None:
                return {"ok": False, "http_status": 404, "error": "해당 회사가 존재하지 않습니다."}

            target_company = convert_orm_to_dict(target_company)
            target_language = convert_orm_to_dict(
                Language.query.filter_by(lang_tag=lang_tag).first()
            )

            company_detail = (
                Company.query.join(CompanyName)
                .join(CompanyTag)
                .join(Language)
                .filter(
                    Company.id == target_company["company_id"],
                    CompanyName.lang_id == target_language["id"],
                    CompanyTag.lang_id == target_language["id"],
                )
                .add_columns(CompanyName.company_name, CompanyTag.tag_name)
                .all()
            )

            result = dict()
            result["company_name"] = company_detail[0][1]
            result["tags"] = [value[2] for value in company_detail]
            return {"ok": True, "data": result}
        except Exception:
            return {"ok": False, "http_status": 500, "error": "에러가 발생했습니다."}
