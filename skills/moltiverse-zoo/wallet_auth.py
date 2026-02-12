#!/usr/bin/env python3
"""
Wallet authentication for Moltiverse Zoo.
Implements EIP-191 message signing for user verification and token balance checking.
"""
import json
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct

# Network config
MONAD_RPC = os.getenv("MONAD_RPC_URL", "https://rpc.monad.xyz")

# Zoo token configuration (set after deployment)
ZOO_TOKEN_ADDRESS = os.getenv("ZOO_TOKEN_ADDRESS", "")
ZOO_TOKEN_ABI = [
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Challenge storage (in production, use database)
_challenges: Dict[str, Dict] = {}


def create_auth_challenge(wallet_address: str) -> str:
    """
    Create a unique challenge message for a wallet to sign.
    Returns the message to be signed by the wallet.
    """
    wallet_address = Web3.to_checksum_address(wallet_address)
    
    # Create challenge with timestamp and nonce
    timestamp = int(time.time())
    nonce = os.urandom(16).hex()
    
    message = f"""Welcome to Moltiverse Zoo!

Please sign this message to authenticate and join the ecosystem.

Wallet: {wallet_address}
Timestamp: {datetime.fromtimestamp(timestamp).isoformat()}
Nonce: {nonce}

This is a one-time verification. You will not be charged gas fees."""
    
    # Store challenge for verification
    _challenges[wallet_address] = {
        "message": message,
        "nonce": nonce,
        "timestamp": timestamp,
        "expires_at": timestamp + 300  # 5 minute expiry
    }
    
    print(f"Created challenge for wallet: {wallet_address}")
    return message


def verify_auth_signature(
    wallet_address: str,
    signature: str,
    min_token_balance: int = 0
) -> Dict:
    """
    Verify a wallet's signature and optionally check token balance.
    
    Args:
        wallet_address: The wallet address that signed the message
        signature: The signed message (0x-prefixed hex)
        min_token_balance: Minimum tokens required (0 = no requirement)
    
    Returns:
        {
            "authenticated": bool,
            "address": checksum_address,
            "message": original_message,
            "token_balance": balance_in_units (if ZOO_TOKEN_ADDRESS set),
            "error": error_message (if any)
        }
    """
    print(f"Auth attempt for wallet: {wallet_address}")
    try:
        wallet_address = Web3.to_checksum_address(wallet_address)
        
        # Check if challenge exists
        if wallet_address not in _challenges:
            return {
                "authenticated": False,
                "address": wallet_address,
                "error": "No active challenge. Call create_auth_challenge first."
            }
        
        challenge = _challenges[wallet_address]
        
        # Check if challenge expired
        if time.time() > challenge["expires_at"]:
            del _challenges[wallet_address]
            return {
                "authenticated": False,
                "address": wallet_address,
                "error": "Challenge expired. Create a new challenge."
            }
        
        # Verify signature
        message = encode_defunct(text=challenge["message"])
        recovered_address = Account.recover_message(message, signature=signature)
        recovered_address = Web3.to_checksum_address(recovered_address)
        
        if recovered_address.lower() != wallet_address.lower():
            print(f"Auth failed: signature mismatch. Expected {wallet_address}, got {recovered_address}")
            return {
                "authenticated": False,
                "address": wallet_address,
                "error": f"Invalid signature. Expected {wallet_address}, got {recovered_address}"
            }
        
        # Clean up challenge (only once)
        print(f"DEBUG: Recovered address: {recovered_address}")
        print(f"DEBUG: Expected address: {wallet_address}")
        print(f"DEBUG: Addresses match: {recovered_address.lower() == wallet_address.lower()}")

        if recovered_address.lower() != wallet_address.lower():
            return {
                "authenticated": False,
                "address": wallet_address,
                "error": f"Invalid signature. Expected {wallet_address}, got {recovered_address}"
            }

        # Remove stored challenge after successful verification
        del _challenges[wallet_address]
        
        result = {
            "authenticated": True,
            "address": wallet_address,
            "message": challenge["message"]
        }
        
        # Check token balance if configured
        if ZOO_TOKEN_ADDRESS:
            try:
                w3 = Web3(Web3.HTTPProvider(MONAD_RPC))
                token_contract = w3.eth.contract(
                    address=Web3.to_checksum_address(ZOO_TOKEN_ADDRESS),
                    abi=ZOO_TOKEN_ABI
                )
                
                # Get balance
                balance_raw = token_contract.functions.balanceOf(wallet_address).call()
                
                # Get decimals
                decimals = token_contract.functions.decimals().call()
                balance = balance_raw / (10 ** decimals)
                
                result["token_balance"] = balance
                result["token_balance_raw"] = balance_raw
                
                # Check minimum balance
                if min_token_balance > 0 and balance < min_token_balance:
                    result["authenticated"] = False
                    result["error"] = f"Insufficient token balance. Need {min_token_balance}, have {balance}"
            
            except Exception as e:
                result["token_check_error"] = str(e)
        
        return result
    
    except Exception as e:
        return {
            "authenticated": False,
            "address": wallet_address,
            "error": str(e)
        }


def get_session_token(wallet_address: str) -> Optional[str]:
    """
    Generate a session token for an authenticated wallet.
    In production, use JWT with expiry.
    """
    # Create a session token without re-checking the signature (caller should verify first)
    try:
        import base64
        token_data = f"{wallet_address}:{int(time.time())}"
        token = base64.b64encode(token_data.encode()).decode()
        return token
    except Exception:
        return None


def verify_session_token(token: str) -> Optional[str]:
    """
    Verify a session token and return the wallet address if valid.
    """
    try:
        import base64
        decoded = base64.b64decode(token).decode()
        wallet_address, timestamp = decoded.split(":")
        
        # Check if token is recent (1 hour expiry)
        if time.time() - int(timestamp) > 3600:
            return None
        
        return Web3.to_checksum_address(wallet_address)
    
    except Exception:
        return None


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Wallet authentication for Moltiverse Zoo")
    parser.add_argument("--create-challenge", type=str, help="Create challenge for wallet")
    parser.add_argument("--verify", type=str, help="Verify signature (wallet:signature format)")
    parser.add_argument("--min-balance", type=float, default=0, help="Minimum token balance required")
    
    args = parser.parse_args()
    
    if args.create_challenge:
        challenge = create_auth_challenge(args.create_challenge)
        print("Challenge created. User should sign this message:\n")
        print(challenge)
        print("\n\nThen call: python3 wallet_auth.py --verify <wallet>:<signature>")
    
    elif args.verify:
        parts = args.verify.split(":")
        if len(parts) != 2:
            print("Invalid format. Use: wallet:signature")
        else:
            wallet, sig = parts
            result = verify_auth_signature(wallet, sig, int(args.min_balance))
            print(json.dumps(result, indent=2))
