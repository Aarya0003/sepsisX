from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os
import uuid
import base64
from pathlib import Path

def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    Format datetime to ISO format string
    """
    if dt is None:
        return None
    return dt.isoformat()

def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO format datetime string to datetime object
    """
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        return None

def generate_unique_id() -> str:
    """
    Generate a unique ID
    """
    return str(uuid.uuid4())

def encode_image_to_base64(image_path: str) -> Optional[str]:
    """
    Encode an image file to base64 string
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            image_type = Path(image_path).suffix.lstrip('.').lower()
            if image_type == 'jpg':
                image_type = 'jpeg'
            return f"data:image/{image_type};base64,{encoded_string}"
    except Exception as e:
        return None

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely load JSON string
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}

def calculate_age(birth_date: Optional[datetime]) -> Optional[int]:
    """
    Calculate age from birth date
    """
    if not birth_date:
        return None
    today = datetime.now()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def is_valid_email(email: str) -> bool:
    """
    Simple email validation
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))