"""
Elasticsearch Connection Utility
Manages connection to Elastic Cloud instance
"""

import os
from typing import Optional
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ElasticsearchClient:
    """Singleton Elasticsearch client"""
    
    _instance: Optional[Elasticsearch] = None
    
    @classmethod
    def get_client(cls) -> Elasticsearch:
        """Get or create Elasticsearch client"""
        if cls._instance is None:
            cls._instance = cls._create_client()
        return cls._instance
    
    @classmethod
    def _create_client(cls) -> Elasticsearch:
        """Create new Elasticsearch client"""
        url = os.getenv('ELASTIC_URL')
        username = os.getenv('ELASTIC_USERNAME')
        password = os.getenv('ELASTIC_PASSWORD')
        
        if not all([url, username, password]):
            raise ValueError("Missing Elasticsearch credentials in .env file")
        
        # Create client
        es = Elasticsearch(
            url,
            basic_auth=(username, password),
            verify_certs=True,
            request_timeout=int(os.getenv('ELASTIC_REQUEST_TIMEOUT', 30)),
            max_retries=int(os.getenv('ELASTIC_MAX_RETRIES', 3)),
            retry_on_timeout=True
        )
        
        # Test connection
        try:
            info = es.info()
            logger.info(f"Connected to Elasticsearch {info['version']['number']}")
            logger.info(f"Cluster: {info['cluster_name']}")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise
        
        return es
    
    @classmethod
    def test_connection(cls) -> dict:
        """Test Elasticsearch connection and return cluster info"""
        es = cls.get_client()
        info = es.info()
        
        return {
            'connected': True,
            'version': info['version']['number'],
            'cluster_name': info['cluster_name'],
            'cluster_uuid': info['cluster_uuid']
        }
    
    @classmethod
    def check_index_exists(cls, index_name: str) -> bool:
        """Check if index exists"""
        es = cls.get_client()
        return es.indices.exists(index=index_name)
    
    @classmethod
    def get_index_count(cls, index_name: str) -> int:
        """Get document count in index"""
        es = cls.get_client()
        if not cls.check_index_exists(index_name):
            return 0
        return es.count(index=index_name)['count']


def get_es_client() -> Elasticsearch:
    """
    Convenience function to get Elasticsearch client
    
    Returns:
        Elasticsearch client instance
    """
    return ElasticsearchClient.get_client()


if __name__ == "__main__":
    # Test connection
    logging.basicConfig(level=logging.INFO)
    
    try:
        info = ElasticsearchClient.test_connection()
        print(f"✓ Connected to Elasticsearch {info['version']}")
        print(f"✓ Cluster: {info['cluster_name']}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        exit(1)
