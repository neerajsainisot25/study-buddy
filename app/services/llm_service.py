"""LLM Service for handling API calls to OpenRouter"""
import requests
import json
import re
from flask import current_app, Response, stream_with_context
from app.config import Config

class LLMService:
    """Service for interacting with LLM API"""
    
    @staticmethod
    def call_llm(messages, model=None):
        """
        Make a call to the LLM API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (defaults to config model)
        
        Returns:
            str: Response content from LLM
        """
        model = model or Config.MODEL
        
        try:
            response = requests.post(
                Config.API_URL,
                headers={
                    "Authorization": f"Bearer {Config.API_KEY}",
                    "HTTP-Referer": Config.APP_URL,
                    "X-Title": Config.APP_NAME,
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            raise Exception(f"LLM API error: {str(e)}")
    
    @staticmethod
    def stream_llm(messages, model=None):
        """
        Stream LLM response using Server-Sent Events (SSE)
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (defaults to config model)
        
        Yields:
            str: Chunks of response content
        """
        model = model or Config.MODEL
        
        try:
            response = requests.post(
                Config.API_URL,
                headers={
                    "Authorization": f"Bearer {Config.API_KEY}",
                    "HTTP-Referer": Config.APP_URL,
                    "X-Title": Config.APP_NAME,
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True
                },
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    # OpenRouter uses 'data: ' prefix for SSE
                    if line_str.startswith('data: '):
                        data_str = line_str[6:].strip()  # Remove 'data: ' prefix
                        if data_str == '[DONE]':
                            break
                        if not data_str:
                            continue
                        try:
                            data = json.loads(data_str)
                            # OpenRouter format: choices[0].delta.content
                            choices = data.get('choices', [])
                            if choices:
                                delta = choices[0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError as e:
                            # Skip invalid JSON lines
                            continue
        except requests.exceptions.RequestException as e:
            # Return error as a chunk (will be handled by caller)
            yield f"Error: {str(e)}"
    
    @staticmethod
    def extract_json(content, json_type='array'):
        """
        Extract JSON from LLM response
        
        Args:
            content: Raw content from LLM
            json_type: 'array' or 'object'
        
        Returns:
            Parsed JSON object
        """
        pattern = r'\[.*\]' if json_type == 'array' else r'\{.*\}'
        json_match = re.search(pattern, content, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try parsing entire content
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON: {str(e)}")

