"""
Message Batcher
Batch messages for efficiency
"""
import time
from typing import List, Any, Optional
from threading import Lock


class MessageBatcher:
    """Batch messages for efficient processing."""
    
    def __init__(self, batch_size: int = 10, timeout: float = 1.0):
        self.batch_size = batch_size
        self.timeout = timeout
        self.batch: List[Any] = []
        self.last_flush = time.time()
        self.lock = Lock()
    
    def add(self, message: Any) -> bool:
        """Add message to batch. Returns True if batch is ready."""
        with self.lock:
            self.batch.append(message)
            
            # Check if batch is full
            if len(self.batch) >= self.batch_size:
                return True
            
            # Check if timeout has passed
            if time.time() - self.last_flush >= self.timeout:
                return True
        
        return False
    
    def get_batch(self) -> List[Any]:
        """Get and clear current batch."""
        with self.lock:
            batch = list(self.batch)
            self.batch = []
            self.last_flush = time.time()
            return batch
    
    def has_pending(self) -> bool:
        """Check if there are pending messages."""
        with self.lock:
            return len(self.batch) > 0
    
    def size(self) -> int:
        """Get current batch size."""
        with self.lock:
            return len(self.batch)


class BatchedSender:
    """Send messages in batches."""
    
    def __init__(self, batcher: MessageBatcher, sender_func):
        self.batcher = batcher
        self.sender_func = sender_func
    
    def send(self, message: Any):
        """Send message (batched)."""
        should_send = self.batcher.add(message)
        
        if should_send:
            batch = self.batcher.get_batch()
            for msg in batch:
                self.sender_func(msg)


if __name__ == "__main__":
    import sys
    
    batcher = MessageBatcher(batch_size=5, timeout=0.5)
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "add":
            for i in range(int(sys.argv[2])):
                batcher.add(f"msg-{i}")
            print(f"Batch size: {batcher.size()}")
        
        elif cmd == "flush":
            batch = batcher.get_batch()
            print(f"Flushed {len(batch)} messages")
        
        elif cmd == "status":
            print(f"Pending: {batcher.has_pending()}, Size: {batcher.size()}")
    else:
        print("Usage: batcher.py <add|flush|status> [count]")