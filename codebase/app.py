import os
import re
import json
import logging
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import requests
from config import get_config

# Load environment variables
load_dotenv()

# Get configuration
config = get_config()

# Configure logging with more detailed format
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='build')
CORS(app)

# Constants from configuration
OPENAI_API_KEY = config.OPENAI_API_KEY
ASSISTANT_ID = config.ASSISTANT_ID
API_URL = f"https://api.openai.com/v1/assistants/{ASSISTANT_ID}/chat"

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

def read_file_content(file_path):
    """
    Read content from a file with enhanced error handling and logging
    
    Args:
        file_path (str): Path to the file to read
        
    Returns:
        str: File content or error message
    """
    logger.info(f"Attempting to read file: {file_path}")
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            return f"ERROR: {error_msg}"
            
        if not file_path.is_file():
            error_msg = f"Path is not a file: {file_path}"
            logger.error(error_msg)
            return f"ERROR: {error_msg}"
            
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            logger.info(f"Successfully read file: {file_path}")
            return content
            
    except PermissionError as e:
        error_msg = f"Permission denied reading file {file_path}"
        logger.error(f"{error_msg}: {str(e)}")
        return f"ERROR: {error_msg}"
        
    except UnicodeDecodeError as e:
        error_msg = f"File encoding error for {file_path}"
        logger.error(f"{error_msg}: {str(e)}")
        return f"ERROR: {error_msg}"
        
    except Exception as e:
        error_msg = f"Error reading file {file_path}"
        logger.error(f"{error_msg}: {str(e)}")
        return f"ERROR: {error_msg}"

def write_to_file(content, file_path):
    """
    Write content to a file with enhanced error handling and logging
    
    Args:
        content (str): Content to write to file
        file_path (str): Path to write the file to
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Attempting to write to file: {file_path}")
    try:
        file_path = Path(file_path)
        
        # Create directory structure if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if directory is writable
        if not os.access(file_path.parent, os.W_OK):
            error_msg = f"Directory not writable: {file_path.parent}"
            logger.error(error_msg)
            return False
            
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
            logger.info(f"Successfully wrote to file: {file_path}")
            return True
            
    except PermissionError as e:
        logger.error(f"Permission denied writing to file {file_path}: {str(e)}")
        return False
        
    except OSError as e:
        logger.error(f"OS error writing to file {file_path}: {str(e)}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error writing to file {file_path}: {str(e)}")
        return False

def parse_openai_response(response_text):
    """
    Parse the OpenAI response with enhanced regex handling and validation
    
    Args:
        response_text (str): Raw response text from OpenAI
        
    Returns:
        dict: Parsed sections with validation status
    """
    logger.info("Parsing OpenAI response")
    try:
        sections = {
            'solution': re.search(r"###Solution:\s*(.*?)(?=###|$)", response_text, re.DOTALL),
            'prompt': re.search(r"###Prompt:\s*(.*?)(?=###|$)", response_text, re.DOTALL),
            'currentbug': re.search(r"###Currentbug:\s*(.*?)(?=###|$)", response_text, re.DOTALL)
        }
        
        parsed = {
            key: match.group(1).strip() if match else ""
            for key, match in sections.items()
        }
        
        # Validate parsed content
        validation = {
            key: bool(content.strip())
            for key, content in parsed.items()
        }
        
        if not all(validation.values()):
            missing = [k for k, v in validation.items() if not v]
            logger.warning(f"Missing or empty sections in response: {missing}")
            
        logger.info("Successfully parsed OpenAI response")
        return parsed
        
    except Exception as e:
        logger.error(f"Error parsing OpenAI response: {str(e)}")
        return {
            'solution': "",
            'prompt': "",
            'currentbug': ""
        }

def construct_prompt(request_text, file_paths, current_problem):
    """
    Construct the prompt with enhanced validation and formatting
    
    Args:
        request_text (str): User's request
        file_paths (list): List of file paths to process
        current_problem (str): Description of current problem
        
    Returns:
        str: Constructed prompt
    """
    logger.info("Constructing prompt")
    try:
        prompt_parts = ["here is what Im doing"]
        
        # Add request text with validation
        if request_text.strip():
            prompt_parts.append(request_text)
        else:
            logger.warning("Empty request text in prompt construction")
            
        # Process file paths
        for idx, path in enumerate(file_paths, start=1):
            if path.strip():
                file_content = read_file_content(path)
                if not file_content.startswith("ERROR:"):
                    prompt_parts.append(f"file {idx}: {file_content}")
                else:
                    logger.warning(f"Skipping file {path} due to read error")
                    
        # Add current problem
        prompt_parts.extend([
            "This is what my current problem:",
            current_problem if current_problem.strip() else "No problem specified"
        ])
        
        final_prompt = "\n".join(prompt_parts)
        logger.info("Successfully constructed prompt")
        return final_prompt
        
    except Exception as e:
        logger.error(f"Error constructing prompt: {str(e)}")
        return ""

@app.route('/api/process', methods=['POST'])
def process_request():
    """
    Process incoming requests with enhanced error handling and response formatting
    """
    request_id = f"req_{os.urandom(4).hex()}"
    logger.info(f"Processing request {request_id}")
    
    try:
        # Validate request data
        data = request.get_json()
        required_fields = ['request', 'filePaths', 'currentProblem', 'bugFilePath', 'solutionFilePath']
        
        if not all(field in data for field in required_fields):
            missing = [f for f in required_fields if f not in data]
            logger.error(f"Request {request_id}: Missing required fields: {missing}")
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing
            }), 400
            
        # Construct and validate prompt
        prompt = construct_prompt(
            data['request'],
            data['filePaths'],
            data['currentProblem']
        )
        
        if not prompt:
            logger.error(f"Request {request_id}: Failed to construct prompt")
            return jsonify({
                'error': 'Failed to construct prompt'
            }), 500
            
        # Call OpenAI API
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }
        
        logger.info(f"Request {request_id}: Calling OpenAI API")
        response = requests.post(API_URL, json=payload, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Request {request_id}: OpenAI API error: {response.text}")
            return jsonify({
                'error': 'OpenAI API error',
                'details': response.text
            }), 500
            
        # Parse response
        response_data = response.json()
        parsed_sections = parse_openai_response(response_data['choices'][0]['message']['content'])
        
        # Write files and track success
        write_results = {
            'solution': write_to_file(parsed_sections['solution'], data['solutionFilePath']),
            'currentbug': write_to_file(parsed_sections['currentbug'], data['bugFilePath'])
        }
        
        if not all(write_results.values()):
            failed = [k for k, v in write_results.items() if not v]
            logger.warning(f"Request {request_id}: Failed to write some files: {failed}")
            
        # Return response
        response = {
            'success': True,
            'requestId': request_id,
            'prompt': parsed_sections['prompt'],
            'solution': parsed_sections['solution'],
            'currentbug': parsed_sections['currentbug'],
            'writeStatus': write_results
        }
        
        logger.info(f"Request {request_id}: Successfully processed")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Request {request_id}: Unexpected error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'requestId': request_id,
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    ) 