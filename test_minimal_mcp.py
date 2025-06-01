#!/usr/bin/env python3
"""Test minimal MCP server for debugging"""

import json
import subprocess
import sys
import time
import os
import threading
import queue

def test_minimal_mcp():
    print("=" * 60)
    print("MINIMAL MCP SERVER TEST")
    print("=" * 60)
    
    try:
        # Start the minimal server
        print("🚀 Starting minimal MCP server...")
        
        # Set environment for better debugging
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["MCP_DEBUG"] = "1"
        
        process = subprocess.Popen(
            [sys.executable, "-u", "minimal_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            bufsize=0  # Unbuffered
        )
        
        print("✓ Process started successfully")
        
        # Create output queues
        stdout_queue = queue.Queue()
        stderr_queue = queue.Queue()
        
        def read_stdout():
            try:
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    stdout_queue.put(line.strip())
            except Exception as e:
                stdout_queue.put(f"STDOUT_ERROR: {e}")
        
        def read_stderr():
            try:
                while True:
                    line = process.stderr.readline()
                    if not line:
                        break
                    stderr_queue.put(line.strip())
            except Exception as e:
                stderr_queue.put(f"STDERR_ERROR: {e}")
        
        # Start reader threads
        stdout_thread = threading.Thread(target=read_stdout, daemon=True)
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stdout_thread.start()
        stderr_thread.start()
        
        # Wait for server initialization
        print("⏳ Waiting for server initialization...")
        time.sleep(3)
        
        # Check stderr for startup logs
        startup_messages = []
        try:
            while not stderr_queue.empty():
                msg = stderr_queue.get_nowait()
                if msg.strip():
                    startup_messages.append(msg)
                    print(f"🔧 STARTUP: {msg}")
        except:
            pass
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialize request...")
        request_json = json.dumps(init_request)
        print(f"Request: {request_json}")
        
        try:
            # Write request
            process.stdin.write(request_json + "\n")
            process.stdin.flush()
            print("✓ Request sent")
        except Exception as e:
            print(f"❌ Failed to send request: {e}")
            process.terminate()
            return False
        
        # Wait for response
        print("⏳ Waiting for response...")
        response_received = False
        
        for i in range(15):  # Wait up to 15 seconds
            # Check stdout
            try:
                while not stdout_queue.empty():
                    line = stdout_queue.get_nowait()
                    if line.strip():
                        print(f"📥 STDOUT: {line}")
                        if line.strip().startswith('{'):
                            try:
                                response = json.loads(line)
                                print(f"✓ Valid JSON response: {response}")
                                response_received = True
                            except json.JSONDecodeError:
                                print(f"⚠ Invalid JSON: {line}")
            except:
                pass
            
            # Check stderr
            try:
                while not stderr_queue.empty():
                    line = stderr_queue.get_nowait()
                    if line.strip():
                        print(f"🔧 STDERR: {line}")
            except:
                pass
            
            # Check if process died
            if process.poll() is not None:
                print(f"❌ Process exited with code: {process.poll()}")
                break
            
            if response_received:
                break
                
            time.sleep(1)
        
        success = response_received
        
        if success:
            print("✅ Initialize successful! Testing tools list...")
            
            # Send tools list request
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            tools_json = json.dumps(tools_request)
            try:
                process.stdin.write(tools_json + "\n")
                process.stdin.flush()
                print("✓ Tools list request sent")
                
                # Wait for tools response
                time.sleep(2)
                tools_received = False
                try:
                    while not stdout_queue.empty():
                        line = stdout_queue.get_nowait()
                        if line.strip():
                            print(f"📥 TOOLS: {line}")
                            if '"tools"' in line or '"result"' in line:
                                tools_received = True
                except:
                    pass
                
                if tools_received:
                    print("✅ Tools list received!")
                else:
                    print("⚠ Tools list not received")
                    
            except Exception as e:
                print(f"❌ Failed to request tools: {e}")
        
        # Clean up
        try:
            process.terminate()
            process.wait(timeout=3)
        except:
            process.kill()
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing minimal MCP server...")
    success = test_minimal_mcp()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ MINIMAL MCP SERVER WORKING!")
    else:
        print("❌ MINIMAL MCP SERVER FAILED!")
    print("=" * 60) 