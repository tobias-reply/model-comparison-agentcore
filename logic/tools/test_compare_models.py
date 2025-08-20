import requests
import json
import os
import glob
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_ids import MODEL_IDS

def call_compare_agent(prompt, model_id=None, system_prompt=None):
    """Call the compare models agent with given parameters"""
    url = "http://127.0.0.1:8081/invocations"  # Different port for compare_models
    headers = {"Content-Type": "application/json"}
    
    payload = {"prompt": prompt}
    if model_id:
        payload["model_id"] = model_id
    if system_prompt:
        payload["system_prompt"] = system_prompt
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def parse_output_file(file_path):
    """Parse output file to extract original prompt, correct answer, and response"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    original_prompt = ""
    correct_answer = None
    prompt_index = None
    response = ""
    
    # Parse the structured format
    for i, line in enumerate(lines):
        if line.startswith("Prompt Index: "):
            prompt_index = line[14:]  # Remove "Prompt Index: " prefix
        elif line.startswith("Prompt: "):
            original_prompt = line[8:]  # Remove "Prompt: " prefix
        elif line.startswith("Correct Answer: "):
            correct_answer = line[16:]  # Remove "Correct Answer: " prefix
        elif line.startswith("Response: "):
            # Get all lines after "Response: "
            response = '\n'.join(lines[i:]).replace("Response: ", "", 1)
            break
    
    return original_prompt, correct_answer, response, prompt_index

def save_comparison_output(analyzed_model_id, answering_model_id, original_question, correct_answer, original_response, formatted_prompt, analysis_response, timestamp, prompt_index):
    """Save comparison output with both model identifications"""
    # Clean model_ids for filename
    clean_analyzed = analyzed_model_id.replace(".", "_").replace(":", "_")
    clean_answering = answering_model_id.replace(".", "_").replace(":", "_")
    
    filename = f"comparison_analyzed_{clean_analyzed}_answered_{clean_answering}_{timestamp}.txt"
    
    # Create prompt-specific directory in compare_output folder
    prompt_dir = os.path.join("..", "compare_output", f"prompt_{prompt_index}")
    os.makedirs(prompt_dir, exist_ok=True)
    
    filepath = os.path.join(prompt_dir, filename)
    with open(filepath, "w") as f:
        f.write(f"Analyzed Model ID: {analyzed_model_id}\n")
        f.write(f"Answering Model ID: {answering_model_id}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("-" * 70 + "\n")
        f.write("ORIGINAL QUESTION:\n")
        f.write("-" * 70 + "\n")
        f.write(f"{original_question}\n")
        if correct_answer:
            f.write("-" * 70 + "\n")
            f.write("CORRECT ANSWER:\n")
            f.write("-" * 70 + "\n")
            f.write(f"{correct_answer}\n")
        f.write("-" * 70 + "\n")
        f.write("ORIGINAL RESPONSE (from analyzed model):\n")
        f.write("-" * 70 + "\n")
        f.write(f"{original_response}\n")
        f.write("-" * 70 + "\n")
        f.write("FORMATTED PROMPT SENT TO COMPARING MODEL:\n")
        f.write("-" * 70 + "\n")
        f.write(f"{formatted_prompt}\n")
        f.write("-" * 70 + "\n")
        f.write("ANALYSIS RESPONSE:\n")
        f.write("-" * 70 + "\n")
        f.write(f"{analysis_response}\n\n")
    
    return filepath

def test_compare_models():
    """Test compare models by analyzing outputs from logic/outputs/ folder"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get all output files from ../math_output/ prompt folders
    output_files = glob.glob("../math_output/prompt_*/output_*.txt")
    
    if not output_files:
        print("No output files found in ../math_output/ prompt folders")
        return []
    
    print("Testing compare models...")
    print(f"Available models for analysis: {len(MODEL_IDS)}")
    print(f"Output files to analyze: {len(output_files)}")
    print("-" * 50)
    
    results = []
    
    for output_file in output_files:
        # Extract the original model ID from filename
        filename = os.path.basename(output_file)
        # Parse filename like: output_eu_anthropic_claude-3-7-sonnet-20250219-v1_0_20250820_112823.txt
        parts = filename.replace("output_", "").replace(".txt", "").split("_")
        # Reconstruct the original model ID
        analyzed_model_id = ".".join(parts[:-2]) + ":" + parts[-2]
        
        print(f"\nAnalyzing output from model: {analyzed_model_id}")
        print(f"File: {output_file}")
        
        # Parse the original output file to extract question, correct answer, and response
        original_question, correct_answer, original_response, prompt_index = parse_output_file(output_file)
        
        # Format the prompt exactly as specified in the workflow
        formatted_prompt = f"User requested answer for following problem: {original_question}. AI-Agent responded like this: {original_response}"
        
        # Add correct answer information if available
        if correct_answer:
            formatted_prompt += f". This is the answer we know is correct: {correct_answer}. Please compare the given answer to the verified one and make sure to adjust your ratings accordingly."
        
        # Test with each model for comparison
        for answering_model_id in MODEL_IDS:
            print(f"  Using {answering_model_id} for analysis...")
            print(f"  Original question: {original_question}")
            if correct_answer:
                print(f"  Correct answer available: {correct_answer}")
            
            analysis_response = call_compare_agent(formatted_prompt, answering_model_id)
            filepath = save_comparison_output(
                analyzed_model_id, answering_model_id, original_question, 
                correct_answer, original_response, formatted_prompt, analysis_response, timestamp, prompt_index
            )
            
            results.append({
                "analyzed_model_id": analyzed_model_id,
                "answering_model_id": answering_model_id,
                "prompt_index": prompt_index,
                "original_question": original_question,
                "correct_answer": correct_answer,
                "original_response": original_response,
                "formatted_prompt": formatted_prompt,
                "analysis_response": analysis_response,
                "original_file": output_file,
                "output_file": filepath
            })
            print(f"    Saved to: {filepath}")
    
    # Save summary
    summary_file = f"../compare_output/comparison_summary_{timestamp}.json"
    with open(summary_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nCompleted! Summary saved to: {summary_file}")
    return results

if __name__ == "__main__":
    print("Compare Models Test")
    print("Make sure your compare_models agent is running on http://127.0.0.1:8081")
    
    try:
        results = test_compare_models()
        print(f"\nTested {len(results)} combinations successfully!")
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nError during testing: {e}")