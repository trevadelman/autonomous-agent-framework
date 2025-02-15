import pytest
import os
from pathlib import Path
import json
from unittest.mock import patch, MagicMock
from cryptography.fernet import Fernet

from autonomous_agent_framework.core.credentials import CredentialManager

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory for testing."""
    config_dir = tmp_path / ".config" / "test_framework"
    config_dir.mkdir(parents=True)
    return config_dir

@pytest.fixture
def credential_manager(temp_config_dir, monkeypatch, mock_keyring):
    """Create a CredentialManager instance with a temporary config directory."""
    monkeypatch.setattr(Path, "home", lambda: temp_config_dir.parent.parent)
    # Mock the master password input
    with patch("getpass.getpass", return_value="test_master_password"):
        manager = CredentialManager(app_name="test_framework")
        # Verify the mock was used
        mock_keyring["set"].assert_called_once()
        return manager

@pytest.fixture
def mock_keyring():
    """Mock keyring for testing."""
    with patch("keyring.get_password") as mock_get, \
         patch("keyring.set_password") as mock_set:
        # Generate a test key
        key = Fernet.generate_key()
        mock_get.return_value = key.decode()
        yield {"get": mock_get, "set": mock_set}

class TestCredentialManager:
    @pytest.mark.asyncio
    async def test_store_and_retrieve_credentials(self, credential_manager, mock_keyring):
        """Test storing and retrieving credentials."""
        test_creds = {
            "api_key": "test_key",
            "secret": "test_secret"
        }
        
        # Mock user input for confirmation
        with patch("builtins.input", return_value="y"):
            stored = await credential_manager.store_credentials(
                "test_tool",
                test_creds
            )
        
        assert stored is True
        
        # Retrieve and verify credentials
        retrieved = await credential_manager.get_credentials("test_tool")
        assert retrieved == test_creds
        
        # Test with required keys
        retrieved = await credential_manager.get_credentials(
            "test_tool",
            required_keys=["api_key"]
        )
        assert retrieved == test_creds
        
        # Test with missing required key
        retrieved = await credential_manager.get_credentials(
            "test_tool",
            required_keys=["missing_key"]
        )
        assert retrieved == {}

    @pytest.mark.asyncio
    async def test_clear_credentials(self, credential_manager, mock_keyring):
        """Test clearing stored credentials."""
        test_creds = {"api_key": "test_key"}
        
        # Store credentials
        with patch("builtins.input", return_value="y"):
            await credential_manager.store_credentials("test_tool", test_creds)
        
        # Clear credentials
        cleared = await credential_manager.clear_credentials("test_tool")
        assert cleared is True
        
        # Verify credentials are cleared
        retrieved = await credential_manager.get_credentials("test_tool")
        assert retrieved == {}
        
        # Test clearing non-existent credentials
        cleared = await credential_manager.clear_credentials("nonexistent_tool")
        assert cleared is False

    @pytest.mark.asyncio
    async def test_request_credentials(self, credential_manager, mock_keyring):
        """Test requesting credentials from user."""
        required_creds = ["api_key", "secret"]
        descriptions = {
            "api_key": "Enter your API key",
            "secret": "Enter your secret"
        }
        
        # Mock getpass for credential input
        with patch("getpass.getpass") as mock_getpass, \
             patch("builtins.input", return_value="n"):  # Don't store credentials
            mock_getpass.side_effect = ["test_key", "test_secret"]
            
            creds = await credential_manager.request_credentials(
                "test_tool",
                required_creds,
                descriptions
            )
        
        assert creds == {
            "api_key": "test_key",
            "secret": "test_secret"
        }
        
        # Verify credentials weren't stored (user input was 'n')
        retrieved = await credential_manager.get_credentials("test_tool")
        assert retrieved == {}

    def test_initialization(self, credential_manager, temp_config_dir):
        """Test credential manager initialization."""
        # Verify directories were created
        assert temp_config_dir.exists()
        assert (temp_config_dir / "credentials").exists()
        
        # Verify salt file was created
        assert (temp_config_dir / "salt").exists()
        
        # Verify Fernet was initialized
        assert credential_manager._fernet is not None

    @pytest.mark.asyncio
    async def test_encryption(self, credential_manager, mock_keyring):
        """Test that credentials are actually encrypted."""
        test_creds = {"api_key": "sensitive_data"}
        
        # Store credentials
        with patch("builtins.input", return_value="y"):
            await credential_manager.store_credentials("test_tool", test_creds)
        
        # Read the raw encrypted file
        cred_file = credential_manager._credentials_path / "test_tool.enc"
        encrypted_data = cred_file.read_bytes()
        
        # Verify the data is encrypted (not plain text)
        assert b"sensitive_data" not in encrypted_data
        
        # But can be decrypted correctly
        retrieved = await credential_manager.get_credentials("test_tool")
        assert retrieved == test_creds
