from flask import jsonify, make_response, json
from flask_restx import Namespace, Resource, reqparse
from .companies_service import CompaniesService

ns = Namespace("companies")


@ns.route("")
class CreateCompany(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = CompaniesService()

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

        result = self.service.create_company(args)
        if result["ok"]:
            return result["data"]
        else:
            return make_response(result["error"], result["http_status"])
