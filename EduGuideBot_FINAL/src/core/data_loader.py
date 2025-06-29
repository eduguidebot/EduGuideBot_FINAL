import json
import logging

logger = logging.getLogger(__name__)

class UniversityDataManager:
    def __init__(self, data_path: str):
        self.universities = []
        self._id_map = {}
        self._load_data(data_path)
        if self.universities:
            self._build_id_map()

    def _load_data(self, data_path: str):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                self.universities = json.load(f)
        except FileNotFoundError:
            logger.error(f"Data file not found at {data_path}")
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {data_path}")

    def _build_id_map(self):
        self._id_map = {uni['id']: uni for uni in self.universities}

    def get_all_universities(self) -> list:
        return self.universities

    def get_university_by_id(self, uni_id: int) -> dict | None:
        return self._id_map.get(uni_id) 