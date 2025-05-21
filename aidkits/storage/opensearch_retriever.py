from typing import List, Dict, Mapping, Any, Type
from uuid import uuid4

from opensearchpy import OpenSearch
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from aidkits.models import LibrarySource, CodeChunk


class OpenSearchRetriever:
    def __init__(
            self,
            client: OpenSearch,
            encoder: SentenceTransformer,
    ) -> None:
        self._client = client
        self._encoder = encoder

    def search(
            self,
            question: str,
            collection_name: str,
            payload_model: Type[BaseModel] = CodeChunk,
            top_k: int = 5,
    ) -> List[BaseModel]:
        """Search for documents in OpenSearch based on a question.
        
        Args:
            question: The question to search for
            collection_name: The name of the index to search in
            payload_model: The model to use for parsing the results
            top_k: The number of results to return
            
        Returns:
            A list of documents matching the query
        """
        query_embedding = self._encoder.encode(
            sentences=question,
            prompt_name="search_query",
        )

        # Convert the embedding to a list if it's not already
        if hasattr(query_embedding, "tolist"):
            query_embedding = query_embedding.tolist()

        # Create a script score query to calculate cosine similarity
        search_body = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                        "params": {"query_vector": query_embedding}
                    }
                }
            }
        }

        response = self._client.search(
            index=collection_name,
            body=search_body
        )

        documents: List[BaseModel] = [
            payload_model.model_validate(hit["_source"])
            for hit in response["hits"]["hits"]
        ]

        return documents

    def search_scored(
            self,
            question: str,
            collection_name: str,
            top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search for documents in OpenSearch and return scored results.
        
        Args:
            question: The question to search for
            collection_name: The name of the index to search in
            top_k: The number of results to return
            
        Returns:
            A list of scored documents matching the query
        """
        query_embedding = self._encoder.encode(
            sentences=question,
            prompt_name="search_query",
        )

        # Convert the embedding to a list if it's not already
        if hasattr(query_embedding, "tolist"):
            query_embedding = query_embedding.tolist()

        # Create a script score query to calculate cosine similarity
        search_body = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                        "params": {"query_vector": query_embedding}
                    }
                }
            }
        }

        response = self._client.search(
            index=collection_name,
            body=search_body
        )

        # Format the results to match the expected output format
        scored_points = []
        for hit in response["hits"]["hits"]:
            scored_point = {
                "id": hit["_id"],
                "payload": hit["_source"],
                "score": hit["_score"],
                "vector": hit["_source"].get("vector", [])
            }
            scored_points.append(scored_point)

        return scored_points

    def create_collection(self, collection_name: str) -> bool:
        """Create a new index in OpenSearch.
        
        Args:
            collection_name: The name of the index to create
            
        Returns:
            True if the index was created successfully
        """
        # Check if the index already exists
        if self._client.indices.exists(index=collection_name):
            return False

        # Create the index with the appropriate mappings for vector search
        index_body = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "vector": {
                        "type": "knn_vector",
                        "dimension": self._encoder.get_sentence_embedding_dimension()
                    },
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "length": {"type": "integer"},
                    "chunk_num": {"type": "integer"},
                    "chunk_amount": {"type": "integer"},
                    "source_title": {"type": "text"}
                }
            }
        }

        response = self._client.indices.create(
            index=collection_name,
            body=index_body
        )

        return response.get("acknowledged", False)

    def delete_collection(self, collection_name: str) -> bool:
        """Delete an index from OpenSearch.
        
        Args:
            collection_name: The name of the index to delete
            
        Returns:
            True if the index was deleted successfully
        """
        if not self._client.indices.exists(index=collection_name):
            return False

        response = self._client.indices.delete(index=collection_name)
        return response.get("acknowledged", False)

    def upload_collection(
            self,
            collection_name: str,
            data: List[Mapping[str, Any]],
            payload_vectorize_field: str,
            batch_size: int = 100,
            show_progress_bar: bool = True,
    ) -> None:
        """Upload a collection of documents to OpenSearch.
        
        Args:
            collection_name: The name of the index to upload to
            data: The data to upload
            payload_vectorize_field: The field to use for vectorization
            batch_size: The batch size for encoding
            show_progress_bar: Whether to show a progress bar
        """
        # Create the index if it doesn't exist
        if not self._client.indices.exists(index=collection_name):
            self.create_collection(collection_name)

        texts: List[str] = [item[payload_vectorize_field] for item in data]
        embeddings = self._encoder.encode(
            sentences=texts,
            batch_size=batch_size,
            prompt_name="search_document",
            show_progress_bar=show_progress_bar,
        )

        # Bulk index the documents
        bulk_data = []
        for payload, embedding in zip(data, embeddings):
            # Convert the embedding to a list if it's not already
            if hasattr(embedding, "tolist"):
                embedding = embedding.tolist()

            # Add the vector to the payload
            payload_with_vector = payload.copy()
            payload_with_vector["vector"] = embedding

            # Add the index operation
            bulk_data.append({"index": {"_index": collection_name, "_id": uuid4().hex}})
            bulk_data.append(payload_with_vector)

            # If we've reached the batch size, index the documents
            if len(bulk_data) >= batch_size * 2:
                self._client.bulk(body=bulk_data)
                bulk_data = []

        # Index any remaining documents
        if bulk_data:
            self._client.bulk(body=bulk_data)

    def upload_library(
            self,
            library: LibrarySource,
            batch_size: int = 100,
    ) -> None:
        """Upload a library to OpenSearch.
        
        Args:
            library: The library to upload
            batch_size: The batch size for encoding
        """
        # Create the index if it doesn't exist
        if not self._client.indices.exists(index=library.title):
            self.create_collection(library.title)

        texts = [item.markdown for item in library.chunks]
        embeddings = self._encoder.encode(
            sentences=texts,
            batch_size=batch_size,
            prompt_name="search_document",
            show_progress_bar=True,
        )

        # Bulk index the documents
        bulk_data = []
        for chunk, embedding in zip(library.chunks, embeddings):
            # Convert the embedding to a list if it's not already
            if hasattr(embedding, "tolist"):
                embedding = embedding.tolist()

            # Add the vector to the payload
            payload = chunk.model_dump()
            payload["vector"] = embedding

            # Add the index operation
            bulk_data.append({"index": {"_index": library.title, "_id": uuid4().hex}})
            bulk_data.append(payload)

            # If we've reached the batch size, index the documents
            if len(bulk_data) >= batch_size * 2:
                self._client.bulk(body=bulk_data)
                bulk_data = []

        # Index any remaining documents
        if bulk_data:
            self._client.bulk(body=bulk_data)
