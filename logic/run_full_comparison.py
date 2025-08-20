#!/usr/bin/env python3
"""
Full Model Comparison Runner
Runs the complete workflow:
1. First runs test_math_agent.py to generate initial responses
2. Then runs test_compare_models.py to analyze those responses
"""

import subprocess
import sys
import time
from datetime import datetime

def run_script(script_name, description):
    """Run a Python script and handle the output"""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"Running: {script_name}")
    print(f"{'='*60}")
    
    try:
        # Run the script and capture output
        result = subprocess.run(
            [sys.executable, script_name], 
            capture_output=False,  # Show output in real-time
            text=True,
            cwd="tools"
        )
        
        if result.returncode == 0:
            print(f"\n✅ {script_name} completed successfully!")
            return True
        else:
            print(f"\n❌ {script_name} failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running {script_name}: {e}")
        return False

def main():
    """Run the full comparison workflow"""
    start_time = datetime.now()
    
    print("🚀 Starting Full Model Comparison Workflow")
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis will:")
    print("1. Generate responses from math_agent for all test prompts")
    print("2. Analyze those responses using compare_models agent")
    print("\nMake sure both agents are running:")
    print("- Math agent on http://127.0.0.1:8080")
    print("- Compare models agent on http://127.0.0.1:8081")
    
    # Ask for confirmation
    try:
        response = input("\nContinue? (y/N): ").lower().strip()
        if response != 'y':
            print("Cancelled by user.")
            return
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        return
    
    success_count = 0
    total_steps = 2
    
    # Step 1: Run math agent tests
    if run_script("test_math_agent.py", "Generate initial math responses"):
        success_count += 1
        print(f"\n⏳ Waiting 3 seconds before next step...")
        time.sleep(3)
    else:
        print(f"\n🛑 Stopping workflow due to failure in step 1")
        return
    
    # Step 2: Run comparison tests
    if run_script("test_compare_models.py", "Analyze responses with compare models"):
        success_count += 1
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print("🏁 WORKFLOW COMPLETE")
    print(f"{'='*60}")
    print(f"Completed steps: {success_count}/{total_steps}")
    print(f"Duration: {duration}")
    print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success_count == total_steps:
        print("✅ All steps completed successfully!")
        print("\nResults saved in:")
        print("- math_output/ (original responses)")
        print("- compare_output/ (comparison analyses)")
    else:
        print("❌ Some steps failed. Check the output above for details.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)