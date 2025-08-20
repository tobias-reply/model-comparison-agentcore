import requests
import json
import os
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_ids import MODEL_IDS
from test_prompts import TEST_PROMPTS

def call_agent(prompt, model_id=None):
    """Call the local agent with given parameters"""
    url = "http://127.0.0.1:8080/invocations"
    headers = {"Content-Type": "application/json"}
    
    payload = {"prompt": prompt}
    if model_id:
        payload["model_id"] = model_id
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def save_output(model_id, prompt_data, response, timestamp, prompt_index):
    """Save output to a file with model ID identification"""
    # Clean model_id for filename (replace dots and colons)
    clean_model_id = model_id.replace(".", "_").replace(":", "_")
    filename = f"output_{clean_model_id}_{timestamp}.txt"
    
    # Create prompt-specific directory in math_output folder
    prompt_dir = os.path.join("..", "math_output", f"prompt_{prompt_index}")
    os.makedirs(prompt_dir, exist_ok=True)
    
    # Handle both string and dict prompt formats
    if isinstance(prompt_data, dict):
        prompt_text = prompt_data["question"]
        correct_answer = prompt_data.get("answer")
    else:
        prompt_text = prompt_data
        correct_answer = None
    
    filepath = os.path.join(prompt_dir, filename)
    with open(filepath, "w") as f:
        f.write(f"Model ID: {model_id}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Prompt Index: {prompt_index}\n")
        f.write(f"Prompt: {prompt_text}\n")
        if correct_answer:
            f.write(f"Correct Answer: {correct_answer}\n")
        f.write("-" * 50 + "\n")
        f.write(f"Response: {response}\n\n")
    
    return filepath

def test_all_models():
    """Test all models with all prompts and save outputs"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("Testing models...")
    print(f"Available models: {len(MODEL_IDS)}")
    print(f"Test prompts: {len(TEST_PROMPTS)}")
    print("-" * 50)
    
    results = []
    
    for model_id in MODEL_IDS:
        print(f"\nTesting model: {model_id}")
        for i, prompt_data in enumerate(TEST_PROMPTS, 1):
            # Handle both string and dict prompt formats
            if isinstance(prompt_data, dict):
                prompt_text = prompt_data["question"]
                display_prompt = prompt_text
            else:
                prompt_text = prompt_data
                display_prompt = prompt_text
            
            print(f"  Prompt {i}: {display_prompt}")
            response = call_agent(prompt_text, model_id)
            filepath = save_output(model_id, prompt_data, response, timestamp, i)
            results.append({
                "model_id": model_id,
                "prompt_index": i,
                "prompt": prompt_data,
                "response": response,
                "file": filepath
            })
            print(f"    Saved to: {filepath}")
    
    # Save summary
    summary_file = f"../math_output/summary_{timestamp}.json"
    with open(summary_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nCompleted! Summary saved to: {summary_file}")
    return results

if __name__ == "__main__":
    print("Model Comparison Test")
    print("Make sure your agent is running on http://127.0.0.1:8080")
    
    try:
        results = test_all_models()
        print(f"\nTested {len(results)} combinations successfully!")
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nError during testing: {e}")