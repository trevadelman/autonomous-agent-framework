import os
from typing import Dict, List, Optional
from pathlib import Path
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass
import keyring

class CredentialManager:
    """Secure management of tool credentials."""

    def __init__(self, app_name: str = "autonomous_agent_framework"):
        self.app_name = app_name
        self._fernet: Optional[Fernet] = None
        self._credentials_path = Path.home() / ".config" / app_name / "credentials"
        self._initialize_storage()

    def _initialize_storage(self) -> None:
        """Initialize the secure storage directory."""
        self._credentials_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption key if not exists
        key_path = self._credentials_path.parent / "key"
        if not key_path.exists():
            salt = os.urandom(16)
            # Get master password from user
            master_password = self._get_master_password()
            
            # Generate key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
            
            # Save salt
            with open(key_path.parent / "salt", "wb") as f:
                f.write(salt)
            
            # Store key securely using system keyring
            keyring.set_password(self.app_name, "encryption_key", key.decode())
        
        # Initialize Fernet with stored key
        stored_key = keyring.get_password(self.app_name, "encryption_key")
        if stored_key:
            self._fernet = Fernet(stored_key.encode())

    def _get_master_password(self) -> str:
        """Securely get master password from user."""
        print("\nInitializing secure credential storage.")
        print("Please set a master password for encrypting tool credentials.")
        print("This password will be required when managing credentials.\n")
        
        while True:
            password = getpass.getpass("Enter master password: ")
            confirm = getpass.getpass("Confirm master password: ")
            
            if password == confirm:
                return password
            print("\nPasswords do not match. Please try again.\n")

    async def store_credentials(
        self,
        tool_name: str,
        credentials: Dict[str, str],
        require_confirmation: bool = True
    ) -> bool:
        """Store credentials securely.
        
        Args:
            tool_name: Name of the tool these credentials are for
            credentials: Dictionary of credential key-value pairs
            require_confirmation: Whether to require user confirmation
            
        Returns:
            bool: True if credentials were stored successfully
        """
        if require_confirmation:
            print(f"\nStoring credentials for: {tool_name}")
            print("Credential keys:", ", ".join(credentials.keys()))
            confirm = input("Proceed? (y/n): ").lower()
            if confirm != "y":
                return False

        if not self._fernet:
            raise RuntimeError("Encryption not initialized")

        # Encrypt credentials
        encrypted_data = self._fernet.encrypt(
            json.dumps(credentials).encode()
        )

        # Store encrypted data
        tool_file = self._credentials_path / f"{tool_name}.enc"
        tool_file.parent.mkdir(parents=True, exist_ok=True)
        tool_file.write_bytes(encrypted_data)
        
        return True

    async def get_credentials(
        self,
        tool_name: str,
        required_keys: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Retrieve stored credentials.
        
        Args:
            tool_name: Name of the tool to get credentials for
            required_keys: Optional list of required credential keys
            
        Returns:
            Dictionary of credential key-value pairs
        """
        if not self._fernet:
            raise RuntimeError("Encryption not initialized")

        tool_file = self._credentials_path / f"{tool_name}.enc"
        
        if not tool_file.exists():
            return {}

        # Decrypt stored credentials
        encrypted_data = tool_file.read_bytes()
        decrypted_data = self._fernet.decrypt(encrypted_data)
        credentials = json.loads(decrypted_data)

        # Verify all required keys are present
        if required_keys:
            missing_keys = [key for key in required_keys if key not in credentials]
            if missing_keys:
                return {}

        return credentials

    async def request_credentials(
        self,
        tool_name: str,
        required_credentials: List[str],
        descriptions: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Request credentials from user.
        
        Args:
            tool_name: Name of the tool requiring credentials
            required_credentials: List of required credential keys
            descriptions: Optional descriptions for each credential
            
        Returns:
            Dictionary of credential key-value pairs
        """
        print(f"\nCredentials needed for: {tool_name}")
        
        credentials = {}
        for cred in required_credentials:
            desc = descriptions.get(cred, "") if descriptions else ""
            if desc:
                print(f"\n{desc}")
            credentials[cred] = getpass.getpass(f"Enter {cred}: ")

        # Store credentials if user agrees
        print("\nWould you like to store these credentials securely?")
        print("They will be encrypted with your master password.")
        if input("Store credentials? (y/n): ").lower() == "y":
            await self.store_credentials(tool_name, credentials)

        return credentials

    async def clear_credentials(self, tool_name: str) -> bool:
        """Clear stored credentials for a tool.
        
        Args:
            tool_name: Name of the tool to clear credentials for
            
        Returns:
            bool: True if credentials were cleared successfully
        """
        tool_file = self._credentials_path / f"{tool_name}.enc"
        
        if tool_file.exists():
            tool_file.unlink()
            return True
            
        return False
