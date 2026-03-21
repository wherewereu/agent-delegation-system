"""
Message Encryption
Encrypt inter-agent messages for secure communication
"""
import os
import json
import base64
from typing import Dict, Optional


class MessageEncryptor:
    """Encrypt and decrypt messages between agents using XOR cipher."""
    
    def __init__(self, key: Optional[bytes] = None):
        self.key = key or self._load_or_generate_key()
    
    def _load_or_generate_key(self) -> bytes:
        """Load key from file or generate new one."""
        key_file = "/Users/soup/.openclaw/workspace/delegation/memory/.key"
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        
        # Generate new key
        key = os.urandom(32)
        
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, "wb") as f:
            f.write(key)
        
        return key
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key."""
        return os.urandom(32)
    
    def _xor_encrypt(self, data: bytes) -> bytes:
        """XOR encrypt data with key."""
        key = self.key
        result = bytearray()
        
        for i, byte in enumerate(data):
            result.append(byte ^ key[i % len(key)])
        
        return bytes(result)
    
    def encrypt(self, plaintext: str) -> Dict:
        """Encrypt a message."""
        data = plaintext.encode()
        
        # Generate random IV
        iv = os.urandom(16)
        
        # Combine IV + data and encrypt
        combined = iv + data
        encrypted = self._xor_encrypt(combined)
        
        return {
            "ciphertext": base64.b64encode(encrypted).decode(),
            "iv": base64.b64encode(iv).decode(),
            "version": "1"
        }
    
    def decrypt(self, encrypted: Dict) -> str:
        """Decrypt a message."""
        ciphertext = base64.b64decode(encrypted["ciphertext"])
        iv = base64.b64decode(encrypted["iv"])
        
        # Decrypt
        decrypted = self._xor_encrypt(ciphertext)
        
        # Remove IV
        plaintext = decrypted[16:]
        
        return plaintext.decode()


class SecureMessenger:
    """Send encrypted messages between agents."""
    
    def __init__(self):
        self.encryptor = MessageEncryptor()
        self.channels: Dict[str, bytes] = {}
    
    def create_channel(self, from_agent: str, to_agent: str) -> str:
        """Create a secure channel between two agents."""
        channel_id = f"{from_agent}:{to_agent}"
        
        # Generate channel key
        channel_key = os.urandom(32)
        self.channels[channel_id] = channel_key
        
        return channel_id
    
    def send(
        self,
        from_agent: str,
        to_agent: str,
        message: str,
        channel_id: str = None
    ) -> bool:
        """Send encrypted message."""
        if not channel_id:
            channel_id = f"{from_agent}:{to_agent}"
        
        # Encrypt message
        encrypted = self.encryptor.encrypt(message)
        
        # In real implementation, would send via Hydra
        return True
    
    def receive(
        self,
        from_agent: str,
        to_agent: str,
        encrypted: Dict,
        channel_id: str = None
    ) -> Optional[str]:
        """Receive and decrypt message."""
        if not channel_id:
            channel_id = f"{from_agent}:{to_agent}"
        
        try:
            return self.encryptor.decrypt(encrypted)
        except Exception as e:
            print(f"Decryption error: {e}")
            return None


# Global instances
encryptor = MessageEncryptor()
messenger = SecureMessenger()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "encrypt":
            text = " ".join(sys.argv[2:])
            encrypted = encryptor.encrypt(text)
            print(json.dumps(encrypted))
        
        elif cmd == "decrypt":
            encrypted = json.loads(" ".join(sys.argv[2:]))
            print(encryptor.decrypt(encrypted))
        
        elif cmd == "key":
            print(base64.b64encode(encryptor.key).decode())
    else:
        print("Usage: encryption.py <encrypt|decrypt|key> [args]")
