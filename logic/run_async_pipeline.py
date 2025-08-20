#!/usr/bin/env python3
"""
Async Pipeline Runner
Runs the complete async workflow:
- Processes math agent requests asynchronously
- Immediately sends completed responses to compare agent
- Pipelines the entire process for maximum efficiency
"""

import subprocess
import sys
import time
from datetime import datetime

def main():
    """Run the async pipeline workflow"""
    start_time = datetime.now()
    
    print("🚀 Starting Async Pipeline Workflow")
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis async pipeline will:")
    print("1. Send requests to math_agent asynchronously")
    print("2. As soon as each response is ready, send it to compare_agent")
    print("3. Process multiple requests in parallel for maximum efficiency")
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
    
    print(f"\n{'='*60}")
    print("RUNNING ASYNC PIPELINE")
    print(f"{'='*60}")
    
    try:
        # Run the async pipeline script
        result = subprocess.run(
            [sys.executable, "test_async_pipeline.py"], 
            capture_output=False,  # Show output in real-time
            text=True,
            cwd="tools"
        )
        
        success = result.returncode == 0
        
    except Exception as e:
        print(f"\n❌ Error running async pipeline: {e}")
        success = False
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print("🏁 ASYNC PIPELINE COMPLETE")
    print(f"{'='*60}")
    print(f"Duration: {duration}")
    print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("✅ Async pipeline completed successfully!")
        print("\nResults saved in:")
        print("- math_output/ (organized by prompt folders)")
        print("- compare_output/ (organized by prompt folders)")
        print("\n🚀 Performance Benefits:")
        print("- Math and compare agents work in parallel")
        print("- No waiting between requests")
        print("- Maximum throughput achieved")
    else:
        print("❌ Async pipeline failed. Check the output above for details.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAsync pipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)