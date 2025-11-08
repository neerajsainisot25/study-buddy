"""Helper utility functions"""
from flask import jsonify
from typing import Any, Dict

def success_response(data: Any, message: str = None) -> Dict:
    """Create a success response"""
    response = {"success": True, "data": data}
    if message:
        response["message"] = message
    return response

def error_response(error: str, status_code: int = 400) -> tuple:
    """Create an error response"""
    return jsonify({"error": error}), status_code

def validate_required_fields(data: Dict, required_fields: list) -> tuple:
    """
    Validate that required fields are present
    
    Returns:
        (is_valid, error_message)
    """
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, None

