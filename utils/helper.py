import json
import logging
from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, ValidationError
from config import settings


def parse_datetime(datetime_str: str, format: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> datetime:
    """
    Parse a datetime string into a datetime object.
    """
    return datetime.strptime(datetime_str, format)


def format_datetime(datetime_obj: datetime, format: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> str:
    """
    Format a datetime object into a string.
    """
    return datetime_obj.strftime(format)


def to_camel_case(snake_str: str) -> str:
    """
    Convert a snake_case string to camelCase.
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def to_snake_case(camel_str: str) -> str:
    """
    Convert a camelCase string to snake_case.
    """
    return ''.join(['_' + c.lower() if c.isupper() else c for c in camel_str]).lstrip('_')


def paginate(items: List[Any], limit: int, offset: int) -> List[Any]:
    """
    Paginate a list of items based on the provided limit and offset.
    """
    return items[offset:offset + limit]


def serialize_model(model: BaseModel) -> Dict[str, Any]:
    """
    Serialize a Pydantic model to a dictionary.
    """
    return model.dict(by_alias=True)


def deserialize_model(model_class: BaseModel, data: Dict[str, Any]) -> BaseModel:
    """
    Deserialize a dictionary into a Pydantic model.
    """
    return model_class(**data)


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load a JSON file and return its contents as a dictionary.
    """
    with open(file_path, 'r') as file:
        return json.load(file)


def save_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """
    Save a dictionary as a JSON file.
    """
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def setup_logging(log_level: str = settings.LOG_LEVEL) -> None:
    """
    Set up logging configuration.
    """
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def validate_payload(payload: Dict[str, Any], model_class: BaseModel) -> BaseModel:
    """
    Validate a payload against a Pydantic model.
    """
    try:
        return model_class(**payload)
    except ValidationError as e:
        raise ValueError(f"Invalid payload: {e}")

def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of a specified size.
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """
    Flatten a nested list into a single list.
    """
    return [item for sublist in nested_list for item in sublist]


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries recursively.
    """
    merged = dict1.copy()
    for key, value in dict2.items():
        if isinstance(value, dict):
            merged[key] = merge_dicts(merged.get(key, {}), value)
        else:
            merged[key] = value
    return merged