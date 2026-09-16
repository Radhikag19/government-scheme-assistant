import json
from pathlib import Path


METADATA_PATH = Path("data/scheme_metadata.json")


class SchemeRepository:

    def __init__(self):
        with open(
            METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        self.schemes = data["schemes"]

    def get_all_schemes(self):
        return self.schemes

    def get_scheme(self, scheme_id: str):
        requested_id = scheme_id.lower().strip()

        for scheme in self.schemes:

            stored_id = scheme.get(
                "scheme_id",
                ""
            )

            if stored_id.lower() == requested_id:
                return scheme

        return None

