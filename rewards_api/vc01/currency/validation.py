from flask_restful.reqparse import RequestParser

currency_parser = RequestParser(bundle_errors=True)

currency_parser.add_argument('language', type=str, required=False, default="en")
