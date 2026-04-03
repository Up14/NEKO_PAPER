# NEKO
Network for Knowledge Organization (NEKO): a universal knowledge mining workflow
<img width="844" alt="NEKO logo and workflow" src="https://github.com/xiao-zhengyang/NEKO/assets/60377007/585dba65-1fa5-44da-b5d3-a608970112ac">

## Publication
If NEKO helps you, please cite us. 
[publication link]

## Applications in academic tasks
1. ✅Quickly learn about a research topic by searching Pubmed, arXiv, etc. and visualize the knowledge.
2. ✏️Write a review paper in a shorter time.
3. 🧪Plan and optimize experiments using knowledge in the past.

## LLM used
In general, NEKO works with any LLM. In this repo, we provide codes for GPT-4 and Qwen1.5.

You need OpenAI API key to use GPT-4. Qwen1.5 is open-source, and you need GPU to deploy Qwen locally.

## Prepare Python environment and download dependencies 
Please install latest Python.

For CUDA version newer than 12.0, run this command in CMD or bash to install dependencies. (You need to clone this repo and navigate to the folder on your disk)

```pip install -r requirements.txt```

For CUDA version 11.x, please use this command

```pip install -r requirements_cuda11.txt```

## Quick start

We provide jupyter notebooks for quick start. Please see Module 1 and Module 2.

We prepared some working examples as jupyter notebooks. If you have not setup LLM and wish to try NEKO, we also prepared some text data processed by LLM.

You can also chat with our NEKO helper on ChatGPT to get help! https://chat.openai.com/g/g-GME1vadzR-neko-helper
