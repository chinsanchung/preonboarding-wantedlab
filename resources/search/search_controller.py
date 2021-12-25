from flask import make_response
from flask_restx import Namespace, Resource, reqparse
from .search_service import SearchService as service

ns = Namespace("search")


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
