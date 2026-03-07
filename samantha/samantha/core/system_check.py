"""System diagnostics and health checks"""

import subprocess
import requests
import os

def check_gpu():
    """Get GPU information"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,name,temperature.gpu,memory.used,memory.total,utilization.gpu', 
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=5
        )
        
        gpus = []
        for line in result.stdout.strip().split('\n'):
            if line and ',' in line:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 6:
                    gpus.append({
                        'index': parts[0],
                        'name': parts[1],
                        'temp': parts[2],
                        'mem_used': int(parts[3]),
                        'mem_total': int(parts[4]),
                        'util': parts[5]
                    })
        return gpus
    except:
        return []

def check_service(port, endpoint='/', timeout=2):
    """Check if service is running"""
    try:
        response = requests.get(f'http://localhost:{port}{endpoint}', timeout=timeout)
        return response.status_code < 500
    except:
        return False

def run_diagnostics():
    """Run full system diagnostics"""
    checks = {
        'ollama': check_service(11434, '/api/tags'),
        'comfyui': check_service(8188, '/system_stats'),
        'gpus_available': len(check_gpu()) > 0
    }
    
    return {
        'healthy': all(checks.values()),
        'checks': checks,
        'gpus': check_gpu()
    }
