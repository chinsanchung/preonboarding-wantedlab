from flask_restx import Namespace, Resource, reqparse

ns = Namespace("companies")


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
            action="append",
        )
        parser.add_argument("x-wanted-language", type=str, location="headers")
        args = parser.parse_args()
        return args
