"""Helper functions for extracting API keys from tokens."""

from typing import Dict, Any, List


def extract_api_key(tokens: Dict[str, Any], key_names: List[str]) -> str:
    """
    Extract API key from tokens dictionary by trying multiple key names.
    
    Args:
        tokens: Dictionary containing auth tokens
        key_names: List of possible key names to try
        
    Returns:
        API key string or empty string if not found
    """
    if not tokens:
        return ""
    
    for key_name in key_names:
        if key_name in tokens:
            return str(tokens[key_name])
    
    return ""
