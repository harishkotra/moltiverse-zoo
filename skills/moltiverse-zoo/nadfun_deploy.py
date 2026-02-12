#!/usr/bin/env python3
"""
Deploy a token on nad.fun using the 4-step flow from AGENTS.md
and deploy on-chain to Monad mainnet.
"""
import argparse
import json
import os
import sys
import requests
from pathlib import Path
from web3 import Web3

# API endpoints from AGENTS.md
NADFUN_API = os.getenv("NADFUN_API_URL", "https://api.nad.fun")

# Monad network config
MONAD_RPC = os.getenv("MONAD_RPC_URL", "https://rpc.monad.xyz")
PRIVATE_KEY = os.getenv("MONAD_PRIVATE_KEY", "")

# BondingCurveRouter contract on Monad (from AGENTS.md)
BONDING_CURVE_ROUTER = "0x6F6B8F1a20703309951a5127c45B49b1CD981A22"

# Simple ABI for BondingCurveRouter.create()
ROUTER_ABI = [
    {
        "inputs": [
            {"name": "metadata", "type": "string"},
            {"name": "salt", "type": "bytes32"},
        ],
        "name": "create",
        "outputs": [{"name": "token", "type": "address"}],
        "stateMutability": "payable",
        "type": "function"
    }
]

def upload_image(image_path: str) -> str:
    """Step 1: Upload image to nad.fun."""
    url = f"{NADFUN_API}/agent/token/image"
    
    # Try different form field names that the API might expect
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # Determine mime type
    mime_type = 'image/jpeg' if image_path.endswith('.jpg') or image_path.endswith('.jpeg') else 'image/png'
    
    files = {
        'image': (Path(image_path).name, image_data, mime_type)
    }
    
    response = requests.post(url, files=files)
    
    if not response.ok:
        try:
            error_detail = response.json()
            print(f"API Error Response: {error_detail}", file=sys.stderr)
        except:
            print(f"API Error (no JSON): {response.text}", file=sys.stderr)
    
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
    if not PRIVATE_KEY:
        return {
            "status": "error",
            "error": "MONAD_PRIVATE_KEY not set in .env",
            "note": "Set MONAD_PRIVATE_KEY to deploy on-chain"
        }
    
    try:
        w3 = Web3(Web3.HTTPProvider(MONAD_RPC))
        if not w3.is_connected():
            return {
                "status": "error",
                "error": f"Cannot connect to Monad RPC: {MONAD_RPC}"
            }
        
        # Get account from private key
        account = w3.eth.account.from_key(PRIVATE_KEY)
        print(f"Deploying from: {account.address}", file=sys.stderr)
        
        # Get contract instance
        contract = w3.eth.contract(address=BONDING_CURVE_ROUTER, abi=ROUTER_ABI)
        
        # Get current gas price
        gas_price = w3.eth.gas_price
        print(f"Current gas price: {w3.from_wei(gas_price, 'gwei')} gwei", file=sys.stderr)
        
        # Get nonce
        nonce = w3.eth.get_transaction_count(account.address)
        
        # Convert salt string to bytes32
        salt_bytes = Web3.to_bytes(hexstr=salt if salt.startswith("0x") else f"0x{salt}")
        
        # Estimate gas
        gas_estimate = contract.functions.create(
            metadata_uri,
            salt_bytes
        ).estimate_gas({"from": account.address, "value": Web3.to_wei(0, "ether")})
        
        gas_limit = int(gas_estimate * 1.2)  # 20% buffer
        print(f"Estimated gas: {gas_estimate}, using: {gas_limit}", file=sys.stderr)
        
        # Build transaction
        tx = contract.functions.create(
            metadata_uri,
            salt_bytes
        ).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": gas_limit,
            "gasPrice": gas_price,
            "value": Web3.to_wei(0, "ether")  # Deployment fee may apply
        })
        
        # Sign transaction
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaction sent: {tx_hash.hex()}", file=sys.stderr)
        
        # Wait for receipt
        print("Waiting for confirmation...", file=sys.stderr)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt["status"] == 1:
            print(f"✓ Token deployed successfully!", file=sys.stderr)
            print(f"✓ Transaction hash: {tx_hash.hex()}", file=sys.stderr)
            
            # Try to extract token address from logs
            token_address = None
            if receipt.get("logs"):
                # First log typically contains the token address
                token_address = receipt["logs"][0].get("address") if receipt["logs"] else None
            
            return {
                "status": "success",
                "tx_hash": tx_hash.hex(),
                "block_number": receipt["blockNumber"],
                "gas_used": receipt["gasUsed"],
                "token_address": token_address,
                "explorer_url": f"https://testnet-explorer.monad.xyz/tx/{tx_hash.hex()}"
            }
        else:
            return {
                "status": "error",
                "error": "Transaction reverted",
                "tx_hash": tx_hash.hex()
            }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def main():
    parser = argparse.ArgumentParser(description="Deploy token on nad.fun")
    parser.add_argument("--name", required=True, help="Token name")
    parser.add_argument("--symbol", required=True, help="Token symbol")
    parser.add_argument("--image-path", required=True, help="Path to token image")
    parser.add_argument("--description", default="", help="Token description")
    parser.add_argument("--pattern", default="7777", help="Vanity address pattern")
    parser.add_argument("--mock", action="store_true", help="Mock mode - skip actual API calls")
    
    args = parser.parse_args()
    
    if args.mock:
        print("⚠️  MOCK MODE: Simulating deployment without API calls", file=sys.stderr)
        print("", file=sys.stderr)
        
        result = {
            "status": "mock_success",
            "note": "This is a simulated deployment. For production, remove --mock flag or deploy via nad.fun UI",
            "token": {
                "name": args.name,
                "symbol": args.symbol,
                "image_path": args.image_path,
                "description": args.description,
                "predicted_address": "0x7777000000000000000000000000000000000000",
            },
            "next_steps": [
                "1. Visit https://nad.fun to deploy token via UI",
                "2. Set ZOO_TOKEN_ADDRESS in .env after deployment",
                "3. Set MIN_TOKEN_BALANCE to gate zoo access"
            ]
        }
        
        print(json.dumps(result, indent=2))
        return 0
    
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
