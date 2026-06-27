# 🚀 IntelliBench-LLM

<div align="center">

### AI-Powered Large Language Model Benchmarking & Performance Prediction Platform

Predict • Benchmark • Recommend • Analyze

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-F7931E?style=for-the-badge\&logo=scikitlearn\&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Desktop-41CD52?style=for-the-badge\&logo=qt\&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

</div>

---

# 📖 Overview

**IntelliBench-LLM** is a Machine Learning-powered benchmarking platform that predicts the performance of Large Language Models (LLMs) using hardware specifications instead of requiring every model to be executed.

The project integrates **Hardware Analysis**, **Machine Learning**, **Benchmark Testing**, and an **Intelligent Recommendation Engine** into a unified desktop application, enabling users to estimate model performance efficiently.

---

# 🎯 Objectives

* Predict LLM performance using Machine Learning.
* Analyze hardware capabilities automatically.
* Recommend the most suitable LLM.
* Reduce benchmarking time.
* Visualize system performance.
* Provide an easy-to-use desktop interface.

---

# ✨ Key Features

### 🖥️ Hardware Analysis

* CPU Detection
* RAM Detection
* GPU Detection
* VRAM Detection
* Storage Information
* Operating System Detection

---

### 🤖 Machine Learning Prediction

Predicts:

* Performance Score
* Tokens per Second
* Expected Latency
* Memory Usage
* Compatibility Rating

---

### 🧠 Intelligent Recommendation Engine

Recommends the best LLM according to:

* CPU Performance
* RAM
* GPU VRAM
* Storage
* Benchmark Score

Supports models such as:

* Llama 3
* Mistral
* Gemma
* Phi-3
* TinyLlama
* DeepSeek
* Qwen

---

### 📊 Benchmark Module

* Inference Time
* CPU Usage
* Memory Usage
* Response Speed
* Performance Rating

---

### 📂 Dataset Generation

Generate datasets containing:

* Hardware Features
* Performance Metrics
* Model Labels

Used for training predictive ML models.

---

### 📈 Machine Learning Pipeline

* Data Collection
* Data Cleaning
* Feature Engineering
* Model Training
* Model Evaluation
* Performance Prediction
* Recommendation

---

# 🧠 Architecture

```text
            Hardware Scan
                   │
                   ▼
         Feature Extraction
                   │
                   ▼
            ML Prediction
          ┌────────┴────────┐
          ▼                 ▼
Performance Score     LLM Recommendation
          │                 │
          └────────┬────────┘
                   ▼
          Benchmark Dashboard
```

---

# 📁 Project Structure

```text
IntelliBench-LLM
│
├── benchmark/
│
├── datasets/
│   ├── raw/
│   └── processed/
│
├── ml/
│   ├── train.py
│   ├── predictor.py
│   ├── preprocessing.py
│   └── dataset_generator.py
│
├── models/
│   ├── classifier.pkl
│   ├── regressor.pkl
│   └── metadata.pkl
│
├── recommender/
│
├── scanner/
│
├── ui/
│
├── assets/
│
├── main.py
│
├── requirements.txt
│
└── README.md
```

---

# 📊 Machine Learning Workflow

```text
Dataset
    │
    ▼
Data Cleaning
    │
    ▼
Feature Engineering
    │
    ▼
Train/Test Split
    │
    ▼
Random Forest Models
    │
    ▼
Prediction
    │
    ▼
Recommendation
```

---

# 🛠 Tech Stack

### Programming Language

* Python

### Machine Learning

* Scikit-Learn
* NumPy
* Pandas
* Joblib

### Desktop GUI

* PySide6

### Data Storage

* CSV
* JSON

### Version Control

* Git
* GitHub

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/raghavupadhyay308-svg/IntelliBench-LLM.git
```

Move into the project directory

```bash
cd IntelliBench-LLM
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python main.py
```

---

# 📊 Applications

* LLM Performance Prediction
* AI Hardware Planning
* Benchmark Automation
* Educational Demonstrations
* Machine Learning Research
* Performance Optimization

---

# 📈 Current ML Models

| Model                    | Purpose                   |
| ------------------------ | ------------------------- |
| Random Forest Regressor  | Predict Performance Score |
| Random Forest Classifier | Recommend Best LLM        |

---

# 🔮 Future Improvements

* XGBoost Integration
* CatBoost Models
* Neural Networks
* AutoML Pipeline
* Live GPU Monitoring
* Cloud Benchmarking
* Docker Deployment
* Web Dashboard
* Multi-GPU Support

---

# 📚 Learning Outcomes

This project demonstrates:

* Machine Learning Pipeline Development
* Feature Engineering
* Regression & Classification
* Model Evaluation
* Desktop GUI Development
* System Benchmarking
* Data Processing
* Software Engineering Best Practices

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push to your branch.
5. Open a Pull Request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

## Raghav Upadhyay

**B.Tech – Artificial Intelligence & Machine Learning**

Graphic Era Hill University, Dehradun

**GitHub:** https://github.com/raghavupadhyay308-svg

---

<div align="center">

### ⭐ If you found this project useful, please consider giving it a Star.

**Built with ❤️ using Python, Machine Learning, and Artificial Intelligence.**

</div>
