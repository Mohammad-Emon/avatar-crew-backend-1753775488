"""Test script to verify CrewAI imports."""

import sys
import pkgutil

def test_imports():
    """Test if we can import CrewAI components."""
    print("=== Testing CrewAI Imports ===\n")
    
    # Check if crewai is installed
    if pkgutil.find_loader("crewai") is None:
        print("❌ Error: crewai package is not installed")
        print("Please install it with: pip install crewai")
        return False
    
    print("✅ crewai package is installed")
    
    # Try to import components
    try:
        from crewai import Agent, Task, Crew
        print("✅ Successfully imported Agent, Task, and Crew from crewai")
        
        # Print the Agent class to see what we're working with
        print("\nAgent class:", Agent)
        print("Agent __module__:", getattr(Agent, "__module__", "N/A"))
        print("Agent __bases__:", getattr(Agent, "__bases__", "N/A"))
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import from crewai: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
