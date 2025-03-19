#!/usr/bin/env python
"""
End-to-end test script for the FuturNod Researcher API.
This script tests the complete flow from API request to result retrieval.
"""

import os
import requests
import json
import time
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_argparse():
    parser = argparse.ArgumentParser(description='End-to-end test for Researcher API')
    parser.add_argument('--url', default="https://localhost:8000",
                        help='API URL (default: https://localhost:8000)')
    parser.add_argument('--verify-ssl', action='store_true',
                        help='Verify SSL certificates')
    parser.add_argument('--api-key', default=os.getenv("API_KEYS", "").split(",")[0],
                        help='API key (default: from API_KEYS env var)')
    parser.add_argument('--query', default='What are the top 5 programming languages in 2023?',
                        help='Research query to test')
    parser.add_argument('--report-type', default='bullet_points',
                        help='Report type (default: bullet_points)')
    parser.add_argument('--max-wait', type=int, default=300,
                        help='Maximum wait time in seconds (default: 300)')
    parser.add_argument('--poll-interval', type=int, default=10,
                        help='Poll interval in seconds (default: 10)')
    return parser.parse_args()

def print_banner(text):
    """Print a banner with the given text."""
    width = 80
    padding = (width - len(text) - 2) // 2
    print("=" * width)
    print(" " * padding + text + " " * padding)
    print("=" * width)

def run_test(args):
    """Run the end-to-end test."""
    print_banner("FUTURNOD RESEARCHER API END-TO-END TEST")
    print(f"Starting test with URL: {args.url}")
    
    # Check API key
    if not args.api_key:
        print("ERROR: API key is required. Use --api-key or set API_KEYS environment variable.")
        return False
    
    # Set up headers
    headers = {
        "X-API-Key": args.api_key,
        "Content-Type": "application/json"
    }
    
    # Step 1: Test health endpoint
    print("\n--- Step 1: Testing health endpoint ---")
    try:
        response = requests.get(
            f"{args.url}/health",
            verify=args.verify_ssl
        )
        
        if response.status_code == 200:
            print(f"✅ Health check successful: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check failed with exception: {str(e)}")
        return False
    
    # Step 2: Test research endpoint
    print("\n--- Step 2: Testing research endpoint ---")
    try:
        data = {
            "query": args.query,
            "report_type": args.report_type
        }
        
        response = requests.post(
            f"{args.url}/research",
            headers=headers,
            json=data,
            verify=args.verify_ssl
        )
        
        if response.status_code != 200:
            print(f"❌ Research API request failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        print(f"✅ Research API request successful: {json.dumps(result, indent=2)}")
        
        if not result.get("success", False):
            print(f"❌ Research API returned success=false: {result.get('message', 'No message')}")
            return False
        
        request_id = result.get("request_id")
        if not request_id:
            print("❌ Research API didn't return a request_id")
            return False
        
        print(f"📝 Request ID: {request_id}")
        
        # Step 3: Poll for results
        print("\n--- Step 3: Polling for results ---")
        
        start_time = time.time()
        max_wait_time = args.max_wait
        poll_interval = args.poll_interval
        
        while time.time() - start_time < max_wait_time:
            elapsed = time.time() - start_time
            print(f"⏳ Checking status after {elapsed:.1f}s...")
            
            try:
                status_response = requests.get(
                    f"{args.url}/status/{request_id}",
                    headers=headers,
                    verify=args.verify_ssl
                )
                
                if status_response.status_code != 200:
                    print(f"⚠️ Status check returned {status_response.status_code} - {status_response.text}")
                    time.sleep(poll_interval)
                    continue
                
                status_result = status_response.json()
                
                # If task is still processing
                if status_result.get("success") and status_result.get("data", {}).get("task_status") == "processing":
                    print("🔄 Task is still processing...")
                    time.sleep(poll_interval)
                    continue
                
                # If task completed successfully
                if status_result.get("success") and "task_status" not in status_result.get("data", {}):
                    print("✅ Task completed successfully!")
                    
                    # Extract and save the report
                    file_output = status_result.get("data", {}).get("file_output")
                    if file_output:
                        with open(f"e2e_test_report.md", "w") as f:
                            f.write(file_output)
                        print(f"📄 Saved report to e2e_test_report.md")
                        
                        # Print a preview
                        preview_length = min(500, len(file_output))
                        print(f"\nReport Preview:\n{'='*50}\n{file_output[:preview_length]}...")
                        if len(file_output) > preview_length:
                            print(f"\n... (total length: {len(file_output)} characters)")
                        print('='*50)
                    
                    return True
                
                # If task failed
                print(f"❌ Task failed: {json.dumps(status_result, indent=2)}")
                return False
                
            except Exception as e:
                print(f"⚠️ Error checking status: {str(e)}")
                time.sleep(poll_interval)
        
        print(f"❌ Timeout after {max_wait_time}s waiting for results")
        return False
        
    except Exception as e:
        print(f"❌ Research API request failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    args = setup_argparse()
    success = run_test(args)
    
    if success:
        print_banner("TEST PASSED")
        exit(0)
    else:
        print_banner("TEST FAILED")
        exit(1)
