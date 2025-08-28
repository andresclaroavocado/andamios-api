import pytest
import asyncio
import httpx
import subprocess
import sys
import time
import os
from pathlib import Path
from contextlib import asynccontextmanager

# Test configuration
TEST_SERVER_HOST = "localhost"
TEST_SERVER_PORT = 8002  # Different from dev server
TEST_BASE_URL = f"http://{TEST_SERVER_HOST}:{TEST_SERVER_PORT}"

class TestServer:
    """Manages test server lifecycle"""
    
    def __init__(self):
        self.process = None
        
    async def start(self):
        """Start test server with test environment"""
        # Set test environment
        env = os.environ.copy()
        env["ENVIRONMENT"] = "test"
        
        # Start server
        project_root = Path(__file__).parent.parent
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "src.andamios_api.main:app",
            "--host", TEST_SERVER_HOST,
            "--port", str(TEST_SERVER_PORT),
            "--log-level", "error"  # Reduce noise in tests
        ]
        
        self.process = subprocess.Popen(
            cmd, 
            cwd=project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to be ready
        await self._wait_for_server()
        
    async def stop(self):
        """Stop test server"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
    
    async def _wait_for_server(self, timeout=30):
        """Wait for server to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{TEST_BASE_URL}/health", timeout=1.0)
                    if response.status_code == 200:
                        return
            except:
                pass
                
            await asyncio.sleep(0.1)
        
        raise RuntimeError(f"Test server failed to start within {timeout} seconds")

# Global test server instance
test_server = TestServer()

@pytest.fixture(scope="session", autouse=True)
async def setup_test_server():
    """Setup test server for entire test session"""
    await test_server.start()
    yield
    await test_server.stop()

@pytest.fixture
async def client():
    """HTTP client for API testing"""
    async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
        yield client

@pytest.fixture
async def auth_client():
    """Authenticated HTTP client for protected endpoints"""
    async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
        # Create test user
        test_user = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        await client.post("/api/v1/auth/register", json=test_user)
        
        # Login to get token
        login_data = {
            "email": "test@example.com", 
            "password": "testpassword123"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        token_data = response.json()
        
        # Set auth header
        client.headers["Authorization"] = f"Bearer {token_data['access_token']}"
        yield client

@pytest.fixture(autouse=True)
async def clean_database():
    """Clean database before each test"""
    # Since we're using in-memory SQLite for tests, 
    # the database is automatically cleaned between server restarts
    # For now, we'll rely on the test environment using :memory: database
    yield

# Configure asyncio for pytest
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()