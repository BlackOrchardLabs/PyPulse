"""
PyPulse Example: Machine Learning Training Pipeline
Demonstrates PyPulse with ML model training workflow
"""

import time
import random
import math
from pypulse import pulse_progress, pulse_task

class MockModel:
    """Mock machine learning model for demonstration"""
    
    def __init__(self):
        self.weights = [random.uniform(-1, 1) for _ in range(10)]
        self.bias = random.uniform(-1, 1)
        self.training_history = {"loss": [], "accuracy": []}
    
    def train_batch(self, batch_data):
        """Simulate training on a batch"""
        time.sleep(0.1)  # Simulate computation
        
        # Simulate loss calculation and weight updates
        mock_loss = random.uniform(0.1, 2.0)
        mock_accuracy = random.uniform(0.7, 0.95)
        
        # Simulate gradient descent
        for i in range(len(self.weights)):
            self.weights[i] -= random.uniform(-0.1, 0.1)
        
        self.bias -= random.uniform(-0.01, 0.01)
        
        return mock_loss, mock_accuracy
    
    def evaluate(self, test_data):
        """Simulate model evaluation"""
        time.sleep(0.5)  # Simulate evaluation
        
        metrics = {
            "accuracy": random.uniform(0.85, 0.98),
            "precision": random.uniform(0.80, 0.95),
            "recall": random.uniform(0.75, 0.92),
            "f1_score": random.uniform(0.78, 0.94)
        }
        
        return metrics

def simulate_ml_training():
    """Simulate a complete machine learning training pipeline"""
    
    print("Starting ML Training Pipeline...")
    
    # Configuration
    config = {
        "num_samples": 10000,
        "num_features": 20,
        "batch_size": 64,
        "num_epochs": 10,
        "validation_split": 0.2,
        "learning_rate": 0.001
    }
    
    with pulse_task("ML Training Pipeline", total_steps=8) as task:
        
        # Step 1: Data Generation
        task.step("Generating synthetic dataset", progress=0.05)
        
        # Simulate dataset generation
        dataset = []
        for i in pulse_progress(range(config["num_samples"]), 
                               task="Generating samples", 
                               step="1/8"):
            time.sleep(0.0005)  # Simulate data generation
            
            sample = {
                "features": [random.uniform(-1, 1) for _ in range(config["num_features"])],
                "label": random.choice([0, 1]),
                "sample_id": i
            }
            dataset.append(sample)
        
        # Step 2: Data Preprocessing
        task.step("Preprocessing dataset", progress=0.15)
        
        preprocessing_steps = [
            "Normalizing features",
            "Handling missing values", 
            "Feature scaling",
            "Data augmentation",
            "Creating validation split"
        ]
        
        for step_name in pulse_progress(preprocessing_steps, 
                                       task="Preprocessing steps", 
                                       step="2/8"):
            time.sleep(0.3)
            # Simulate preprocessing work
            if "normalizing" in step_name.lower():
                # Simulate feature normalization
                for sample in dataset[:100]:  # Just a subset for demo
                    sample["features"] = [f * 0.5 for f in sample["features"]]
        
        # Step 3: Model Architecture Design
        task.step("Designing model architecture", progress=0.25)
        
        # Simulate model design process
        design_steps = [
            "Defining input layer",
            "Adding hidden layers",
            "Configuring activation functions",
            "Setting up output layer",
            "Compiling model"
        ]
        
        model_architecture = {}
        for step in pulse_progress(design_steps, 
                                  task="Architecture design", 
                                  step="3/8"):
            time.sleep(0.4)
            model_architecture[step] = f"configured_{step.replace(' ', '_').lower()}"
        
        # Initialize model
        model = MockModel()
        
        # Step 4: Model Training
        task.step("Training model", progress=0.4)
        
        # Calculate training parameters
        num_batches = len(dataset) // config["batch_size"]
        
        for epoch in pulse_progress(range(config["num_epochs"]), 
                                   task="Training epochs", 
                                   step="4/8"):
            
            epoch_loss = 0
            epoch_accuracy = 0
            
            # Process batches
            for batch_num in pulse_progress(range(num_batches), 
                                           task=f"Epoch {epoch+1}/{config['num_epochs']}",
                                           leave=False):
                
                # Get batch data
                start_idx = batch_num * config["batch_size"]
                end_idx = min(start_idx + config["batch_size"], len(dataset))
                batch_data = dataset[start_idx:end_idx]
                
                # Train on batch
                loss, accuracy = model.train_batch(batch_data)
                epoch_loss += loss
                epoch_accuracy += accuracy
            
            # Record epoch metrics
            avg_loss = epoch_loss / num_batches
            avg_accuracy = epoch_accuracy / num_batches
            model.training_history["loss"].append(avg_loss)
            model.training_history["accuracy"].append(avg_accuracy)
            
            # Simulate validation
            time.sleep(0.2)
        
        # Step 5: Model Evaluation
        task.step("Evaluating trained model", progress=0.7)
        
        # Simulate test dataset
        test_dataset = dataset[:len(dataset)//4]  # 25% for testing
        
        evaluation_metrics = model.evaluate(test_dataset)
        
        # Additional evaluation steps
        evaluation_steps = [
            "Confusion matrix analysis",
            "ROC curve generation",
            "Feature importance analysis",
            "Error analysis"
        ]
        
        for eval_step in pulse_progress(evaluation_steps, 
                                       task="Evaluation steps", 
                                       step="5/8"):
            time.sleep(0.6)
        
        # Step 6: Hyperparameter Tuning
        task.step("Hyperparameter optimization", progress=0.8)
        
        # Simulate hyperparameter search
        hyperparameters = [
            {"lr": 0.01, "batch_size": 32},
            {"lr": 0.001, "batch_size": 64},
            {"lr": 0.0001, "batch_size": 128},
            {"lr": 0.005, "batch_size": 32},
            {"lr": 0.002, "batch_size": 64}
        ]
        
        tuning_results = []
        for params in pulse_progress(hyperparameters, 
                                    task="Parameter combinations", 
                                    step="6/8"):
            time.sleep(1.5)  # Simulate training with different params
            
            # Simulate performance evaluation
            performance = random.uniform(0.85, 0.95)
            tuning_results.append({
                "params": params,
                "performance": performance
            })
        
        # Step 7: Model Interpretation
        task.step("Generating model explanations", progress=0.9)
        
        interpretation_methods = [
            "SHAP values calculation",
            "LIME explanations",
            "Attention visualization",
            "Feature importance ranking",
            "Decision boundary analysis"
        ]
        
        interpretations = {}
        for method in pulse_progress(interpretation_methods, 
                                    task="Interpretation methods", 
                                    step="7/8"):
            time.sleep(0.8)
            interpretations[method] = f"generated_{method.replace(' ', '_').lower()}"
        
        # Step 8: Save Model and Results
        task.step("Saving model and results", progress=0.98)
        
        # Simulate saving various artifacts
        artifacts = [
            "trained_model.pkl",
            "training_history.json",
            "evaluation_metrics.json",
            "hyperparameter_results.json",
            "model_interpretations.json",
            "deployment_config.yaml"
        ]
        
        for artifact in pulse_progress(artifacts, 
                                      task="Saving artifacts", 
                                      step="8/8"):
            time.sleep(0.4)
        
        # Final update
        task.step("ML Pipeline complete!", progress=1.0)
        time.sleep(1)
    
    # Print comprehensive results
    print("\n" + "="*80)
    print("MACHINE LEARNING PIPELINE RESULTS")
    print("="*80)
    
    print(f"\nDataset Statistics:")
    print(f"  Total samples: {len(dataset):,}")
    print(f"  Features per sample: {config['num_features']}")
    print(f"  Training batches: {num_batches}")
    print(f"  Batch size: {config['batch_size']}")
    
    print(f"\nTraining Results:")
    final_loss = model.training_history["loss"][-1]
    final_accuracy = model.training_history["accuracy"][-1]
    print(f"  Final loss: {final_loss:.4f}")
    print(f"  Final accuracy: {final_accuracy:.2%}")
    print(f"  Best accuracy: {max(model.training_history['accuracy']):.2%}")
    
    print(f"\nEvaluation Metrics:")
    for metric, value in evaluation_metrics.items():
        print(f"  {metric}: {value:.3f}")
    
    print(f"\nHyperparameter Tuning:")
    best_params = max(tuning_results, key=lambda x: x["performance"])
    print(f"  Best performance: {best_params['performance']:.3f}")
    print(f"  Best parameters: {best_params['params']}")
    
    print(f"\nGenerated Artifacts:")
    for artifact in artifacts:
        print(f"  ✓ {artifact}")
    
    print("="*80)

def simulate_model_comparison():
    """Simulate comparing multiple ML models"""
    
    print("\nStarting Model Comparison...")
    
    models = ["Random Forest", "SVM", "Neural Network", "Gradient Boosting"]
    
    with pulse_task("Model Comparison", total_steps=len(models)) as task:
        
        comparison_results = {}
        
        for i, model_name in enumerate(pulse_progress(models, task="Training models")):
            task.step(f"Training {model_name}", progress=(i + 1) / len(models))
            
            # Simulate model training
            training_time = random.uniform(2, 8)
            time.sleep(training_time)
            
            # Simulate performance metrics
            comparison_results[model_name] = {
                "accuracy": random.uniform(0.80, 0.95),
                "training_time": training_time,
                "inference_speed": random.uniform(100, 1000),
                "memory_usage": random.uniform(50, 500)
            }
        
        task.step("Model comparison complete!", progress=1.0)
    
    # Print comparison results
    print("\nModel Comparison Results:")
    print("-" * 60)
    print(f"{'Model':<20} {'Accuracy':<10} {'Train Time':<12} {'Inference':<12}")
    print("-" * 60)
    
    for model, metrics in comparison_results.items():
        print(f"{model:<20} {metrics['accuracy']:.3f}    {metrics['training_time']:.1f}s        {metrics['inference_speed']:.0f} req/s")
    
    # Find best model
    best_model = max(comparison_results.keys(), 
                    key=lambda x: comparison_results[x]["accuracy"])
    print(f"\n🏆 Best performing model: {best_model}")

if __name__ == "__main__":
    # Run the ML pipeline simulation
    simulate_ml_training()
    
    # Run model comparison
    simulate_model_comparison()
    
    print("\n🎉 All ML simulations completed successfully!")
    print("This demonstrates how PyPulse can track complex ML workflows with nested progress indicators.")