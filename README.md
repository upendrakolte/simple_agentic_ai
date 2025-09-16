# Simple Agentic AI Boilerplate

This repository provides a minimal boilerplate to help you get started with building agentic AI applications using LangGraph
, LangChain
, and OpenAI models
.

It demonstrates how to set up an agent loop where an LLM can:

Take user input

Decide whether to respond directly or call a tool

Use external tools (e.g., calculator, web search)

Return the final answer to the user

The included example agent comes with:

Calculator Tool → evaluates basic math expressions

Web Search Tool → searches the web via DuckDuckGo

Why this repo?

The goal is to provide a clean, lightweight starting point for developers who want to explore:

Building agent workflows

Connecting LLMs with tools

Creating state-based AI systems with LangGraph

This is not a production-ready framework, but a learning and prototyping boilerplate.

🚀 Getting Started

Install dependencies

pip install -r requirements.txt


Set your environment variables
Make sure you have an OpenAI API key available:

export OPENAI_API_KEY=your_key_here


Run the agent

python simple_agentic_ai.py

Example Interaction
You: What is 15 * 12?
Agent: 180

You: Search for latest AI news
Agent: [Web search results...]

⚠️ Disclaimer

The calculator_tool uses Python’s eval() — not safe for untrusted input. Replace it with a safer evaluator in production.

This is a toy example. Extend and adapt it for real-world projects.
