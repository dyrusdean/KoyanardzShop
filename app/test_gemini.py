#!/usr/bin/env python
"""
Test script to verify Gemini API key and connectivity
"""
import os
import json
import urllib.request
import urllib.error

def list_available_models(api_key):
    """List available models for the API key"""
    print("\n🔍 Checking available models...")
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        if 'models' in data:
            print("✅ Available models:")
            for model in data['models']:
                print(f"  - {model.get('name', 'Unknown')}")
            return data['models']
        else:
            print("⚠️ No models found in response")
            return []
            
    except urllib.error.HTTPError as e:
        print(f"Status Code: {e.code}")
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            print(f"Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
        except:
            pass
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_gemini_api():
    """Test Gemini API connection with the provided key"""
    # Read from .env file manually
    api_key = None
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    api_key = line.split('=')[1].strip()
                    break
    except:
        pass
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"Testing with API Key: {api_key[:20]}...")
    
    # First, list available models
    models = list_available_models(api_key)
    
    if not models:
        print("\n❌ No models available for your API key")
        return False
    
    # Filter for models that are likely to support generateContent (text chat)
    chat_models = [m for m in models if any(keyword in m.get('name', '') for keyword in ['gemini-2.5', 'gemini-2.0', 'gemini-pro', 'flash', 'pro-latest', 'flash-latest'])]
    
    if not chat_models:
        chat_models = models  # Fall back to trying all models
    
    print(f"\n🔍 Found {len(chat_models)} potential chat models. Testing...")
    
    for model_obj in chat_models[:3]:  # Test first 3
        test_model = model_obj.get('name', '').replace('models/', '')
        print(f"\nTesting {test_model}...")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{test_model}:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": "Hello, can you respond with a short greeting?"}]
                }
            ]
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method='POST'
            )
            
            response = urllib.request.urlopen(req, timeout=10)
            data = json.loads(response.read().decode('utf-8'))
            
            print(f"Status Code: 200")
            
            if data.get('candidates'):
                text = data['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ SUCCESS! Response: {text}")
                print(f"\nℹ️  Use this model in your code: {test_model}")
                return True
            else:
                print(f"⚠️ Empty response: {data}")
                
        except urllib.error.HTTPError as e:
            print(f"Status Code: {e.code}")
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                if 'error' in error_data:
                    error_msg = error_data['error'].get('message', 'Unknown error')
                    print(f"Error: {error_msg}")
            except:
                pass
                
        except urllib.error.URLError as e:
            print(f"❌ Connection failed: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("Gemini API Key Tester")
    print("=" * 60)
    
    success = test_gemini_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ API Key is working correctly!")
    else:
        print("❌ API Key is not working. Please check:")
        print("1. API key is valid and not expired")
        print("2. Enable 'Google AI for Developers API' in Google Cloud Console")
        print("3. Make sure billing is enabled on your Google Cloud project")
        print("4. Check that the API key has the right permissions")
    print("=" * 60)
