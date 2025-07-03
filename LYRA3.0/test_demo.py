#!/usr/bin/env python3
"""
LYRA 3.0 Demo Test Script
Demonstrates the command processing capabilities
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.decision_engine import DecisionEngine
from core.context_manager import ContextManager

def demo_lyra_commands():
    """Demonstrate LYRA 3.0 command processing"""
    print("🤖 LYRA 3.0 Command Processing Demo")
    print("=" * 50)
    
    # Initialize components
    context_mgr = ContextManager()
    decision_engine = DecisionEngine(context_mgr)
    
    # Test commands
    test_commands = [
        "Hello LYRA",
        "System status",
        "Switch to defense mode", 
        "Move TRINETRA forward",
        "Launch KRAIT-3",
        "Help",
        "Thank you"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n[TEST {i}] Command: '{command}'")
        print("-" * 30)
        
        response = decision_engine.process_command(command)
        
        print(f"Status: {response.get('status', 'unknown')}")
        print(f"Message: {response.get('message', 'No message')}")
        
        if 'action' in response:
            print(f"Action: {response['action']}")
        
        if 'intent' in response:
            print(f"Intent: {response['intent']}")
            
        print()
    
    print("🎯 Demo completed! LYRA 3.0 successfully processed all commands.")

if __name__ == "__main__":
    demo_lyra_commands()
