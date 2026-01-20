import requests
import re

# Test product 20 which has a 3D model
url = 'http://127.0.0.1:8000/product_item/20/'
print(f'Testing: {url}')

try:
    response = requests.get(url, timeout=10)
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        # Check key elements
        checks = [
            ('Canvas element', 'model-3d-canvas'),
            ('Button element', 'toggle-3d-btn'),
            ('3D model URL', '3d_models'),
            ('Three.js script', 'three.min.js'),
            ('GLTFLoader script', 'GLTFLoader.js'),
        ]
        
        for name, pattern in checks:
            if pattern in response.text:
                print(f'✓ {name} found')
            else:
                print(f'✗ {name} NOT found')
        
        # Extract model URL if present
        matches = re.findall(r'3d_models/[^"\\s<]*', response.text)
        if matches:
            print(f'\nModel paths found:')
            for match in matches[:5]:
                print(f'  - {match}')
                
        # Check the modelURL variable
        match = re.search(r"modelURL = '([^']*)'", response.text)
        if match:
            print(f'\nmodelURL JS variable: {match.group(1)}')
        else:
            print('\nmodelURL JS variable: NOT FOUND')
    else:
        print(f'Error: {response.status_code}')
        print(response.text[:500])
        
except Exception as e:
    print(f'Error: {e}')
