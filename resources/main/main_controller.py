from flask_restx import Namespace, Resource

ns = Namespace("main")


@ns.route("")
class GetMainPage(Resource):
    def get(self):
        return "preonboarding-wantedlab 프로젝트입니다."
