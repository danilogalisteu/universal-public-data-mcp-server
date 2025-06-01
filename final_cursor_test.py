#!/usr/bin/env python3
"""Final test simulating Cursor's MCP connection"""

import json
import subprocess
import sys
import time
import os

def test_cursor_connection():
    print("=" * 70)
    print("🎯 FINAL CURSOR MCP CONNECTION TEST")
    print("=" * 70)
    
    try:
        # Use the exact same configuration as cursor_mcp_config.json
        print("🚀 Starting server with Cursor configuration...")
        
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONPATH"] = "C:\\Users\\mihir\\OneDrive\\Documents\\mcpproject"
        
        # Use absolute path like Cursor would
        process = subprocess.Popen(
            ["python", "C:\\Users\\mihir\\OneDrive\\Documents\\mcpproject\\src\\server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="C:\\Users\\mihir\\OneDrive\\Documents\\mcpproject",
            env=env
        )
        
        print("✓ Server process started")
        
        # Wait for initialization
        time.sleep(3)
        
        print("🤝 Testing full MCP handshake sequence...")
        
        # Step 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "cursor",
                    "version": "0.42.0"
                }
            }
        }
        
        print("📤 1. Sending initialize...")
        try:
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Read response
            response_line = process.stdout.readline()
            print(f"📥 Initialize response: {response_line.strip()}")
            
            init_response = json.loads(response_line)
            if "result" in init_response:
                print("✅ Initialize successful")
            else:
                print("❌ Initialize failed")
                return False
                
        except Exception as e:
            print(f"❌ Initialize failed: {e}")
            return False
        
        # Step 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        print("📤 2. Sending initialized notification...")
        try:
            process.stdin.write(json.dumps(initialized_notification) + "\n")
            process.stdin.flush()
            print("✅ Initialized notification sent")
        except Exception as e:
            print(f"❌ Initialized notification failed: {e}")
            return False
        
        # Step 3: List tools
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        print("📤 3. Requesting tools list...")
        try:
            process.stdin.write(json.dumps(tools_request) + "\n")
            process.stdin.flush()
            
            # Read tools response
            tools_response_line = process.stdout.readline()
            print(f"📥 Tools response received: {len(tools_response_line)} chars")
            
            tools_response = json.loads(tools_response_line)
            if "result" in tools_response and "tools" in tools_response["result"]:
                tools_count = len(tools_response["result"]["tools"])
                print(f"✅ Tools list received: {tools_count} tools available")
                
                # Show first few tools
                for i, tool in enumerate(tools_response["result"]["tools"][:3]):
                    print(f"   🔧 {tool['name']}: {tool['description']}")
                
                if tools_count > 3:
                    print(f"   ... and {tools_count - 3} more tools")
                    
            else:
                print("❌ Tools list invalid")
                return False
                
        except Exception as e:
            print(f"❌ Tools list failed: {e}")
            return False
        
        # Step 4: Test a tool call
        test_tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_system_status",
                "arguments": {}
            }
        }
        
        print("📤 4. Testing tool call (get_system_status)...")
        try:
            process.stdin.write(json.dumps(test_tool_request) + "\n")
            process.stdin.flush()
            
            # Read tool response
            tool_response_line = process.stdout.readline()
            print(f"📥 Tool response received: {len(tool_response_line)} chars")
            
            tool_response = json.loads(tool_response_line)
            if "result" in tool_response:
                print("✅ Tool call successful")
                # Parse the response content
                content = tool_response["result"]
                if isinstance(content, list) and len(content) > 0:
                    first_content = content[0]
                    if "text" in first_content:
                        # Try to parse the JSON inside
                        try:
                            data = json.loads(first_content["text"])
                            print(f"   📊 Status: {data.get('status', 'unknown')}")
                        except:
                            print(f"   📄 Response: {first_content['text'][:100]}...")
            else:
                print("❌ Tool call failed")
                return False
                
        except Exception as e:
            print(f"❌ Tool call failed: {e}")
            return False
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Server successfully handles MCP protocol")
        print("✅ Initialize handshake works")
        print("✅ Tools list retrieval works")
        print("✅ Tool execution works")
        
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=3)
        except:
            process.kill()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing complete MCP connection flow...")
    success = test_cursor_connection()
    
    print("\n" + "=" * 70)
    if success:
        print("🎯 ✅ MCP SERVER IS READY FOR CURSOR!")
        print("You can now use the cursor_mcp_config.json file in Cursor")
        print("Expected behavior: Green dot ✅ in Cursor IDE")
    else:
        print("❌ MCP SERVER NEEDS MORE FIXES")
        print("Check the error messages above")
    print("=" * 70) 