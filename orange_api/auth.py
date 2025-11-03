"""
OAuth token management module for Orange API
Handles token fetching, caching, and automatic refresh
"""
import os
import time
from typing import Optional
from dotenv import load_dotenv
import httpx

load_dotenv()


class TokenManager:    
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.oauth_server_url = os.getenv("OAUTH_SERVER_URL")
        
        # Token storage
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        
        # Validate credentials
        if not all([self.client_id, self.client_secret, self.oauth_server_url]):
            raise ValueError(
                "Missing required environment variables: CLIENT_ID, CLIENT_SECRET, OAUTH_SERVER_URL"
            )
    
    async def get_token(self) -> str:
        # Return cached token if still valid (with 60s buffer)
        if self._access_token and time.time() < (self._token_expires_at - 60):
            return self._access_token
        
        # Fetch new token
        await self._fetch_token()
        return self._access_token
    
    async def _fetch_token(self) -> None:
        """Fetch a new access token from the OAuth server"""
        url = f"{self.oauth_server_url}/openidconnect/playground/v1.0/token"
        
        # Prepare form data (x-www-form-urlencoded)
        data = {
            "grant_type": "client_credentials"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    data=data,
                    auth=(self.client_id, self.client_secret),  # Basic auth
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                
                # Parse response
                token_data = response.json()
                self._access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires_at = time.time() + expires_in
                
                print(f"✓ Token fetched successfully. Expires in {expires_in}s")
                
        except httpx.HTTPStatusError as e:
            print(f"✗ Token request failed with status {e.response.status_code}")
            print(f"Response: {e.response.text}")
            raise
        except Exception as e:
            print(f"✗ Token request failed: {str(e)}")
            raise
    
    def clear_token(self) -> None:
        """Clear cached token (useful for testing or forcing refresh)"""
        self._access_token = None
        self._token_expires_at = 0


# Global token manager instance
token_manager = TokenManager()


async def get_access_token() -> str:
    return await token_manager.get_token()
