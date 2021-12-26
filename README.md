# 프리온보딩 백엔드 과정 8번째 과제: 원티드랩

[원티드랩](https://www.wantedlab.com/)에서 제공해주신 API 설계 과제입니다.

AWS Beanstalk 에 Docker 플랫폼으로 배포했으며, 주소는 [http://preonboardingwantedlab-env.eba-rm42kqcd.ap-northeast-2.elasticbeanstalk.com](http://preonboardingwantedlab-env.eba-rm42kqcd.ap-northeast-2.elasticbeanstalk.com)입니다.

## 과제에 대한 안내

### 1. 필수 요구 사항

- 회사명의 일부만 들어가도 검색이 되어야 하는 회사명 자동 완성 기능을 구현합니다.
- 회사 이름으로 회사를 검색합니다.
- 새로운 회사를 추가합니다.

### 2. 개발 요구 사항

- [테스트 케이스](https://github.com/chinsanchung/preonboarding-wantedlab/blob/main/test_app.py)를 통과할 수 있어야 합니다.
- ORM 을 사용합니다. 데이터베이스는 RDB 를 사용합니다.
- 결과는 JSON 형식이어야 합니다.

---

## 데이터베이스 ERD

![wantedlab ERD](https://user-images.githubusercontent.com/33484830/146767647-9d92bef5-b48d-4bb4-9422-4ba24628e8a7.PNG)

---

## 개발 환경

- 언어: Python
- 데이터베이스: AWS RDS for MySQL
- 사용 도구: Flask, Flask-Migrate, Flask-SQLAlchemy, PyMySQL, flask-restx, python=dotenv, requests, Docker, AWS Beanstalk

---

## API 문서

포스트맨으로 작성한 [API 문서](https://documenter.getpostman.com/view/18317278/UVREjQ5v)에서 상세한 내용을 확인하실 수 있습니다.

---

## 실행 방법

**AWS RDS 로 데이터베이스를 설정했기에, 로컬 환경에서 테스트하기 위해선 관련 설정이 담긴 .env 파일이 필요합니다.**

1. `git clone`으로 프로젝트를 가져옵니다.
2. .env 파일을 생성하고 아래의 내용을 기입합니다.

```
RDS_HOST
RDS_PORT
RDS_DB_NAME
RDS_USERNAME
RDS_PASSWORD
```

3. 다음으로 실행 방법입니다. Docker 를 이용하여 별도의 패키지 설치가 없어도 실행이 가능합니다. 터미널에 `bash docker_run.sh`를 입력하여 이미지를 만들고, 컨테이너를 백그라운드에서 실행합니다. `localhost:8080` 주소에서 테스트하실 수 있습니다.

---

## 수행한 작업

### 회사 생성하기

POST `/companies` URI를 요청해 회사를 생성합니다. 요청으로 보낼 JSON 형식은 다음과 같습니다. 여기에 `x-wanted-language`를 헤더에 넣어야합니다. (ko, en, ja, tw 등 언어 태그를 값으로 입력합니다.)

```json
{
  "company_name": {
    "ko": "라인 프레쉬",
    "tw": "LINE FRESH",
    "en": "LINE FRESH"
  },
  "tags": [
    {
      "tag_name": {
        "ko": "태그_1",
        "tw": "tag_1",
        "en": "tag_1"
      }
    }
  ]
}
```

#### 1. 요청 값 확인하기

우선 companies_controller 에서 요청으로 들어온 값을 확인하고, companies_service 의 `create_company` 메소드로 전달합니다.

```python
from flask_restx import Namespace, Resource, reqparse

@ns.route("")
class CreateCompany(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "company_name",
            type=dict,
            required=True,
        )
        parser.add_argument(
            "tags",
            type=list,
            required=True,
            location="json",
        )
        parser.add_argument("x-wanted-language", type=str, location="headers")
        args = parser.parse_args()

        result = service.create_company(args)
        if result["ok"]:
            return result["data"]
        else:
            return make_response(result["error"], result["http_status"])
```

`flask_restx`의 `reqparse`를 이용하여 우선 요청으로 들어온 값을 검증합니다. 그리고 `parse_args()` 메소드를 이용해 딕셔너리로 변환하여 파이썬에서 사용할 수 있게 합니다.

서비스에서 결과를 확인하면 성공인지 실패인지를 구분하여 상황에 맞게 응답을 보냅니다.

#### 2. 서비스에서 회사를 생성하기

다음은 companies_service 입니다. 회사를 생성할 때 필요한 절차는 아래와 같습니다. 수행 과정에서 하나라도 실패하면 그동안 등록한 것을 취소하기 위해 트랜잭션을 사용했습니다.

1. 새로운 `Company`를 생성합니다. 회사 이름과 태그를 등록할 때 외래키로써 사용합니다.
2. 회사 이름 객체의 키의 언어 코드를 통해 `Language`를 데이터베이스에 등록 또는 조회하여 불러옵니다.
3. `Company`, `Language`, 회사 이름으로 `CompanyName`을 생성합니다.
4. 태그를 등록하기 전, 태그 객체의 키의 언어 코드를 통해 데이터베이스에 등록 또는 조회하여 불러옵니다.
5. `Company`, `Language`, 태그 이름으로 `CompanyTag`를 등록합니다.
6. 생성이 완료되면 `company_name`, `tags`를 가진 딕셔너리를 리턴합니다. 실패할 경우, 에러 메시지와 상태 코드를 리턴합니다.

전체적인 구조입니다. `languages_cache`, `names_cache`, `tags_cache`는 각각 생성한 언어, 회사 이름과 태그를 저장합니다. 특히 이름과 태그는 언어 태그를 키로 하여 마지막에 응답으로 보낼 때 활용합니다.

```python
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
            # 1. 회사 생성
            # 2. 언어, 회사 이름 생성
            # 3. 언어, 회사 태그 생성
        except Exception:
            session.rollback()
            return {"ok": False, "http_status": http_status, "error": error}
        finally:
            session.close()
```

우선 새로운 회사를 생성합니다. `session.add`로 회사를 세션에 추가하고, `session.flush`를 통해 트랜잭션에 보류 중인 상태로 전환합니다. `flush`를 통해 실제로 등록된 것처럼 id 값을 발급받지만, 커밋을 해야만 정상적으로 등록됩니다.

```python
new_company = Company(created_at=datetime.now())
session.add(new_company)
session.flush()
```

다음으로 , `find_or_create_language` 함수로 `Language`를 등록하고, `check_and_create_company_name` 함수로 이름을 중복 체크한 후 없을 경우에 `CompanyName`을 생성하고 그 값을 리턴합니다. 만약 이름이 중복될 경우, 에러를 띄워 트랜잭션을 종료하고 이미 존재한다는 문구를 응답으로 보냅니다.

```python
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
```

회사 태그를 등록합니다. 회사 이름에서 등록한 언어와 태그의 언어가 일치하지 않는 경우를 고려하기 위해, 이름을 등록할 때 사용한 언어를 모은 캐시 `languages_cache`에서 새로운 언어인지를 확인합니다. 그리고 언어를 새로 등록하거나 또는 기존의 언어를 가져와 태크를 등록합니다.

```python
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
```

마지막으로 헤더의 `x-wanted-language`의 언어 태그에 맞게 `names_cache`, `tags_cache` 캐시에서 값을 가져와 응답으로 보냅니다.

```python
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
```

### 특정 회사 조회하기

GET `/companies/:keyword` URI를 요청해 특정 이름을 가진 회사를 조회합니다. keyword에 회사 이름을, 헤더에 `x-wanted-language`(언어 태그)를 입력합니다.

#### 1. 요청 값 확인하기

companies_controller 에서 URI 파라미터, 헤더를 검증 및 확인하여 딕셔너리로 변환합니다. 그리고 서비스의 `get_company` 메소드로 전달합니다.

```python
@ns.route("/<string:keyword>")
class GetCompany(Resource):
    def get(self, keyword):
        parser = reqparse.RequestParser()
        parser.add_argument("x-wanted-language", type=str, location="headers")
        args = parser.parse_args()

        result = service.get_company(
            {"keyword": keyword, "x-wanted-language": args["x-wanted-language"]}
        )
        if result["ok"]:
            return result["data"]
        else:
        return make_response(result["error"], result["http_status"])
```

#### 2. 서비스에서 회사를 조회하기

companies_service 의 `get_company` 메소드에서 비즈니스 로직을 수행합니다.

1. 입력한 키워드의 이름을 가진 회사가 존재하는지 확인합니다. 회사가 존재하지 않으면 404 코드를 가진 메시지를 응답으로 보냅니다.

```python
keyword = args["keyword"]
target_company = CompanyName.query.filter_by(company_name=keyword).first()

if target_company is None:
    return {"ok": False, "http_status": 404, "error": "해당 회사가 존재하지 않습니다."}
```

2. `CompanyName`, `Language`를 조회하고, ORM 쿼리문으로 얻은 SQLAlchemy 형식의 데이터를 딕셔너리로 변환합니다. 만약 변환하지 않으면 딕셔너리의 방식으로 데이터를 불러올 떄 `000 object is not subscriptable`에러가 발생합니다. [How to convert SQLAlchemy row object to a Python dict?](https://stackoverflow.com/a/37350445)을 참고해서 작성했습니다.

```python
def convert_orm_to_dict(row):
    return {
        column.key: getattr(row, column.key)
        for column in inspect(row).mapper.column_attrs
    }
```

```python
target_company = convert_orm_to_dict(target_company)
target_language = convert_orm_to_dict(
    Language.query.filter_by(lang_tag=lang_tag).first()
)
```

3. `Company`에 `CompanyName`, `CompanyTag`, `Language`을 join하여 모든 데이터를 불러온 후, 회사 아이디, 회사 이름의 lang_id, 회사 태그의 lang_id 가 일치하는 값만 조회하는 필터링을 수행합니다. 마지막으로 회사의 이름, 태그의 이름을 컬럼으로 추가합니다.

```python
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
```

4. 지정한 형식에 맞게 데이터를 정리한 후 리턴합니다.

```python
result = dict()
result["company_name"] = company_detail[0][1]
result["tags"] = [value[2] for value in company_detail]
return {"ok": True, "data": result}
```

### 회사명 자동 완성

#### 1. 요청 값 확인하기

search_controller 에서 요청 값을 검증하고, 딕셔너리로 변환하여 서비스의 `search_company` 메소드에 전달합니다. 그 다음 서비스의 결과에 따라 클라이언트에 응답을 전달합니다.

```python
@ns.route("")
class SearchCompany(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("query", type=str, location="args")
        parser.add_argument("x-wanted-language", type=str, location="headers")
        args = parser.parse_args()

        result = service.search_company(args)
        if result["ok"]:
            return result["data"]
        else:
            return make_response(result["error"], result["http_status"])
```

#### 2. 서비스에서 키워드로 결과를 확인하기

search_service 의 `search_company` 메소드로 자동 완성을 수행합니다.

1. 요청하는 언어와 키워드를 필터링하여 회사 이름의 목록을 가져옵니다. 만약 `company_name_list` 리스트의 길이가 0이면 에러를 리턴하는 조건문을 넣었습니다.

```python
company_name_list = (
    CompanyName.query.join(Language)
    .filter(
        Language.lang_tag == args["x-wanted-language"],
        CompanyName.company_name.like("%{}%".format(args["query"])),
    )
    .all()
)
if len(company_name_list) == 0:
    return {"ok": False, "http_status": 404, "error": "회사가 존재하지 않습니다."}
```

2. SQLAlchemy 형식의 데이터를 딕셔너리로 변환하는 한편, 응답에서 지정한 형식에 맞게 데이터를 가공한 후 리턴합니다.

```python
for val in company_name_list:
    # 출처: https://stackoverflow.com/a/1960546
    company_name = str(getattr(val, val.__table__.columns[3].name))
    result.append({"company_name": company_name})

return {"ok": True, "data": result}
```

---

## 폴더 구조

```
.
├── Dockerfile
├── README.md
├── add_data_from_csv.py
├── app.py
├── config.py
├── database.py
├── docker_run.sh
├── migrations
│   ├── README
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       └── af06cc88f8f4_.py
├── requirements.txt
├── resources
│   ├── __init__.py
│   ├── companies
│   │   ├── companies_controller.py
│   │   └── companies_service.py
│   ├── main
│   │   └── main_controller.py
│   ├── models.py
│   └── search
│       ├── search_controller.py
│       └── search_service.py
├── test_app.py
├── venv
└── wanted_temp_data.csv
```
