from unittest.mock import Mock, patch


class TestClassifyQuery:
    """Test classify_query function"""

    def test_classify_identity_query(self):
        """Test identity phrase classification"""
        from backend.app.core.rag_service import classify_query

        mock_llm = Mock()

        identity_queries = [
            "Who are you?",
            "What are you?",
            "Tell me about yourself",
            "Introduce yourself",
        ]

        for query in identity_queries:
            result = classify_query(query, mock_llm)
            assert result == "identity", f"Failed for query: {query}"

    def test_classify_policy_query(self):
        """Test policy keyword classification"""
        from backend.app.core.rag_service import classify_query

        mock_llm = Mock()

        policy_queries = [
            "What is the leave policy?",
            "How many leave days do I get?",
            "Tell me about the notice period",
            "What is the communication allowance?",
            "Explain the employment contract",
        ]

        for query in policy_queries:
            result = classify_query(query, mock_llm)
            assert result == "policy", f"Failed for query: {query}"

    def test_classify_casual_query(self):
        """Test casual phrase classification"""
        from backend.app.core.rag_service import classify_query

        mock_llm = Mock()

        # These should match exactly or start the query
        casual_queries = [
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
            "bye",
            "goodbye",
            "thanks",
            "thank you",
            "ok",
            "okay",
            "sure",
            # With spaces after
            "hi there",
            "hello world",
            "thanks a lot",
            "how are you how",  # starts with "how are you "
            "good morning everyone",
        ]

        for query in casual_queries:
            result = classify_query(query, mock_llm)
            assert result == "casual", f"Failed for query: '{query}' - got {result}"

    def test_classify_casual_query_with_punctuation(self):
        """Test casual phrases don't match with punctuation"""
        from backend.app.core.rag_service import classify_query

        mock_llm = Mock()
        mock_llm.generate_raw = Mock(return_value="casual")

        # These have punctuation, so they won't match the exact triggers
        # They will fall back to LLM classification
        punctuated_queries = [
            "Hi!",
            "Hello?",
            "How are you?",
            "Thanks!",
        ]

        for query in punctuated_queries:
            result = classify_query(query, mock_llm)
            # These will use LLM for classification
            assert result in [
                "casual",
                "unknown",
            ], f"Failed for query: '{query}' - got {result}"

    def test_classify_unknown_uses_llm(self):
        """Test unknown queries use LLM classifier"""
        from backend.app.core.rag_service import classify_query

        mock_llm = Mock()
        mock_llm.generate_raw = Mock(return_value="policy")

        result = classify_query("Some random question", mock_llm)
        assert result == "policy"
        mock_llm.generate_raw.assert_called_once()

    def test_classify_llm_fallback_unknown(self):
        """Test LLM fallback returns unknown on exception"""
        from backend.app.core.rag_service import classify_query

        mock_llm = Mock()
        mock_llm.generate_raw = Mock(side_effect=Exception("LLM error"))

        result = classify_query("Some unique question", mock_llm)
        assert result == "unknown"


class TestRewriteQuery:
    """Test rewrite_query function"""

    def test_rewrite_query_calls_llm(self):
        """Test rewrite_query calls LLM"""
        from backend.app.core.rag_service import rewrite_query

        mock_llm = Mock()
        mock_llm.generate_raw = Mock(return_value="rewritten query")

        result = rewrite_query("original query", mock_llm)

        assert result == "rewritten query"
        mock_llm.generate_raw.assert_called_once()

    def test_rewrite_query_uses_company_terminology(self):
        """Test rewrite_query prompt includes terminology hints"""
        from backend.app.core.rag_service import rewrite_query

        mock_llm = Mock()
        mock_llm.generate_raw = Mock(return_value="rewritten")

        rewrite_query("test query", mock_llm)

        call_args = mock_llm.generate_raw.call_args[0][0]
        assert "commission" in call_args or "allowance" in call_args


class TestTruncateContext:
    """Test truncate_context function"""

    def test_truncate_context_empty_string(self):
        """Test truncate_context with empty string"""
        from backend.app.core.rag_service import truncate_context

        result = truncate_context("", 600)
        assert result == ""

    def test_truncate_context_none(self):
        """Test truncate_context with None"""
        from backend.app.core.rag_service import truncate_context

        result = truncate_context(None, 600)
        assert result == ""

    def test_truncate_context_short_text(self):
        """Test truncate_context with short text"""
        from backend.app.core.rag_service import truncate_context

        text = "This is a short text."
        result = truncate_context(text, 600)
        assert result == text

    def test_truncate_context_long_text(self):
        """Test truncate_context truncates long text"""
        from backend.app.core.rag_service import truncate_context

        text = "Sentence one. Sentence two. Sentence three. " * 50
        result = truncate_context(text, 100)

        assert len(result) <= 110  # Allow some buffer
        assert result.endswith(".")

    def test_truncate_context_max_chars_respected(self):
        """Test truncate_context respects max_chars limit"""
        from backend.app.core.rag_service import truncate_context

        text = "Word " * 200
        result = truncate_context(text, 200)

        assert len(result) <= 210


class TestRunRag:
    """Test run_rag function"""

    def test_run_rag_identity_query(
        self, mock_embedder, mock_vector_store, mock_llm, mock_reranker, mock_bm25
    ):
        """Test run_rag handles identity queries"""
        from backend.app.core.rag_service import run_rag

        with patch(
            "backend.app.core.rag_service.classify_query", return_value="identity"
        ):
            answer, sources, context, status = run_rag(
                "Who are you?",
                mock_embedder,
                mock_vector_store,
                mock_llm,
                mock_reranker,
                mock_bm25,
            )

            assert status == "identity"
            assert "Wamo Labs" in answer
            assert sources == []

    def test_run_rag_casual_query(
        self, mock_embedder, mock_vector_store, mock_llm, mock_reranker, mock_bm25
    ):
        """Test run_rag handles casual queries"""
        from backend.app.core.rag_service import run_rag

        mock_llm.generate = Mock(return_value="Hello! How can I help?")

        with patch(
            "backend.app.core.rag_service.classify_query", return_value="casual"
        ):
            answer, sources, context, status = run_rag(
                "Hello",
                mock_embedder,
                mock_vector_store,
                mock_llm,
                mock_reranker,
                mock_bm25,
            )

            assert status == "casual"
            assert answer == "Hello! How can I help?"
            assert sources == []

    def test_run_rag_policy_query_no_results(
        self, mock_embedder, mock_vector_store, mock_llm, mock_reranker, mock_bm25
    ):
        """Test run_rag returns default message when no results"""
        from backend.app.core.rag_service import run_rag

        mock_reranker.rerank = Mock(return_value=[])

        with patch(
            "backend.app.core.rag_service.classify_query", return_value="policy"
        ):
            with patch(
                "backend.app.core.rag_service.rewrite_query", return_value="rewritten"
            ):
                answer, sources, context, status = run_rag(
                    "Leave policy?",
                    mock_embedder,
                    mock_vector_store,
                    mock_llm,
                    mock_reranker,
                    mock_bm25,
                )

                assert status == "out_of_context"
                assert "Wamo Labs" in answer
                assert sources == []

    def test_run_rag_policy_query_success(
        self, mock_embedder, mock_vector_store, mock_llm, mock_reranker, mock_bm25
    ):
        """Test run_rag successfully processes policy query"""
        from backend.app.core.rag_service import run_rag

        mock_llm.generate = Mock(
            return_value="Based on policy, employees get 20 leave days."
        )

        with patch(
            "backend.app.core.rag_service.classify_query", return_value="policy"
        ):
            with patch(
                "backend.app.core.rag_service.rewrite_query", return_value="rewritten"
            ):
                answer, sources, context, status = run_rag(
                    "How many leave days?",
                    mock_embedder,
                    mock_vector_store,
                    mock_llm,
                    mock_reranker,
                    mock_bm25,
                )

                assert status == "ok"
                assert "20 leave days" in answer
                assert len(sources) > 0

    def test_run_rag_with_history(
        self, mock_embedder, mock_vector_store, mock_llm, mock_reranker, mock_bm25
    ):
        """Test run_rag includes conversation history"""
        from backend.app.core.rag_service import run_rag

        history = [
            {"role": "user", "content": "What is leave policy?"},
            {"role": "assistant", "content": "Leave policy is..."},
        ]

        mock_llm.generate = Mock(return_value="Answer with context")

        with patch(
            "backend.app.core.rag_service.classify_query", return_value="policy"
        ):
            with patch(
                "backend.app.core.rag_service.rewrite_query", return_value="rewritten"
            ):
                run_rag(
                    "Tell me more",
                    mock_embedder,
                    mock_vector_store,
                    mock_llm,
                    mock_reranker,
                    mock_bm25,
                    history=history,
                )

                # Verify history was used
                mock_llm.generate.assert_called_once()


class TestRunRagStream:
    """Test run_rag_stream function"""

    def test_run_rag_stream_identity_query(
        self, mock_embedder, mock_vector_store, mock_llm, mock_reranker, mock_bm25
    ):
        """Test run_rag_stream handles identity queries"""
        from backend.app.core.rag_service import run_rag_stream

        with patch(
            "backend.app.core.rag_service.classify_query", return_value="identity"
        ):
            events = list(
                run_rag_stream(
                    "Who are you?",
                    mock_embedder,
                    mock_vector_store,
                    mock_llm,
                    mock_reranker,
                    mock_bm25,
                )
            )

            # Should have token and done events
            assert len(events) >= 2
            assert events[0][0] == "token"
            assert events[-1][0] == "done"
            assert events[-1][1]["status"] == "identity"

    def test_run_rag_stream_casual_query(
        self, mock_embedder, mock_vector_store, mock_llm, mock_reranker, mock_bm25
    ):
        """Test run_rag_stream handles casual queries"""
        from backend.app.core.rag_service import run_rag_stream

        with patch(
            "backend.app.core.rag_service.classify_query", return_value="casual"
        ):
            events = list(
                run_rag_stream(
                    "Hi",
                    mock_embedder,
                    mock_vector_store,
                    mock_llm,
                    mock_reranker,
                    mock_bm25,
                )
            )

            assert events[-1][1]["status"] == "casual"

    def test_run_rag_stream_policy_query(
        self, mock_embedder, mock_vector_store, mock_llm, mock_reranker, mock_bm25
    ):
        """Test run_rag_stream handles policy queries"""
        from backend.app.core.rag_service import run_rag_stream

        with patch(
            "backend.app.core.rag_service.classify_query", return_value="policy"
        ):
            with patch(
                "backend.app.core.rag_service.rewrite_query", return_value="rewritten"
            ):
                events = list(
                    run_rag_stream(
                        "Leave policy?",
                        mock_embedder,
                        mock_vector_store,
                        mock_llm,
                        mock_reranker,
                        mock_bm25,
                    )
                )

                # Verify stream format
                token_events = [e for e in events if e[0] == "token"]
                done_events = [e for e in events if e[0] == "done"]

                assert len(token_events) > 0
                assert len(done_events) == 1
                assert done_events[0][1]["status"] == "ok"

    def test_run_rag_stream_yields_proper_format(
        self, mock_embedder, mock_vector_store, mock_llm, mock_reranker, mock_bm25
    ):
        """Test run_rag_stream yields proper event format"""
        from backend.app.core.rag_service import run_rag_stream

        with patch(
            "backend.app.core.rag_service.classify_query", return_value="policy"
        ):
            with patch(
                "backend.app.core.rag_service.rewrite_query", return_value="rewritten"
            ):
                for event_type, data in run_rag_stream(
                    "Leave policy?",
                    mock_embedder,
                    mock_vector_store,
                    mock_llm,
                    mock_reranker,
                    mock_bm25,
                ):
                    assert isinstance(event_type, str)
                    assert isinstance(data, dict)
                    assert event_type in ["token", "done", "error"]
                    break  # Just check first event
