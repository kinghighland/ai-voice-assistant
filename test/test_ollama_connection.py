#!/usr/bin/env python3
import ollama

def test_ollama_connection():
    try:
        print("Testing Ollama connection...")
        
        # Test 1: List models
        print("1. Listing available models...")
        models = ollama.list()
        print(f"Available models: {[model['name'] for model in models['models']]}")
        
        # Test 2: Try to generate with minicpm-v
        print("\n2. Testing generation with minicpm-v:latest...")
        response = ollama.generate(
            model='minicpm-v:latest',
            prompt='Hello, please respond in Chinese'
        )
        print(f"Response: {response['response']}")
        
        print("\n✅ Ollama connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    test_ollama_connection()