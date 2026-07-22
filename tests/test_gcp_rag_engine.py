"""
Unit tests for GoogleCloudRAGEngine and policy_search_tool contract
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure root workspace is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.tools.gcp_rag_engine import GoogleCloudRAGEngine, PolicyIndex
from agent.tools.rag_tool import policy_search_tool


class TestGoogleCloudRAGEngine(unittest.TestCase):

    def setUp(self):
        self.knowledge_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../knowledge")
        )

    def test_local_fallback_search(self):
        engine = GoogleCloudRAGEngine(engine_type="local_fallback", knowledge_dir=self.knowledge_dir)
        results = engine.search("leave", top_k=3)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "Local fallback search should return matching policy results")
        
        required_keys = ["doc_title", "header", "file_path", "content", "full_text", "score"]
        for item in results:
            for key in required_keys:
                self.assertIn(key, item, f"Key '{key}' missing in search result")
            self.assertIsInstance(item["score"], float)

    def test_vertex_search_fallback_on_error(self):
        engine = GoogleCloudRAGEngine(engine_type="vertex_search", knowledge_dir=self.knowledge_dir)
        # Without GCP credentials / SDK, search should fallback seamlessly to local index and return results
        results = engine.search("leave", top_k=2)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "Vertex search fallback should yield local policy results")

    def test_vertex_rag_corpus_fallback_on_error(self):
        engine = GoogleCloudRAGEngine(engine_type="vertex_rag_corpus", knowledge_dir=self.knowledge_dir)
        results = engine.search("conduct", top_k=2)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "Vertex RAG corpus fallback should yield local policy results")

    def test_vertex_vector_search_fallback_on_error(self):
        engine = GoogleCloudRAGEngine(engine_type="vertex_vector_search", knowledge_dir=self.knowledge_dir)
        results = engine.search("travel", top_k=2)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "Vertex vector search fallback should yield local policy results")

    def test_mocked_vertex_search_dispatch(self):
        engine = GoogleCloudRAGEngine(engine_type="vertex_search", knowledge_dir=self.knowledge_dir)
        mock_results = [{
            "doc_title": "Mocked Title",
            "header": "Mocked Header",
            "file_path": "mock/path.md",
            "content": "Mocked content body",
            "full_text": "Mocked Title > Mocked Header\nMocked content body",
            "score": 0.95,
        }]
        with patch.object(engine, "_search_vertex_search", return_value=mock_results):
            results = engine.search("query", top_k=1)
            self.assertEqual(results, mock_results)

    def test_mocked_vertex_rag_corpus_dispatch(self):
        engine = GoogleCloudRAGEngine(engine_type="vertex_rag_corpus", knowledge_dir=self.knowledge_dir)
        mock_results = [{
            "doc_title": "RAG Corpus Title",
            "header": "RAG Corpus Section",
            "file_path": "rag/corpus/path.md",
            "content": "RAG Corpus content snippet",
            "full_text": "RAG Corpus Title > RAG Corpus Section\nRAG Corpus content snippet",
            "score": 0.92,
        }]
        with patch.object(engine, "_search_vertex_rag_corpus", return_value=mock_results):
            results = engine.search("query", top_k=1)
            self.assertEqual(results, mock_results)

    def test_mocked_vertex_vector_search_dispatch(self):
        engine = GoogleCloudRAGEngine(engine_type="vertex_vector_search", knowledge_dir=self.knowledge_dir)
        mock_results = [{
            "doc_title": "Vector Search Doc 123",
            "header": "Vector Search Result",
            "file_path": "vector_search://123",
            "content": "Matching vector document snippet",
            "full_text": "Vector Search Doc 123 > Vector Search Result\nMatching vector document snippet",
            "score": 0.88,
        }]
        with patch.object(engine, "_search_vertex_vector_search", return_value=mock_results):
            results = engine.search("query", top_k=1)
            self.assertEqual(results, mock_results)


class TestPolicySearchToolContract(unittest.TestCase):

    def test_policy_search_tool_found_contract(self):
        res = policy_search_tool("leave policy")
        self.assertIsInstance(res, dict)
        self.assertIn("found", res)
        self.assertIn("query", res)
        self.assertIn("results", res)
        self.assertIn("citations", res)

        self.assertTrue(res["found"])
        self.assertEqual(res["query"], "leave policy")
        self.assertGreater(len(res["results"]), 0)
        self.assertGreater(len(res["citations"]), 0)

        for item in res["results"]:
            self.assertIn("source", item)
            self.assertIn("content", item)

        for cit in res["citations"]:
            self.assertIn("document", cit)
            self.assertIn("section", cit)
            self.assertIn("file", cit)

    def test_policy_search_tool_not_found_contract(self):
        res = policy_search_tool("nonexistentxyz123query")
        self.assertIsInstance(res, dict)
        self.assertIn("found", res)
        self.assertIn("query", res)
        self.assertIn("results", res)
        self.assertIn("citations", res)
        self.assertFalse(res["found"])
        self.assertEqual(res["results"], [])
        self.assertEqual(res["citations"], [])


if __name__ == "__main__":
    unittest.main()
