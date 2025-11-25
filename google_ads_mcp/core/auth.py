import os
from pathlib import Path
from typing import Optional
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

class GoogleAdsAuthenticator:
    SCOPES = ['https://www.googleapis.com/auth/adwords']
    
    def __init__(self, auth_type: str, credentials_path: str, token_path: Optional[str] = None):
        self.auth_type = auth_type.lower()
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path) if token_path else Path("token.json")
        
        if self.auth_type not in ['oauth', 'service_account']:
            raise ValueError("auth_type must be 'oauth' or 'service_account'")
        if not self.credentials_path.exists():
            raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
    
    def get_credentials(self):
        if self.auth_type == 'oauth':
            return self._get_oauth_credentials()
        return self._get_service_account_credentials()
    
    def _get_oauth_credentials(self):
        creds = None
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), self.SCOPES)
                creds = flow.run_local_server(port=0)
                self.token_path.write_text(creds.to_json())
        
        return creds
    
    def _get_service_account_credentials(self):
        return service_account.Credentials.from_service_account_file(
            str(self.credentials_path), scopes=self.SCOPES
        )
