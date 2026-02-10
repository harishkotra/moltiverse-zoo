#!/usr/bin/env python3
"""
Deploy a token on nad.fun using the 4-step flow from AGENTS.md
"""
import argparse
import json
import os
import sys
import requests
from pathlib import Path

# API endpoints from AGENTS.md
NADFUN_API = os.getenv("NADFUN_API_URL", "https://dev-api.nad.fun")

def upload_image(image_path: str) -> str:
    """Step 1: Upload image to nad.fun."""
    url = f"{NADFUN_API}/agent/token/image"
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(url, files=files)
        response.raise_for_status()
    
    data = response.json()
    return data['image_uri']

def upload_metadata(name: str, symbol: str, description: str, image_uri: str) -> str:
    """Step 2: Upload metadata to nad.fun."""
    url = f"{NADFUN_API}/agent/token/metadata"
    
    payload = {
        "name": name,
        "symbol": symbol,
        "description": description,
        "image": image_uri
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    data = response.json()
    return data['metadata_uri']

def mine_salt(target_pattern: str = "7777") -> dict:
    """Step 3: Mine salt for vanity address."""
    url = f"{NADFUN_API}/agent/salt"
    
    payload = {
        "pattern": target_pattern
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    data = response.json()
    return {
        "salt": data['salt'],
        "predicted_address": data['predicted_address']
    }

def deploy_token(metadata_uri: str, salt: str) -> dict:
    """Step 4: Deploy token on-chain via BondingCurveRouter."""
    # This would use web3.py to call BondingCurveRouter.create()
    # For now, return the info needed for on-chain deployment
    
    return {
        "status": "ready_for_deployment",
        "metadata_uri": metadata_uri,
        "salt": salt,
        "next_step": "Call BondingCurveRouter.create() with these params",
        "contract": "0x6F6B8F1a20703309951a5127c45B49b1CD981A22",
        "note": "Deploy fee: ~10 MON (check Curve.feeConfig()[0])"
    }

def main():
    parser = argparse.ArgumentParser(description="Deploy token on nad.fun")
    parser.add_argument("--name", required=True, help="Token name")
    parser.add_argument("--symbol", required=True, help="Token symbol")
    parser.add_argument("--image-path", required=True, help="Path to token image")
    parser.add_argument("--description", default="", help="Token description")
    parser.add_argument("--pattern", default="7777", help="Vanity address pattern")
    
    args = parser.parse_args()
    
    try:
        # Step 1: Upload image
        print("Step 1/4: Uploading image...", file=sys.stderr)
        image_uri = upload_image(args.image_path)
        print(f"✓ Image URI: {image_uri}", file=sys.stderr)
        
        # Step 2: Upload metadata
        print("Step 2/4: Uploading metadata...", file=sys.stderr)
        metadata_uri = upload_metadata(args.name, args.symbol, args.description, image_uri)
        print(f"✓ Metadata URI: {metadata_uri}", file=sys.stderr)
        
        # Step 3: Mine salt
        print(f"Step 3/4: Mining salt for pattern {args.pattern}...", file=sys.stderr)
        salt_data = mine_salt(args.pattern)
        print(f"✓ Salt: {salt_data['salt']}", file=sys.stderr)
        print(f"✓ Predicted address: {salt_data['predicted_address']}", file=sys.stderr)
        
        # Step 4: Prepare deployment
        print("Step 4/4: Preparing deployment...", file=sys.stderr)
        deployment = deploy_token(metadata_uri, salt_data['salt'])
        
        result = {
            "status": "success",
            "token": {
                "name": args.name,
                "symbol": args.symbol,
                "image_uri": image_uri,
                "metadata_uri": metadata_uri,
                "salt": salt_data['salt'],
                "predicted_address": salt_data['predicted_address']
            },
            "deployment": deployment
        }
        
        print(json.dumps(result, indent=2))
        return 0
        
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": str(e)
        }, indent=2))
        return 1

if __name__ == "__main__":
    sys.exit(main())
