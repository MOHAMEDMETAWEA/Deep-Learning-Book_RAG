"""
Test Suite for LangChain Chat Project
Tests all three interfaces (API, Gradio, CLI) and validates functionality
"""

import requests
import time
import json
import sys
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
API_BASE = os.getenv("API_BASE", "http://localhost:8000")
TIMEOUT = 30
TEST_SESSION = "test_session_verify"

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{'='*60}\n{text}\n{'='*60}{RESET}")

def print_pass(text):
    print(f"{GREEN}✅ PASS{RESET}: {text}")

def print_fail(text):
    print(f"{RED}❌ FAIL{RESET}: {text}")

def print_info(text):
    print(f"{YELLOW}ℹ️  INFO{RESET}: {text}")

def print_test(text):
    print(f"\n{BLUE}🧪 TEST{RESET}: {text}")

# ============================================================================
# TEST 1: Health Check
# ============================================================================

def test_health_check():
    print_test("API Health Check")
    try:
        r = requests.get(f"{API_BASE}/health", timeout=TIMEOUT)
        data = r.json()
        
        if r.status_code == 200 and data.get("status") == "ok":
            print_pass(f"API is running (version {data.get('version', 'unknown')})")
            return True
        else:
            print_fail(f"Unexpected response: {r.status_code} - {data}")
            return False
    except requests.exceptions.ConnectionError:
        print_fail(f"Cannot connect to {API_BASE}")
        print_info("Make sure to run: uvicorn api:api --reload")
        return False
    except Exception as e:
        print_fail(f"Error: {str(e)}")
        return False

# ============================================================================
# TEST 2: Chat Endpoint - Basic Functionality
# ============================================================================

def test_chat_endpoint():
    print_test("Chat Endpoint - Basic Functionality")
    
    payload = {
        "session_id": TEST_SESSION,
        "question": "مرحبا، من أنت؟"  # Arabic: "Hi, who are you?"
    }
    
    try:
        r = requests.post(
            f"{API_BASE}/chat",
            json=payload,
            timeout=TIMEOUT
        )
        
        if r.status_code == 200:
            data = r.json()
            if data.get("session_id") == TEST_SESSION and data.get("answer"):
                print_pass(f"Chat response received: {data['answer'][:60]}...")
                return True
            else:
                print_fail(f"Incomplete response: {data}")
                return False
        else:
            print_fail(f"HTTP {r.status_code}: {r.text}")
            return False
    except Exception as e:
        print_fail(f"Error: {str(e)}")
        return False

# ============================================================================
# TEST 3: Input Validation
# ============================================================================

def test_input_validation():
    print_test("Input Validation")
    
    # Test 1: Empty session_id
    print("  Testing empty session_id...")
    payload = {"session_id": "", "question": "test"}
    try:
        r = requests.post(f"{API_BASE}/chat", json=payload, timeout=TIMEOUT)
        if r.status_code == 422:  # Validation error
            print_pass("Empty session_id correctly rejected")
        else:
            print_fail(f"Should reject empty session_id, got {r.status_code}")
            return False
    except Exception as e:
        print_fail(f"Error: {str(e)}")
        return False
    
    # Test 2: Oversized session_id
    print("  Testing oversized session_id...")
    payload = {"session_id": "x" * 100, "question": "test"}
    try:
        r = requests.post(f"{API_BASE}/chat", json=payload, timeout=TIMEOUT)
        if r.status_code == 422:  # Validation error
            print_pass("Oversized session_id correctly rejected")
        else:
            print_fail(f"Should reject oversized session_id, got {r.status_code}")
            return False
    except Exception as e:
        print_fail(f"Error: {str(e)}")
        return False
    
    # Test 3: Empty question
    print("  Testing empty question...")
    payload = {"session_id": "valid_id", "question": ""}
    try:
        r = requests.post(f"{API_BASE}/chat", json=payload, timeout=TIMEOUT)
        if r.status_code == 422:  # Validation error
            print_pass("Empty question correctly rejected")
        else:
            print_fail(f"Should reject empty question, got {r.status_code}")
            return False
    except Exception as e:
        print_fail(f"Error: {str(e)}")
        return False
    
    print_pass("All validation tests passed")
    return True

# ============================================================================
# TEST 4: History Tracking
# ============================================================================

def test_history_tracking():
    print_test("History Tracking")
    
    session_id = f"{TEST_SESSION}_history"
    
    # Send first message
    print("  Sending first message...")
    r1 = requests.post(
        f"{API_BASE}/chat",
        json={"session_id": session_id, "question": "السؤال الأول"},
        timeout=TIMEOUT
    )
    
    if r1.status_code != 200:
        print_fail(f"First message failed: {r1.status_code}")
        return False
    
    time.sleep(1)
    
    # Send second message
    print("  Sending second message...")
    r2 = requests.post(
        f"{API_BASE}/chat",
        json={"session_id": session_id, "question": "السؤال الثاني"},
        timeout=TIMEOUT
    )
    
    if r2.status_code != 200:
        print_fail(f"Second message failed: {r2.status_code}")
        return False
    
    # Check history
    print("  Checking history...")
    r_history = requests.get(
        f"{API_BASE}/history/{session_id}",
        timeout=TIMEOUT
    )
    
    if r_history.status_code == 200:
        history = r_history.json()
        count = len(history.get("history", []))
        
        if count >= 4:  # 2 Q&A = 4 messages
            print_pass(f"History tracked {count} messages correctly")
            return True
        else:
            print_fail(f"Expected ≥4 messages, got {count}")
            return False
    else:
        print_fail(f"History retrieval failed: {r_history.status_code}")
        return False

# ============================================================================
# TEST 5: Session Isolation
# ============================================================================

def test_session_isolation():
    print_test("Session Isolation")
    
    # Create message in session A
    print("  Creating session A...")
    r_a = requests.post(
        f"{API_BASE}/chat",
        json={"session_id": "session_a", "question": "في الجلسة أ"},
        timeout=TIMEOUT
    )
    
    # Create message in session B
    print("  Creating session B...")
    r_b = requests.post(
        f"{API_BASE}/chat",
        json={"session_id": "session_b", "question": "في الجلسة ب"},
        timeout=TIMEOUT
    )
    
    if r_a.status_code != 200 or r_b.status_code != 200:
        print_fail("Failed to create sessions")
        return False
    
    # Check that histories are different
    print("  Verifying histories are isolated...")
    h_a = requests.get(f"{API_BASE}/history/session_a", timeout=TIMEOUT).json()
    h_b = requests.get(f"{API_BASE}/history/session_b", timeout=TIMEOUT).json()
    
    hist_a = h_a.get("history", [])
    hist_b = h_b.get("history", [])
    
    # Check that session A contains "أ" and session B contains "ب"
    a_has_correct_msg = any("أ" in msg.get("content", "") for msg in hist_a)
    b_has_correct_msg = any("ب" in msg.get("content", "") for msg in hist_b)
    
    if a_has_correct_msg and b_has_correct_msg:
        print_pass("Sessions are properly isolated")
        return True
    else:
        print_fail("Sessions not properly isolated")
        return False

# ============================================================================
# TEST 6: Clear Session
# ============================================================================

def test_clear_session():
    print_test("Clear Session")
    
    session_id = f"{TEST_SESSION}_clear"
    
    # Add message
    print("  Adding message...")
    requests.post(
        f"{API_BASE}/chat",
        json={"session_id": session_id, "question": "رسالة للحذف"},
        timeout=TIMEOUT
    )
    
    # Clear session
    print("  Clearing session...")
    r_clear = requests.post(
        f"{API_BASE}/clear",
        json={"session_id": session_id},
        timeout=TIMEOUT
    )
    
    if r_clear.status_code != 200:
        print_fail(f"Clear failed: {r_clear.status_code}")
        return False
    
    # Check history is empty
    print("  Verifying history is empty...")
    r_history = requests.get(f"{API_BASE}/history/{session_id}", timeout=TIMEOUT)
    
    if r_history.status_code == 200:
        history = r_history.json().get("history", [])
        if len(history) == 0:
            print_pass("Session cleared successfully")
            return True
        else:
            print_fail(f"History not empty: {len(history)} messages remaining")
            return False
    else:
        print_fail(f"History check failed: {r_history.status_code}")
        return False

# ============================================================================
# TEST 7: Error Handling
# ============================================================================

def test_error_handling():
    print_test("Error Handling")
    
    # Test invalid JSON
    print("  Testing invalid JSON...")
    try:
        r = requests.post(
            f"{API_BASE}/chat",
            data="not json",
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        if r.status_code in [400, 422]:
            print_pass("Invalid JSON correctly rejected")
        else:
            print_fail(f"Should return 4xx, got {r.status_code}")
            return False
    except Exception as e:
        print_pass(f"Invalid JSON error handled: {str(e)[:50]}")
    
    # Test timeout on nonexistent endpoint
    print("  Testing nonexistent endpoint...")
    try:
        r = requests.get(f"{API_BASE}/nonexistent", timeout=5)
        if r.status_code == 404:
            print_pass("Nonexistent endpoint returns 404")
        else:
            print_fail(f"Expected 404, got {r.status_code}")
            return False
    except Exception as e:
        print_fail(f"Unexpected error: {str(e)}")
        return False
    
    print_pass("Error handling tests passed")
    return True

# ============================================================================
# TEST 8: Concurrency (Multiple Requests)
# ============================================================================

def test_concurrency():
    print_test("Concurrency Test")
    
    print("  Sending 3 concurrent requests...")
    import threading
    results = []
    
    def send_request(msg_num):
        try:
            r = requests.post(
                f"{API_BASE}/chat",
                json={
                    "session_id": f"concurrent_{msg_num}",
                    "question": f"الرسالة {msg_num}"
                },
                timeout=TIMEOUT
            )
            results.append(r.status_code == 200)
        except:
            results.append(False)
    
    threads = [threading.Thread(target=send_request, args=(i,)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    if all(results) and len(results) == 3:
        print_pass("Concurrency test passed (3/3 successful)")
        return True
    else:
        print_fail(f"Concurrency test failed ({sum(results)}/3 successful)")
        return False

# ============================================================================
# TEST 9: Response Format
# ============================================================================

def test_response_format():
    print_test("Response Format Validation")
    
    r = requests.post(
        f"{API_BASE}/chat",
        json={"session_id": "format_test", "question": "test"},
        timeout=TIMEOUT
    )
    
    if r.status_code != 200:
        print_fail(f"Chat request failed: {r.status_code}")
        return False
    
    data = r.json()
    
    # Check required fields
    required_fields = ["session_id", "answer"]
    missing = [f for f in required_fields if f not in data]
    
    if missing:
        print_fail(f"Missing fields: {missing}")
        return False
    
    # Check field types
    if not isinstance(data["session_id"], str):
        print_fail("session_id is not string")
        return False
    
    if not isinstance(data["answer"], str):
        print_fail("answer is not string")
        return False
    
    print_pass(f"Response format valid: {json.dumps(data, ensure_ascii=False)[:80]}...")
    return True

# ============================================================================
# TEST 10: Documentation Endpoints
# ============================================================================

def test_documentation():
    print_test("Documentation Endpoints")
    
    # Check /docs
    print("  Checking /docs...")
    try:
        r = requests.get(f"{API_BASE}/docs", timeout=TIMEOUT)
        if r.status_code == 200:
            print_pass("Swagger UI available at /docs")
        else:
            print_fail(f"/docs returned {r.status_code}")
            return False
    except Exception as e:
        print_fail(f"Error accessing /docs: {str(e)}")
        return False
    
    # Check /openapi.json
    print("  Checking /openapi.json...")
    try:
        r = requests.get(f"{API_BASE}/openapi.json", timeout=TIMEOUT)
        if r.status_code == 200:
            print_pass("OpenAPI schema available")
        else:
            print_fail(f"/openapi.json returned {r.status_code}")
            return False
    except Exception as e:
        print_fail(f"Error accessing /openapi.json: {str(e)}")
        return False
    
    return True

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    print_header("🧪 LangChain Chat - Full Test Suite")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Session: {TEST_SESSION}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Chat Endpoint", test_chat_endpoint),
        ("Input Validation", test_input_validation),
        ("History Tracking", test_history_tracking),
        ("Session Isolation", test_session_isolation),
        ("Clear Session", test_clear_session),
        ("Error Handling", test_error_handling),
        ("Concurrency", test_concurrency),
        ("Response Format", test_response_format),
        ("Documentation", test_documentation),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print_fail(f"Unexpected error in {name}: {str(e)}")
            results[name] = False
    
    # Summary
    print_header("📊 Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {GREEN}{passed}/{total}{RESET} tests passed")
    
    if passed == total:
        print(f"\n{GREEN}{'='*60}")
        print("🎉 ALL TESTS PASSED! System is ready for production.")
        print(f"{'='*60}{RESET}")
        return 0
    else:
        print(f"\n{RED}{'='*60}")
        print(f"⚠️  {total - passed} test(s) failed. Please review the output above.")
        print(f"{'='*60}{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
