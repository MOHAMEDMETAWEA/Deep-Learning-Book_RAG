# 🤖 DEPI: Generative & Agentic AI Professional 🚀

Welcome to the comprehensive repository for the **Generative & Agentic AI Professional** track. This repository serves as a centralized hub for all labs, projects, and practical assignments throughout this 120-hour intensive program.

---

## 🛤️ Course Journey & Syllabus

This track is designed to take a practitioner from the foundations of Machine Learning to the cutting edge of Autonomous Agents and Multi-Agent Systems. Below is the complete roadmap of the curriculum.

### 🗺️ Curriculum Roadmap

| Module | Focus Area | Status |
| :--- | :--- | :--- |
| **01 Intro & Orientation** | Environment setup, Ethics, & AI Landscape | ✅ Complete |
| **02 ML Fundamentals** | Regression, Classification, & Evaluation Metrics | ✅ Complete |
| **03 Deep Learning & Transformers** | CNNs, RNNs, LSTMs, & Transformer Architectures | ✅ Complete |
| **04 Generative AI Fundamentals** | VAEs, GANs, Diffusion Models, & Fine-tuning (LoRA) | ✅ Complete |
| **05 Advanced Prompting** | Chain-of-Thought, Reasoning, & Function Calling | ✅ Complete |
| **06 Agentic AI Fundamentals** | Autonomous Agents, Planning, & Tool Use | ✅ Complete |
| **07 RAG & Memory Systems** | Fusion, Re-ranking, & Memory Augmented Models | 🔄 In Progress |
| **08 Advanced RAG Systems** | Semantic Cache, GraphRAG, & Agentic RAG | ⏳ Upcoming |
| **09 Deployment & Monitoring** | Scaling, API Integration, & Cost Optimization | 🔄 In Progress |
| **10 Governance & Capstone** | Industry Trends & Final Project Implementation | ⏳ Upcoming |

---

## 📁 Repository Structure

The labs and projects are organized by module following the course progression:

### 🧠 Core Modules

- **`M2 ML Fundamentals`**:
  - Implementation of core supervised and unsupervised algorithms.
  - Labs covering regression, classification, and clustering.
- **`M3 Deep Learning & Transformers`**:
  - Journey from basic Neural Networks to Transformers.
  - Sessions on Computer Vision (CNNs) and NLP (RNNs, LSTMs).
  - Deep dive into Transformer architectures (BERT, GPT).
- **`M4 Generative AI Fundamentals`**:
  - **VAEs**: Variational Autoencoders for latent space representation.
  - **GANs**: Generative Adversarial Networks for image generation.
  - **Diffusion Models**: Noise prediction and reverse diffusion processes.
  - **LoRA**: Parameter-efficient fine-tuning for Stable Diffusion.
- **`M5 Prompt Eng`**:
  - **Microsoft Phi-3.5**: Benchmarks and instruction tuning.
  - **Function Calling**: Implementing decision engines for tickets and legal contracts.
  - **Reasoning Patterns**: Chain-of-Thought and multi-step reasoning.
- **`M6 Agentic`**:
  - **S1–S2 Core Agent Patterns**: Orchestration, stateful agents, interactive loops, and Code-Acting (LLM-generated pandas).
    - 📓 `Lab1_Safe_Sales_Insights_Agent.ipynb` — Decision-Driven Code-Acting Agent with policy enforcement, AST sandbox, and 6-query test suite.
  - **S3 Self-Correction**: Implementing agents that can reflect and fix their own errors.
    - 📓 `Lab2_Policy_Aware_Self_Correcting_Agent.ipynb` — **Advanced production-hardened agent** featuring auto-repair (5 retries), schema mapping (synonyms + fuzzy), ambiguity handling, and a full evaluation harness with 14 red-team attacks.
    - 📄 `Lab2_Documentation.md` — Detailed technical documentation on pipeline architecture, security rules, and metrics.
- **`M7 RAG_Retrieval Augmented Generation`**:
  - **Part 1 — Policy Decision Agent**: Managing data access and authorization logic within retrieval contexts.
  - **Part 2 — RAG Foundation**: Core implementation of vector-based retrieval and generation augmenting.

### 🌐 Integration & Deployment

- **`Hugging Face & FastAPI`**:
  - Connecting models to web interfaces using Gradio.
  - Building scalable APIs with FastAPI to serve ML models.

---

## 🛠️ Key Learning Outcomes & Features

- **🧠 Foundational Mastery:** Solid understanding of ML/DL architectures from basic regression to complex Transformers.
- **🎨 Generative Excellence:** Hands-on experience with VAEs, GANs, and Diffusion models, including LoRA fine-tuning for specialized image generation.
- **🎯 Advanced Prompting:** Mastering Microsoft Phi-3.5 for reasoning-driven workflows, Chain-of-Thought prompting, and structured function calling.
- **🤖 Agentic Autonomy:** Designing autonomous agents capable of independent planning, multi-step execution, and complex tool interaction.
- **🛡️ Security & Governance:** Implementing deterministic policy enforcement and AST-based Python sandboxes to prevent data leaks and unauthorized system access.
- **🛠️ Self-Correction & Reliability:** Advanced reflection loops for autonomous code repair, schema mapping (synonyms/fuzzy matching) for robust natural language interaction, and comprehensive evaluation harnesses (red-teaming) for production-grade verification.
- **🏗️ RAG Architectures:** Understanding and implementing Retrieval-Augmented Generation to ground LLMs in external knowledge with verified policies.
- **🌐 Production Readiness:** Building scalable APIs with FastAPI and deploying models to local and cloud environments (Docker, Hugging Face).

---

## 🧰 Tech Stack

- **Frameworks:** `TensorFlow`, `PyTorch`, `Keras`, `JAX`
- **Generative AI:** `Hugging Face (Transformers, Diffusers, Accelerate)`, `OpenAI API`, `Microsoft Phi-3.5`, `BitsAndBytes (4-bit Quantization)`
- **Deployment:** `FastAPI`, `Gradio`, `Uvicorn`, `Docker`
- **Data & Reasoning:** `LangChain`, `NumPy`, `Pandas`, `Scikit-learn`, `Matplotlib`, `AST (Abstract Syntax Trees)`, `Difflib (Fuzzy Matching)`

---

## 🚀 How to Use

As this is a journey, the notebooks are designed to be self-contained within their respective folders.

1. **Explore Modules:** Navigate to the folder of interest.
2. **Setup Environment:** Each module may have specific requirements. A general environment with `jupyter`, `torch`/`tensorflow`, and `transformers` is recommended.
3. **Run Labs:** Open the `.ipynb` files to see implementations and complete the practical assignments.

---

## 🌟 Acknowledgments

This journey is part of the **DEPI (Digital Egypt Pioneers Initiative)**. Special thanks to the instructors and the community for the continuous support.

---
*Stay tuned as we continue to build more intelligent agents!* 🏗️🤖
