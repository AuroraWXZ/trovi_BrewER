
import os
import sys
import pandas as pd
import pollock.metrics as metrics
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError
import contextlib

# Configuration
DATASET = "survey_sample"
SUT = "sqlite"
CLEAN_DIR = f"{DATASET}/clean"
LOADED_DIR = f"results/{SUT}/{DATASET}/loading"

def evaluate_single_file_silent(filename):
    """Calculates F1 scores for a single file, silencing stdout/stderr."""
    with open(os.devnull, "w") as devnull:
        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
            clean_path = os.path.join(CLEAN_DIR, filename)
            loaded_path = os.path.join(LOADED_DIR, filename + "_converted.csv")
            
            row = {"file": filename, "success": 0, "header_f1": 0, "record_f1": 0, "cell_f1": 0}
            try:
                if os.path.exists(loaded_path) and os.path.getsize(loaded_path) > 0:
                    if metrics.successful_csv(loaded_path):
                        row["success"] = 1
                        # Exact same math as the original paper:
                        res = metrics.header_record_cell_measures_csv(clean_path, loaded_path, 1)
                        row["header_f1"] = res[2]
                        row["record_f1"] = res[5]
                        row["cell_f1"] = res[8]
            except:
                pass
            return row

if __name__ == "__main__":
    print(f"--- EVALUATING {SUT.upper()} ---", flush=True)

    if not os.path.exists(LOADED_DIR):
        print("Error: No results directory found!")
        exit(1)

    files = [f for f in os.listdir(CLEAN_DIR) if f.endswith(".csv")]
    
    # Use CPU count - 2 to prevent freezing the server
    safe_cores = max(1, (os.cpu_count() or 1) - 2)
    print(f"Processing {len(files)} files using {safe_cores} workers...", flush=True)
    
    results = []
    with ProcessPoolExecutor(max_workers=safe_cores) as executor:
        future_to_file = {executor.submit(evaluate_single_file_silent, f): f for f in files}
        
        try:
            # 60s timeout per file batch
            for i, future in enumerate(as_completed(future_to_file, timeout=60)):
                res = future.result()
                results.append(res)
                if i % 1 == 0: 
                    print(f"[{i+1}/{len(files)}] Processed...", flush=True)
                    
        except TimeoutError:
            print("\nTIMEOUT: Some workers took too long. Calculating partial results.")
            for fut in future_to_file: fut.cancel()

    if not results:
        print("Fatal Error: No files finished successfully.")
        exit(1)

    df = pd.DataFrame(results)

    # VIDEO-FRIENDLY OUTPUT FORMAT
    print("\n" + "="*40)
    print(f" FINAL SCORES: {SUT} on {DATASET}")
    print("="*40)
    print(f"Success Rate:  {df['success'].mean():.2%}")
    print(f"Header F1:     {df['header_f1'].mean():.4f}")
    print(f"Record F1:     {df['record_f1'].mean():.4f}")
    print(f"Cell F1:       {df['cell_f1'].mean():.4f}")
    print("="*40 + "\n")
