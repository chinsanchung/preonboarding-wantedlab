from __future__ import print_function
from datetime import datetime
from sqlalchemy import create_engine, orm

from .. import db
from ..models import Company, Language, CompanyName, CompanyTag
import config

# 트랜잭션을 하기 전에 미리 생성합니다.
def create_company():
    new_company = Company(created_at=datetime.now())
    db.session.add(new_company)
    db.session.commit()
    return new_company


# 트랜젝션을 실패할 경우 삭제합니다.
def delete_company(company):
    db.session.delete(company)
    db.session.commit()
    return


def find_or_create_language(keyword, session):
    exist_lang = Language.query.filter_by(lang_tag=keyword).first()
    if exist_lang is None:
        new_language = Language(lang_tag=keyword)
        session.add(new_language)
        return new_language
    else:
        return exist_lang


def check_and_create_company_name(keyword, company_id, lang_id, session):
    exist_name = CompanyName.query.filter_by(company_name=keyword).first()
    if exist_name is None:
        new_name = CompanyName(
            company_id=company_id,
            lang_id=lang_id,
            company_name=keyword,
        )
        session.add(new_name)
        return True
    else:
        return False


class CompaniesService:
    def create_company(self, args):
        http_status = 200
        error = ""
        language_dict = dict()
        name_dict = dict()
        tags_dict = dict()

        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        session = orm.Session(engine)

        new_company = create_company()
        try:
            # 회사 이름 등록하기.
            for key, val in args.company_name.items():
                # 회사 이름: 이미 존재하는 회사 이름이면 에러를 리턴하고, 아니면 생성합니다.
                # 언어: 등록하지 않은 언어일 경우 생성합니다.
                language = find_or_create_language(key, session)
                language_dict[key] = language
                # 회사 이름: 동일한 이름의 회사가 존재하면 에러를, 아니면 이름을 데이터로 저장합니다.
                exist_name = CompanyName.query.filter_by(company_name=val)
                is_succeed_to_create_name = check_and_create_company_name(
                    keyword=val,
                    company_id=new_company.id,
                    lang_id=language.id,
                    session=session,
                )
                if is_succeed_to_create_name is False:
                    http_status = 400
                    error = "이미 존재하는 이름입니다."
                    raise Exception()
                name_dict[key] = val

            # 4. 태그: 회사를 이용해서 태그를 등록합니다.
            session.commit()
            return {"ok": True, "http_status": 200, "data": "s"}
        except Exception as err:
            print("EXCEPTION", err)
            session.rollback()
            delete_company(new_company)
            return {"ok": False, "http_status": http_status, "error": error}
        finally:
            session.close()
