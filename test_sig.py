from eth_account import Account
from eth_account.messages import encode_defunct

# Test data from the user
wallet = '0x2542b084F2FC864c81Cee6CadB1DD84828dd8288'
sig = '0xb5af4dd9fc1c6b7898403f53ac481c846779c7769ac231c613e7a3dd097aea1939e606cb8c44af9b6d8128c0048ff72d68aa63f1eb47d344b0bb6f72e486473f1c'

# Create a test message
challenge = '''Welcome to Moltiverse Zoo!

Please sign this message to authenticate and join the ecosystem.

Wallet: 0x2542b084F2FC864c81Cee6CadB1DD84828dd8288
Timestamp: 2026-02-12T12:47:00
Nonce: testnonce

This is a one-time verification. You will not be charged gas fees.'''

print('Testing signature verification...')
print('Wallet:', wallet)
print('Signature length (bytes):', len(sig[2:]) // 2)

try:
    message = encode_defunct(text=challenge)
    recovered = Account.recover_message(message, signature=sig)
    print('Recovered address:', recovered)
    print('Expected address:', wallet)
    print('Match:', recovered.lower() == wallet.lower())
except Exception as e:
    print('Error:', str(e))
