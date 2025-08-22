# backend/simple_cache.py
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class SimpleAnalysisCache:
    def __init__(self):
        self.store: Dict[str, Dict] = {}
        self.lock = asyncio.Lock()
        self.max_size = 50
        self.ttl_hours = 24
    
    def _compute_key(self, file_bytes: bytes, context: str) -> str:
        """Compute cache key from file content + context"""
        hasher = hashlib.sha256()
        hasher.update(file_bytes)
        hasher.update(context.encode('utf-8'))
        return hasher.hexdigest()
    
    async def get_cached_result(self, file_bytes: bytes, context: str) -> Optional[Dict[str, Any]]:
        """Get cached result if exists and valid"""
        cache_key = self._compute_key(file_bytes, context)
        
        async with self.lock:
            if cache_key in self.store:
                cached_item = self.store[cache_key]
                
                # Check TTL
                cached_time = cached_item['timestamp']
                if datetime.now() - cached_time < timedelta(hours=self.ttl_hours):
                    print(f"✅ Cache HIT for file (key: {cache_key[:12]}...)")
                    return cached_item['result']
                else:
                    # Remove expired entry
                    del self.store[cache_key]
                    print(f"🗑️ Expired cache entry removed")
            
            print(f"❌ Cache MISS for file (key: {cache_key[:12]}...)")
            return None
    
    async def set_cached_result(self, file_bytes: bytes, context: str, result: Dict[str, Any]):
        """Store result in cache"""
        cache_key = self._compute_key(file_bytes, context)
        
        async with self.lock:
            # Implement simple LRU eviction
            if len(self.store) >= self.max_size:
                # Remove oldest entry
                oldest_key = min(self.store.keys(), 
                               key=lambda k: self.store[k]['timestamp'])
                del self.store[oldest_key]
                print(f"🗑️ Cache full, removed oldest entry")
            
            self.store[cache_key] = {
                'result': result,
                'timestamp': datetime.now()
            }
            
            print(f"💾 Cached result (key: {cache_key[:12]}..., total entries: {len(self.store)})")
    
    async def get_stats(self):
        """Get cache statistics"""
        async with self.lock:
            return {
                "total_entries": len(self.store),
                "max_entries": self.max_size,
                "ttl_hours": self.ttl_hours
            }

# Global cache instance
analysis_cache = SimpleAnalysisCache()
