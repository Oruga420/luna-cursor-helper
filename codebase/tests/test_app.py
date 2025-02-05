import pytest
import json
import os
from pathlib import Path
from app import app, read_file_content, write_to_file, parse_openai_response, construct_prompt

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for file operations"""
    return tmp_path

def test_read_file_content_success(temp_dir):
    """Test successful file reading"""
    test_file = temp_dir / "test.txt"
    test_content = "Test content"
    test_file.write_text(test_content)
    
    result = read_file_content(str(test_file))
    assert result == test_content

def test_read_file_content_not_found():
    """Test reading non-existent file"""
    result = read_file_content("nonexistent.txt")
    assert result.startswith("ERROR: File not found")

def test_read_file_content_permission_error(temp_dir):
    """Test reading file with no permissions"""
    test_file = temp_dir / "noperm.txt"
    test_file.write_text("Test")
    test_file.chmod(0o000)
    
    result = read_file_content(str(test_file))
    assert result.startswith("ERROR: Permission denied")
    
    # Cleanup
    test_file.chmod(0o666)

def test_write_to_file_success(temp_dir):
    """Test successful file writing"""
    test_file = temp_dir / "write_test.txt"
    content = "Test write content"
    
    result = write_to_file(content, str(test_file))
    assert result is True
    assert test_file.read_text() == content

def test_write_to_file_permission_error(temp_dir):
    """Test writing to directory with no permissions"""
    no_perm_dir = temp_dir / "noperm"
    no_perm_dir.mkdir()
    no_perm_dir.chmod(0o444)
    
    result = write_to_file("test", str(no_perm_dir / "test.txt"))
    assert result is False
    
    # Cleanup
    no_perm_dir.chmod(0o777)

def test_parse_openai_response_success():
    """Test successful response parsing"""
    test_response = """###Solution: Test solution
###Prompt: Test prompt
###Currentbug: Test bug"""
    
    result = parse_openai_response(test_response)
    assert result['solution'] == "Test solution"
    assert result['prompt'] == "Test prompt"
    assert result['currentbug'] == "Test bug"

def test_parse_openai_response_missing_sections():
    """Test parsing response with missing sections"""
    test_response = """###Solution: Test solution
###Prompt: Test prompt"""
    
    result = parse_openai_response(test_response)
    assert result['solution'] == "Test solution"
    assert result['prompt'] == "Test prompt"
    assert result['currentbug'] == ""

def test_parse_openai_response_invalid():
    """Test parsing invalid response"""
    result = parse_openai_response("Invalid response")
    assert all(value == "" for value in result.values())

def test_construct_prompt_success():
    """Test successful prompt construction"""
    request_text = "Test request"
    file_paths = []
    current_problem = "Test problem"
    
    result = construct_prompt(request_text, file_paths, current_problem)
    assert "here is what Im doing" in result
    assert request_text in result
    assert current_problem in result

def test_construct_prompt_with_files(temp_dir):
    """Test prompt construction with file content"""
    test_file = temp_dir / "test.txt"
    test_file.write_text("File content")
    
    result = construct_prompt(
        "Test request",
        [str(test_file)],
        "Test problem"
    )
    assert "File content" in result

def test_process_request_missing_fields(client):
    """Test the /api/process endpoint with missing fields"""
    response = client.post('/api/process', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'missing' in data

def test_process_request_valid_data(client, monkeypatch, temp_dir):
    """Test the /api/process endpoint with valid data"""
    # Create test files
    solution_file = temp_dir / "solution.txt"
    bug_file = temp_dir / "bug.txt"
    
    # Mock OpenAI API response
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self.text = "Success"
        
        def json(self):
            return {
                'choices': [{
                    'message': {
                        'content': '''###Solution: Test solution
###Prompt: Test prompt
###Currentbug: Test bug'''
                    }
                }]
            }
    
    def mock_post(*args, **kwargs):
        return MockResponse()
    
    # Apply mock
    import requests
    monkeypatch.setattr(requests, "post", mock_post)
    
    # Test data
    test_data = {
        'request': 'Test request',
        'filePaths': [],
        'currentProblem': 'Test problem',
        'bugFilePath': str(bug_file),
        'solutionFilePath': str(solution_file)
    }
    
    response = client.post('/api/process', json=test_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'requestId' in data
    assert data['prompt'] == "Test prompt"
    assert data['solution'] == "Test solution"
    assert data['currentbug'] == "Test bug"
    assert data['writeStatus']['solution'] is True
    assert data['writeStatus']['currentbug'] is True

def test_process_request_file_write_failure(client, monkeypatch, temp_dir):
    """Test the /api/process endpoint with file write failure"""
    # Create directory with no write permissions
    no_perm_dir = temp_dir / "noperm"
    no_perm_dir.mkdir()
    no_perm_dir.chmod(0o444)
    
    # Mock OpenAI API response
    class MockResponse:
        def __init__(self):
            self.status_code = 200
            self.text = "Success"
        
        def json(self):
            return {
                'choices': [{
                    'message': {
                        'content': '''###Solution: Test solution
###Prompt: Test prompt
###Currentbug: Test bug'''
                    }
                }]
            }
    
    def mock_post(*args, **kwargs):
        return MockResponse()
    
    # Apply mock
    import requests
    monkeypatch.setattr(requests, "post", mock_post)
    
    # Test data
    test_data = {
        'request': 'Test request',
        'filePaths': [],
        'currentProblem': 'Test problem',
        'bugFilePath': str(no_perm_dir / "bug.txt"),
        'solutionFilePath': str(no_perm_dir / "solution.txt")
    }
    
    response = client.post('/api/process', json=test_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert data['writeStatus']['solution'] is False
    assert data['writeStatus']['currentbug'] is False
    
    # Cleanup
    no_perm_dir.chmod(0o777) 