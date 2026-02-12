#!/usr/bin/env python3
"""
Check token balance on Monad blockchain.
"""
import argparse
import json
import os
import sys
from web3 import Web3

# Default RPC from AGENTS.md
MONAD_RPC = os.getenv("MONAD_RPC_URL", "https://rpc.monad.xyz")

def check_balance(address: str, token_address: str = None) -> dict:
    """Check MON or token balance."""
    w3 = Web3(Web3.HTTPProvider(MONAD_RPC))
    
    if not w3.is_connected():
        return {"status": "error", "error": "Cannot connect to Monad RPC"}
    
    # Check MON balance
    mon_balance = w3.eth.get_balance(address)
    mon_balance_eth = w3.from_wei(mon_balance, 'ether')
    
    result = {
        "status": "success",
        "address": address,
        "mon_balance": str(mon_balance_eth),
        "mon_balance_wei": str(mon_balance)
    }
    
    # If token address provided, check ERC20 balance
    if token_address:
        # ERC20 balanceOf ABI
        erc20_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            }
        ]
        
        try:
            contract = w3.eth.contract(address=token_address, abi=erc20_abi)
            token_balance = contract.functions.balanceOf(address).call()
            result["token_address"] = token_address
            result["token_balance"] = str(token_balance)
        except Exception as e:
            result["token_error"] = str(e)
    
    return result

def main():
    parser = argparse.ArgumentParser(description="Check balance on Monad")
    parser.add_argument("--address", required=True, help="Wallet address")
    parser.add_argument("--token", help="Token contract address (optional)")
    
    args = parser.parse_args()
    
    result = check_balance(args.address, args.token)
    print(json.dumps(result, indent=2))
    
    return 0 if result.get("status") == "success" else 1

if __name__ == "__main__":
    sys.exit(main())
