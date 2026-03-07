"""Configuration management for Samantha AI"""

import yaml
import os
from pathlib import Path

DEFAULT_CONFIG = {
    'version': '1.0.0',
    'system': {
        'gpus': {
            'chat': [2, 3],
            'image': [0],
            'video': [1],
            'training': [0]
        },
        'services': {
            'ollama_port': 11434,
            'comfyui_port': 8188,
            'web_port': 8501
        }
    },
    'models': {
        'llm': {
            'name': 'samantha-max',
            'context_length': 4096
        },
        'image': {
            'base': 'sd_xl_base_1.0.safetensors'
        },
        'video': {
            'fast': 'Wan2.2_TI2V_5B_fp16.safetensors',
            'quality': 'Wan2.2_I2V_A14B_fp16_fp16.safetensors'
        }
    },
    'paths': {
        'models': '/root/ai_system',
        'datasets': '/root/datasets',
        'outputs': '/root/outputs',
        'loras': '/root/ai_system/loras'
    },
    'features': {
        'nsfw': True,
        'code_execution': True,
        'web_browsing': True,
        'auto_update': False
    }
}

def load_config(config_path=None):
    """Load configuration from file or return defaults"""
    if config_path is None:
        config_path = '/opt/samantha/config/config.yaml'
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config
    except Exception as e:
        print(f"Config load error: {e}")
    
    return DEFAULT_CONFIG

def save_config(config, config_path=None):
    """Save configuration to file"""
    if config_path is None:
        config_path = '/opt/samantha/config/config.yaml'
    
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        print(f"Config save error: {e}")
        return False
