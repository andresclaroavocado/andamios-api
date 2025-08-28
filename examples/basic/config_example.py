"""
Configuration Example (client-only)

Rules:
- No server/FastAPI setup here.
- Shows different environment configurations.
- Validates required settings are present.
- Demonstrates environment switching.
"""

import os
import sys
from pathlib import Path

# Add src to path to import config
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_environment_config(env_name: str):
    """Test configuration for a specific environment"""
    print(f"\n🔧 Testing {env_name.upper()} Configuration")
    print("-" * 40)
    
    # Set environment variable
    os.environ["ENVIRONMENT"] = env_name
    
    try:
        # Import config (this will load the environment-specific settings)
        from andamios_api.core.config import get_settings, validate_required_config
        
        # Get fresh settings for this environment
        settings = get_settings()
        
        # Display configuration
        print(f"   Environment: {settings.environment}")
        print(f"   Database URL: {settings.database_url}")
        print(f"   API Host: {settings.api_host}:{settings.api_port}")
        print(f"   Debug Mode: {settings.api_debug}")
        print(f"   JWT Secret: {settings.jwt_secret_key[:16]}... (truncated)")
        print(f"   JWT Expiration: {settings.jwt_access_token_expire_minutes} minutes")
        print(f"   CORS Origins: {len(settings.cors_origins_list)} configured")
        print(f"   Log Level: {settings.log_level}")
        
        # Validate configuration
        validate_required_config(settings)
        print("   ✅ Configuration validation: PASSED")
        
        return True
        
    except ValueError as e:
        print(f"   ❌ Configuration validation: FAILED")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"   💥 Configuration loading: FAILED")
        print(f"   Error: {e}")
        return False

def test_missing_config():
    """Test behavior when configuration files are missing"""
    print(f"\n🚨 Testing Missing Configuration")
    print("-" * 40)
    
    # Set environment to non-existent one
    os.environ["ENVIRONMENT"] = "nonexistent"
    
    try:
        from andamios_api.core.config import get_settings
        
        # Clear module cache to force reload
        if 'andamios_api.core.config' in sys.modules:
            del sys.modules['andamios_api.core.config']
        
        settings = get_settings()
        print(f"   Fallback to defaults: ✅")
        print(f"   Environment: {settings.environment}")
        print(f"   Database URL: {settings.database_url}")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to handle missing config: {e}")
        return False

def main():
    print("🚀 Configuration Validation Example")
    print("=" * 50)
    
    # Test each environment configuration
    environments = ["development", "test", "production"]
    results = []
    
    for env in environments:
        # Clear module cache to force fresh config loading
        if 'andamios_api.core.config' in sys.modules:
            del sys.modules['andamios_api.core.config']
            
        success = test_environment_config(env)
        results.append((env, success))
    
    # Test missing configuration handling
    missing_config_success = test_missing_config()
    
    # Summary
    print(f"\n📊 Configuration Test Summary")
    print("=" * 35)
    
    for env, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {env.capitalize()}: {status}")
    
    missing_status = "✅ PASS" if missing_config_success else "❌ FAIL"
    print(f"   Missing config: {missing_status}")
    
    total_tests = len(results) + 1
    passed_tests = sum(1 for _, success in results if success) + (1 if missing_config_success else 0)
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All configuration tests passed!")
    else:
        print("⚠️  Some configuration tests failed")
    
    # Environment-specific tips
    print(f"\n💡 Environment Tips:")
    print("   - Use ENVIRONMENT=development for local development")
    print("   - Use ENVIRONMENT=test for automated testing")
    print("   - Use ENVIRONMENT=production for production deployment")
    print("   - Update .env.production with your production values")

if __name__ == "__main__":
    main()