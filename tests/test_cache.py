#!/usr/bin/env python
import os
import time
import shutil
import pytest
from app.cache_manager import CacheManager

class TestCacheManager:
    """Unit tests for the CacheManager class."""
    
    @classmethod
    def setup_class(cls):
        """Set up the test class."""
        # Create a test cache directory
        cls.test_cache_dir = "test_cache"
        
        # Clean up any existing test cache directory
        if os.path.exists(cls.test_cache_dir):
            shutil.rmtree(cls.test_cache_dir)
        
        os.makedirs(cls.test_cache_dir, exist_ok=True)
    
    @classmethod
    def teardown_class(cls):
        """Clean up after tests."""
        # Remove the test cache directory
        if os.path.exists(cls.test_cache_dir):
            shutil.rmtree(cls.test_cache_dir)
    
    def setup_method(self):
        """Set up each test method."""
        # Create a cache manager with a short TTL for testing
        self.cache = CacheManager(cache_dir=self.test_cache_dir, ttl=2)
        
        # Test data
        self.test_data = {"query": "Test query", "report_type": "test_report"}
        self.test_result = {"report": "This is a test report", "sources": [{"title": "Test Source", "url": "https://example.com"}]}
    
    def test_cache_get_set(self):
        """Test setting and getting values from cache."""
        # Initially, cache should be empty
        assert self.cache.get(self.test_data) is None
        
        # Set a value in the cache
        self.cache.set(self.test_data, self.test_result)
        
        # Get the value from cache
        cached_result = self.cache.get(self.test_data)
        
        # Check that the cached result matches the original
        assert cached_result is not None
        assert cached_result["report"] == self.test_result["report"]
        assert cached_result["sources"][0]["title"] == self.test_result["sources"][0]["title"]
    
    def test_cache_expiration(self):
        """Test that cached values expire after TTL."""
        # Set a value in the cache
        self.cache.set(self.test_data, self.test_result)
        
        # Verify it's in the cache
        assert self.cache.get(self.test_data) is not None
        
        # Wait for TTL to expire
        time.sleep(3)
        
        # Verify it's no longer in the cache
        assert self.cache.get(self.test_data) is None
    
    def test_cache_invalidate(self):
        """Test invalidating a cached value."""
        # Set a value in the cache
        self.cache.set(self.test_data, self.test_result)
        
        # Verify it's in the cache
        assert self.cache.get(self.test_data) is not None
        
        # Invalidate the cache
        result = self.cache.invalidate(self.test_data)
        
        # Verify invalidation was successful
        assert result is True
        
        # Verify it's no longer in the cache
        assert self.cache.get(self.test_data) is None
