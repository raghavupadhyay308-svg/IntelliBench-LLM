🚀 LLM-Bench-AI
AI-Powered Large Language Model Benchmarking & Recommendation System

An intelligent Machine Learning system that predicts the inference performance of Large Language Models (LLMs) on different hardware configurations and recommends the most suitable model based on available system resources.

Unlike traditional benchmarking tools that rely solely on real-time execution, LLM-Bench-AI combines hardware analysis, ML prediction, benchmark testing, and intelligent recommendation into a single application.

Project Preview
System Scan
      │
      ▼
Hardware Features
      │
      ▼
Machine Learning Model
      │
      ├───────────────┐
      ▼               ▼
Performance      Best LLM
Prediction      Recommendation
      │
      ▼
Benchmark Results
Features
Hardware Detection
Automatic CPU Detection
RAM Analysis
GPU Memory Detection
Storage Information
Operating System Detection
Machine Learning Prediction

Predicts

Expected Tokens/Second
Estimated Latency
Expected Memory Usage
Overall Performance Score
Intelligent Recommendation Engine

Recommends

TinyLlama
Phi-3
Gemma
Llama 3
Mistral
DeepSeek
Qwen

Based on

Available RAM
CPU Performance
GPU VRAM
Storage
Benchmark Module

Measures

Inference Speed
Execution Time
Resource Utilization
Memory Consumption
Dataset Generation

Synthetic dataset generator for

Hardware Specs
↓

Performance Labels
↓

Training Dataset
ML Model Training

Includes

Classification Model
Regression Model
Feature Engineering
Data Preprocessing
Model Serialization
Desktop GUI

Built using

PySide6
Modern Interface
Multi-page Navigation
Interactive Results
Machine Learning Workflow
Dataset
      │
      ▼
Cleaning
      │
      ▼
Feature Engineering
      │
      ▼
Train/Test Split
      │
      ▼
Regression Model
      │
      ▼
Performance Prediction

----------------------------

Dataset
      │
      ▼
Classification
      │
      ▼
Best LLM Recommendation
ML Algorithms

Current implementation

✅ Random Forest Regressor

✅ Random Forest Classifier

Future Improvements

XGBoost
LightGBM
CatBoost
Neural Networks
Tech Stack
Machine Learning
Python
Scikit-Learn
NumPy
Pandas
Joblib
Desktop
PySide6
Data
JSON
CSV
Visualization
Matplotlib (Future)
Folder Structure
LLM-Bench-AI

│
├── benchmark/
│      inference_test.py
│
├── data/
│      models_db.json
│
├── ml/
│      train.py
│      predictor.py
│      generate_dataset.py
│      dataset.csv
│
├── models/
│      classifier.pkl
│      regressor.pkl
│      meta.pkl
│
├── recommender/
│      model_recommender.py
│
├── scanner/
│      system_scan.py
│
├── ui/
│      benchmark_page.py
│      results_page.py
│      scan_page.py
│
├── requirements.txt
│
└── main.py
Machine Learning Pipeline
System Scan

↓

Feature Extraction

↓

Preprocessing

↓

Regression Prediction

↓

Classification

↓

Model Recommendation

↓

Benchmark Validation
Future Scope
Deep Learning Prediction
GPU Benchmark Dataset
Cloud Deployment
Auto Dataset Collection
Reinforcement Learning Recommendation
LLM Fine-tuning Support
Multi-GPU Support
Cross-platform Benchmarking
Research Applications
AI Infrastructure Planning
Hardware Compatibility Analysis
Edge AI Deployment
LLM Performance Prediction
Educational ML Demonstrations
Results

The ML model predicts

Performance Score
Expected Inference Speed
Memory Requirement
Best LLM Selection

without running every model, significantly reducing benchmarking time.

Installation
git clone https://github.com/yourusername/LLM-Bench-AI.git

cd LLM-Bench-AI

pip install -r requirements.txt

python main.py
Requirements
Python 3.11+

PySide6

Scikit-Learn

NumPy

Pandas

Joblib
Author

Raghav Upadhyay

B.Tech Artificial Intelligence & Machine Learning

Graphic Era Hill University

Resume Project Description

LLM-Bench-AI | Machine Learning Performance Prediction System

Developed an AI-powered benchmarking system that predicts Large Language Model (LLM) inference performance using Machine Learning.
Built regression and classification models to estimate execution speed, memory usage, and recommend optimal LLMs based on hardware specifications.
Implemented automated hardware scanning, feature engineering, benchmark evaluation, and a PySide6 desktop interface for real-time predictions.
Tech Stack: Python, Scikit-Learn, Pandas, NumPy, PySide6, Joblib, JSON.
