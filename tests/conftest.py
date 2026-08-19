import sys
from pathlib import Path

# Add project root to sys.path during test execution
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_project_root(tmp_path):
    with patch("pipeline.deduplicator.PROJECT_ROOT", tmp_path):
        yield

class MockSentenceTransformer:
    def encode(self, sentences, **kwargs):
        is_single = isinstance(sentences, str)
        if is_single:
            sentences = [sentences]
            
        embeddings = []
        for s in sentences:
            s_lower = s.lower()
            if "learning data curation" in s_lower:
                if "useful" in s_lower:
                    embeddings.append([1.0, 1.0, 0.1])
                else:
                    embeddings.append([1.0, 1.0, 0.0])
            else:
                embeddings.append([0.0, 0.0, 1.0])
                
        import numpy as np
        res = np.array(embeddings, dtype=np.float32)
        return res[0] if is_single else res

@pytest.fixture(scope="session")
def dedup_model():
    return MockSentenceTransformer()
