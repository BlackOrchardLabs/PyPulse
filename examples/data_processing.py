"""
PyPulse Example: Data Processing Pipeline
Demonstrates real-world usage with data analysis workflow
"""

import time
import random
import json
from pathlib import Path
from pypulse import pulse_progress, pulse_task

def simulate_data_processing():
    """Simulate a real data processing pipeline"""
    
    print("Starting data processing pipeline...")
    
    # Simulate loading configuration
    config = {
        "dataset_size": 1000,
        "batch_size": 50,
        "num_epochs": 5,
        "validation_split": 0.2
    }
    
    with pulse_task("Data Processing Pipeline", total_steps=6) as task:
        
        # Step 1: Load raw data
        task.step("Loading raw dataset", progress=0.1)
        raw_data = []
        for i in pulse_progress(range(config["dataset_size"]), 
                               task="Loading data", 
                               step="1/6"):
            # Simulate data loading
            time.sleep(0.002)
            raw_data.append({
                "id": i,
                "value": random.uniform(0, 100),
                "category": random.choice(["A", "B", "C"])
            })
        
        # Step 2: Data cleaning
        task.step("Cleaning and preprocessing", progress=0.25)
        cleaned_data = []
        for item in pulse_progress(raw_data, 
                                  task="Cleaning data", 
                                  step="2/6"):
            # Simulate cleaning
            time.sleep(0.001)
            if item["value"] > 10:  # Remove outliers
                cleaned_data.append(item)
        
        # Step 3: Feature engineering
        task.step("Engineering features", progress=0.4)
        features = []
        for item in pulse_progress(cleaned_data, 
                                  task="Feature engineering", 
                                  step="3/6"):
            time.sleep(0.003)
            features.append({
                "id": item["id"],
                "value": item["value"],
                "category": item["category"],
                "value_squared": item["value"] ** 2,
                "log_value": max(0, item["value"]) + 1
            })
        
        # Step 4: Train model (simulated)
        task.step("Training ML model", progress=0.6)
        model_metrics = {"accuracy": [], "loss": []}
        
        for epoch in pulse_progress(range(config["num_epochs"]), 
                                   task="Training epochs", 
                                   step="4/6"):
            # Simulate training
            time.sleep(1)
            
            # Simulate batch processing
            num_batches = len(features) // config["batch_size"]
            for batch in pulse_progress(range(num_batches), 
                                       task=f"Epoch {epoch+1} batches",
                                       leave=False):
                time.sleep(0.05)
            
            # Simulate metrics
            accuracy = 0.7 + (epoch * 0.05) + random.uniform(-0.02, 0.02)
            loss = 0.5 - (epoch * 0.08) + random.uniform(-0.01, 0.01)
            model_metrics["accuracy"].append(accuracy)
            model_metrics["loss"].append(loss)
        
        # Step 5: Validation
        task.step("Validating model", progress=0.8)
        validation_results = {}
        
        validation_steps = ["Splitting data", "Running predictions", "Calculating metrics"]
        for i, step_name in enumerate(pulse_progress(validation_steps, 
                                                    task="Validation steps", 
                                                    step="5/6")):
            time.sleep(0.8)
            validation_results[step_name] = random.uniform(0.8, 0.95)
        
        # Step 6: Save results
        task.step("Saving results", progress=0.95)
        
        # Simulate saving various outputs
        outputs = [
            "model_weights.pkl",
            "training_history.json", 
            "validation_report.csv",
            "feature_importance.png"
        ]
        
        for output in pulse_progress(outputs, 
                                    task="Saving outputs", 
                                    step="6/6"):
            time.sleep(0.3)
            # Simulate file saving
            output_path = Path(f"output_{output}")
            if output.endswith('.json'):
                with open(output_path, 'w') as f:
                    json.dump(model_metrics, f, indent=2)
            else:
                output_path.touch()
        
        # Final update
        task.step("Pipeline complete!", progress=1.0)
        time.sleep(0.5)
    
    print("Data processing pipeline completed successfully!")
    print(f"Processed {len(features)} records across {config['num_epochs']} epochs")
    print(f"Final accuracy: {model_metrics['accuracy'][-1]:.3f}")

if __name__ == "__main__":
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Run the simulation
    simulate_data_processing()
    
    print(f"\nCheck the '{output_dir}' directory for generated files!")
    print("Note: This is a simulation - no actual ML models were trained.")