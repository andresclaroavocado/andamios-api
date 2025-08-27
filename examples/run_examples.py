"""
Run all API CRUD examples

Rules:
- Check API server availability first
- Run each example in sequence
- Report success/failure for each
"""

import asyncio
import httpx
import subprocess
import sys
from pathlib import Path

async def check_api_health():
    """Check if API server is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/health", timeout=2.0)
            return response.status_code == 200
    except:
        return False

def run_example(script_name: str) -> bool:
    """Run a single example script"""
    script_path = Path(__file__).parent / "basic" / script_name
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {script_name}: SUCCESS")
            print(f"   Output: {result.stdout.strip().split(chr(10))[-1]}")  # Last line
            return True
        else:
            print(f"❌ {script_name}: FAILED")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {script_name}: TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {script_name}: EXCEPTION - {e}")
        return False

async def main():
    print("🚀 Running all Andamios API CRUD examples")
    print("=" * 50)
    
    # Check API health
    print("🏥 Checking API server health...")
    if not await check_api_health():
        print("❌ API server not available at http://localhost:8001")
        print("   Start server with: uvicorn src.andamios_api.main:app --port 8001 --reload")
        return
    print("✅ API server is healthy")
    
    # Run examples
    examples = ["user_crud.py", "item_crud.py", "auth_example.py", "user_crud_auth.py"]
    results = []
    
    print(f"\n📋 Running {len(examples)} examples:")
    print("-" * 30)
    
    for example in examples:
        success = run_example(example)
        results.append((example, success))
    
    # Summary
    print(f"\n📊 Results Summary:")
    print("-" * 20)
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for example, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {example}: {status}")
    
    print(f"\n🎯 Overall: {successful}/{total} examples passed")
    
    if successful == total:
        print("🎉 All examples completed successfully!")
        return 0
    else:
        print("⚠️  Some examples failed")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
        sys.exit(130)