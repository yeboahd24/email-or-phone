from django.http import HttpResponseBadRequest
from django.core.exceptions import ValidationError
from rest_framework import parsers
from .utils import *


class WordParser(parsers.BaseParser):

    media_type = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    def parse(self, stream, media_type=None, parser_context=None):
        if (
            media_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            return parse_word_document(stream)
        return HttpResponseBadRequest("Unsupported file type")


class PDFParser(parsers.BaseParser):

    media_type = "application/pdf"

    def parse(self, stream, media_type=None, parser_context=None):
        if media_type == "application/pdf":
            return parse_pdf(stream)
        return HttpResponseBadRequest("Unsupported file type")


class JSONParser(parsers.BaseParser):

    media_type = "application/json"

    def parse(self, stream, media_type=None, parser_context=None):
        if media_type == "application/json":
            return parse_json(stream)
        return HttpResponseBadRequest("Unsupported file type")


class CSVParser(parsers.BaseParser):

    media_type = "text/csv"

    def parse(self, stream, media_type=None, parser_context=None):
        if media_type == "text/csv":
            return parse_csv(stream)
        return HttpResponseBadRequest("Unsupported file type")


class ExcelParser(parsers.BaseParser):

    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def parse(self, stream, media_type=None, parser_context=None):
        if (
            media_type
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            return parse_excel(stream)
        return HttpResponseBadRequest("Unsupported file type")
