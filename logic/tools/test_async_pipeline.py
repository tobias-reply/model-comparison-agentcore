import asyncio
import aiohttp
import json
import os
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_ids import MODEL_IDS
from test_prompts import TEST_PROMPTS

async def call_math_agent(session, prompt, model_id=None):
    """Call the math agent asynchronously"""
    url = "http://127.0.0.1:8080/invocations"
    headers = {"Content-Type": "application/json"}
    
    payload = {"prompt": prompt}
    if model_id:
        payload["model_id"] = model_id
    
    try:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                return await response.text()
            else:
                return f"Error: {response.status} - {await response.text()}"
    except Exception as e:
        return f"Error: {str(e)}"

async def call_compare_agent(session, prompt, model_id=None):
    """Call the compare agent asynchronously"""
    url = "http://127.0.0.1:8081/invocations"
    headers = {"Content-Type": "application/json"}
    
    payload = {"prompt": prompt}
    if model_id:
        payload["model_id"] = model_id
    
    try:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                return await response.text()
            else:
                return f"Error: {response.status} - {await response.text()}"
    except Exception as e:
        return f"Error: {str(e)}"

def save_math_output(model_id, prompt_data, response, timestamp, prompt_index):
    """Save math agent output to file"""
    clean_model_id = model_id.replace(".", "_").replace(":", "_")
    filename = f"output_{clean_model_id}_{timestamp}.txt"
    
    prompt_dir = os.path.join("..", "math_output", f"prompt_{prompt_index}")
    os.makedirs(prompt_dir, exist_ok=True)
    
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
    
    return filepath, prompt_text, correct_answer

def save_comparison_output(analyzed_model_id, answering_model_id, original_question, correct_answer, original_response, formatted_prompt, analysis_response, timestamp, prompt_index):
    """Save comparison output to file"""
    clean_analyzed = analyzed_model_id.replace(".", "_").replace(":", "_")
    clean_answering = answering_model_id.replace(".", "_").replace(":", "_")
    
    filename = f"comparison_analyzed_{clean_analyzed}_answered_{clean_answering}_{timestamp}.txt"
    
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

async def process_comparison_for_response(session, math_result, timestamp, compare_models):
    """Process all comparison models for a single math response"""
    analyzed_model_id, prompt_index, prompt_data, original_response, filepath, prompt_text, correct_answer = math_result
    
    print(f"  Starting comparisons for {analyzed_model_id} - Prompt {prompt_index}")
    
    # Format the prompt for comparison
    formatted_prompt = f"User requested answer for following problem: {prompt_text}. AI-Agent responded like this: {original_response}"
    if correct_answer:
        formatted_prompt += f". This is the answer we know is correct: {correct_answer}. Please compare the given answer to the verified one and make sure to adjust your ratings accordingly."
    
    comparison_tasks = []
    for answering_model_id in compare_models:
        task = process_single_comparison(
            session, analyzed_model_id, answering_model_id, prompt_text, 
            correct_answer, original_response, formatted_prompt, timestamp, prompt_index
        )
        comparison_tasks.append(task)
    
    # Run all comparisons for this response in parallel
    comparison_results = await asyncio.gather(*comparison_tasks, return_exceptions=True)
    
    print(f"  ✅ Completed all comparisons for {analyzed_model_id} - Prompt {prompt_index}")
    return comparison_results

async def process_single_comparison(session, analyzed_model_id, answering_model_id, prompt_text, correct_answer, original_response, formatted_prompt, timestamp, prompt_index):
    """Process a single comparison"""
    print(f"    Analyzing with {answering_model_id}...")
    
    analysis_response = await call_compare_agent(session, formatted_prompt, answering_model_id)
    filepath = save_comparison_output(
        analyzed_model_id, answering_model_id, prompt_text,
        correct_answer, original_response, formatted_prompt, 
        analysis_response, timestamp, prompt_index
    )
    
    return {
        "analyzed_model_id": analyzed_model_id,
        "answering_model_id": answering_model_id,
        "prompt_index": prompt_index,
        "original_question": prompt_text,
        "correct_answer": correct_answer,
        "original_response": original_response,
        "formatted_prompt": formatted_prompt,
        "analysis_response": analysis_response,
        "output_file": filepath
    }

async def process_math_request(session, model_id, prompt_data, prompt_index, timestamp):
    """Process a single math request"""
    if isinstance(prompt_data, dict):
        prompt_text = prompt_data["question"]
    else:
        prompt_text = prompt_data
    
    print(f"🔢 Processing: {model_id} - Prompt {prompt_index}")
    
    response = await call_math_agent(session, prompt_text, model_id)
    filepath, prompt_text, correct_answer = save_math_output(model_id, prompt_data, response, timestamp, prompt_index)
    
    print(f"  ✅ Math response saved: {filepath}")
    
    return (model_id, prompt_index, prompt_data, response, filepath, prompt_text, correct_answer)

async def async_pipeline_test():
    """Run async pipeline test with immediate comparison processing"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("🚀 Starting Async Pipeline Test")
    print(f"Available math models: {len(MODEL_IDS)}")
    print(f"Available compare models: {len(MODEL_IDS)}")
    print(f"Test prompts: {len(TEST_PROMPTS)}")
    print("-" * 60)
    
    all_results = []
    all_comparison_results = []
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
        # Create all math processing tasks
        math_tasks = []
        for model_id in MODEL_IDS:
            for i, prompt_data in enumerate(TEST_PROMPTS, 1):
                task = process_math_request(session, model_id, prompt_data, i, timestamp)
                math_tasks.append(task)
        
        # Process math requests and immediately start comparisons as they complete
        async def process_pipeline():
            comparison_tasks = []
            
            # Process math requests as they complete
            for completed_task in asyncio.as_completed(math_tasks):
                try:
                    # Get the completed math result
                    math_result = await completed_task
                    all_results.append(math_result)
                    
                    # IMMEDIATELY start comparison processing for this result
                    comparison_task = process_comparison_for_response(session, math_result, timestamp, MODEL_IDS)
                    comparison_tasks.append(comparison_task)
                    
                    print(f"🔀 Math complete → Starting comparisons for {math_result[0]} - Prompt {math_result[1]}")
                    
                except Exception as e:
                    print(f"Error in math processing: {e}")
            
            # Wait for all comparison tasks to complete
            print(f"\n⏳ Waiting for all {len(comparison_tasks)} comparison batches to complete...")
            comparison_results = await asyncio.gather(*comparison_tasks, return_exceptions=True)
            
            # Flatten results
            for batch in comparison_results:
                if not isinstance(batch, Exception):
                    all_comparison_results.extend([r for r in batch if not isinstance(r, Exception)])
            
            return all_comparison_results
        
        # Run the pipeline
        await process_pipeline()
    
    # Save summary
    summary_file = f"../math_output/async_summary_{timestamp}.json"
    with open(summary_file, "w") as f:
        json.dump([{
            "model_id": r[0],
            "prompt_index": r[1],
            "prompt": r[2],
            "response": r[3],
            "file": r[4]
        } for r in all_results], f, indent=2)
    
    comparison_summary_file = f"../compare_output/async_comparison_summary_{timestamp}.json"
    with open(comparison_summary_file, "w") as f:
        json.dump(all_comparison_results, f, indent=2)
    
    print(f"\n🏁 Async Pipeline completed!")
    print(f"Math responses processed: {len(all_results)}")
    print(f"Comparison responses processed: {len(all_comparison_results)}")
    print(f"Math summary saved to: {summary_file}")
    print(f"Comparison summary saved to: {comparison_summary_file}")
    print(f"Results organized by prompt in math_output/ and compare_output/ folders")

if __name__ == "__main__":
    print("Async Pipeline Test")
    print("Make sure both agents are running:")
    print("- Math agent on http://127.0.0.1:8080")
    print("- Compare models agent on http://127.0.0.1:8081")
    
    try:
        asyncio.run(async_pipeline_test())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nError during testing: {e}")