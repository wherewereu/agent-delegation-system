"""
Test: Message Encryption
Red first - tests for encrypted inter-agent communication
"""
import pytest
import os
from encryption import MessageEncryptor


class TestMessageEncryption:
    """Test message encryption for agent communication."""

    def test_generate_key(self):
        """Should generate encryption key"""
        key = MessageEncryptor.generate_key()
        
        assert key is not None
        assert len(key) == 32  # 256-bit key

    def test_encrypt_decrypt(self):
        """Should encrypt and decrypt message"""
        encryptor = MessageEncryptor()
        
        plaintext = "secret task for scout"
        
        encrypted = encryptor.encrypt(plaintext)
        
        assert encrypted != plaintext
        
        decrypted = encryptor.decrypt(encrypted)
        
        assert decrypted == plaintext

    def test_different_ciphertext(self):
        """Same message should produce different ciphertext"""
        encryptor = MessageEncryptor()
        
        msg = "same message"
        
        encrypted1 = encryptor.encrypt(msg)
        encrypted2 = encryptor.encrypt(msg)
        
        # Should be different due to random IV
        assert encrypted1 != encrypted2

    def test_encrypted_message_format(self):
        """Should produce proper encrypted message format"""
        encryptor = MessageEncryptor()
        
        encrypted = encryptor.encrypt("test message")
        
        # Should have ciphertext and IV
        assert "ciphertext" in encrypted
        assert "iv" in encrypted


class TestSecureMessenger:
    """Test secure messenger between agents."""

    def test_create_secure_channel(self):
        """Should create secure communication channel"""
        from encryption import SecureMessenger
        
        messenger = SecureMessenger()
        
        channel = messenger.create_channel("scout", "link")
        
        assert channel is not None

    def test_send_secure_message(self):
        """Should send encrypted message between agents"""
        from encryption import SecureMessenger
        
        messenger = SecureMessenger()
        
        channel = messenger.create_channel("scout", "link")
        
        result = messenger.send("scout", "link", "secret data", channel)
        
        assert result is True


class TestErrorCodes:
    """Test standardized error codes."""

    def test_error_code_list(self):
        """Should have list of error codes"""
        from errors import ErrorCode, get_error_message
        
        assert ErrorCode.TIMEOUT.value == "TIMEOUT"
        assert ErrorCode.AGENT_UNAVAILABLE.value == "AGENT_UNAVAILABLE"
        
        msg = get_error_message(ErrorCode.TIMEOUT)
        
        assert "timed out" in msg.lower() or "timeout" in msg.lower()

    def test_error_handling(self):
        """Should handle errors properly"""
        from errors import DelegationError, ErrorCode
        
        error = DelegationError(ErrorCode.AGENT_UNAVAILABLE, "scout is busy")
        
        assert error.code == ErrorCode.AGENT_UNAVAILABLE
        assert "scout is busy" in str(error)