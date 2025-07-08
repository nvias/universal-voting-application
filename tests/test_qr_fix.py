#!/usr/bin/env python3
"""
Quick test to verify QR code fix
"""

import subprocess
import time
import requests

def run_cmd(cmd):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔧 Testing QR Code Fix")
    print("=" * 30)
    
    # Rebuild the container
    print("\n1️⃣  Rebuilding container...")
    success, stdout, stderr = run_cmd("docker-compose up -d --build")
    if not success:
        print(f"   ❌ Failed to rebuild: {stderr}")
        return False
    print("   ✅ Container rebuilt")
    
    # Wait for service
    print("\n2️⃣  Waiting for service...")
    for i in range(30):
        try:
            response = requests.get("http://localhost:5000/api/v1/health", timeout=2)
            if response.status_code == 200:
                print("   ✅ Service is ready!")
                break
        except:
            pass
        print(f"   ⏳ Waiting... ({i+1}/30)")
        time.sleep(1)
    else:
        print("   ❌ Service not ready")
        return False
    
    # Test QR page directly
    print("\n3️⃣  Testing QR page...")
    try:
        # First, get a voting session ID
        sessions_response = requests.get("http://localhost:5000/api/v1/voting", timeout=5)
        if sessions_response.status_code == 200:
            sessions = sessions_response.json()
            if sessions:
                voting_id = sessions[0]['id']
                qr_url = f"http://localhost:5000/presentation/{voting_id}"
                
                # Test QR page
                qr_response = requests.get(qr_url, timeout=5)
                if qr_response.status_code == 200:
                    print(f"   ✅ QR page loads: {qr_url}")
                    
                    # Check if it contains the fixed JavaScript
                    if "generateFallbackQR" in qr_response.text:
                        print("   ✅ QR fix is applied")
                    else:
                        print("   ⚠️  QR fix might not be applied")
                else:
                    print(f"   ❌ QR page failed: {qr_response.status_code}")
            else:
                print("   ⚠️  No voting sessions found")
        else:
            print(f"   ❌ Could not get voting sessions: {sessions_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing QR page: {e}")
    
    print("\n🎯 Test Results:")
    print("   • QR page should now work with fallback")
    print("   • If QR library fails, it will use qrserver.com")
    print("   • If that fails, it shows direct link")
    print("\n📱 Try visiting the QR page now:")
    print("   http://localhost:5000/presentation/607473")

if __name__ == "__main__":
    main()
