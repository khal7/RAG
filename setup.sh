#!/bin/zsh

mkdir -p "$HOME/goinfre/rag/uv_cache"
mkdir -p "$HOME/goinfre/rag/huggingface"
mkdir -p "$HOME/goinfre/rag/venv"

export UV_CACHE_DIR="$HOME/goinfre/rag/uv_cache"
export HF_HOME="$HOME/goinfre/rag/huggingface"
export UV_PROJECT_ENVIRONMENT="$HOME/goinfre/rag/venv"