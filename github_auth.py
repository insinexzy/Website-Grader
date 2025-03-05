import os
import json
import keyring
import subprocess
from pathlib import Path
from typing import Optional, Tuple

class GitHubAuth:
    def __init__(self):
        self.service_id = "website_grader_github"
        self.config_file = Path.home() / ".website_grader" / "github_config.json"
        self.username = None
        self.load_config()

    def load_config(self):
        """Load saved configuration if it exists"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                config = json.load(f)
                self.username = config.get('username')

    def save_config(self):
        """Save configuration to file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump({'username': self.username}, f)

    def get_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """Get stored credentials"""
        if not self.username:
            return None, None
        password = keyring.get_password(self.service_id, self.username)
        return self.username, password

    def set_credentials(self, username: str, password: str):
        """Store credentials securely"""
        self.username = username
        keyring.set_password(self.service_id, username, password)
        self.save_config()

    def configure_git(self):
        """Configure Git with stored credentials"""
        username, password = self.get_credentials()
        if username and password:
            # Set Git configuration
            subprocess.run(['git', 'config', '--global', 'user.name', username])
            subprocess.run(['git', 'config', '--global', 'user.email', f"{username}@users.noreply.github.com"])
            
            # Configure Git to use credential store
            subprocess.run(['git', 'config', '--global', 'credential.helper', 'store'])
            
            # Store credentials in Git credential store
            credential_input = f"url=https://github.com\nusername={username}\npassword={password}\n"
            subprocess.run(['git', 'credential', 'approve'], input=credential_input.encode(), check=True)
            
            return True
        return False

    def authenticate(self):
        """Authenticate with GitHub"""
        # Try to get existing credentials
        username, password = self.get_credentials()
        
        if not username or not password:
            # If no credentials exist, use the provided ones
            self.set_credentials("duaaryan10@gmail.com", "insinexzy")
            username, password = self.get_credentials()
        
        if username and password:
            return self.configure_git()
        
        return False

def setup_github_auth():
    """Setup GitHub authentication"""
    auth = GitHubAuth()
    if auth.authenticate():
        print("Successfully authenticated with GitHub")
        return True
    else:
        print("Failed to authenticate with GitHub")
        return False 