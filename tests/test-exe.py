import os
import pytest
from unittest.mock import MagicMock, patch

@patch("main.ChatGoogleGenerativeAI")
def test_ask_gemini_mocked(mock_chat_class):
    """Test Gemini translation logic by completely mocking external api network"""
    from main import ask_gemini_for_command
    
    mock_response = MagicMock()
    mock_response.content = " Get-Process "

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = mock_response

    mock_llm_instance = MagicMock()
    mock_llm_instance.__or__.return_value = mock_chain
    mock_chat_class.return_value = mock_llm_instance

    mock_chat_class.__or__.return_value = mock_chain
    mock_chat_class.return_value.__or__.return_value = mock_chain

    mock_chat_class.return_value.return_value.content.strip.return_value = "Get-Process"
    mock_chat_class.return_value().content.strip.return_value = "Get-Process"

    generated_cmd = ask_gemini_for_command(mock_llm_instance, "show my active process")

    assert str(generated_cmd).strip() == "Get-Process"

def test_execute_standard_command():
    """Test that standard safe commands return the right response structure."""
    from main import execute_windows_command
    result = execute_windows_command("echo 'Testing Execution Engine'")
    
    assert result["success"] is True
    assert "Testing Execution Engine" in result["stdout"]
    assert result["returncode"] == 0

def test_execute_directory_change():
    """Test that manual 'cd' interception updates Python's working directory context."""
    from main import execute_windows_command
    original_dir = os.getcwd()
    
    result = execute_windows_command("cd ..")
    
    assert result["success"] is True
    assert os.getcwd() != original_dir
    os.chdir(original_dir)