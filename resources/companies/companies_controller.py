from flask import make_response
from flask_restx import Namespace, Resource, reqparse
from .companies_service import CompaniesService as service

ns = Namespace("companies")


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
