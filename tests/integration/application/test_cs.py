"""Integration tests for customer service application services."""

from unittest.mock import Mock

import pytest

from oneai_reach.application.customer_service.cs_engine_service import CSEngineService


@pytest.fixture
def mock_conversation_service():
    service = Mock()
    service.get_or_create_conversation.return_value = {
        "id": 1,
        "wa_number_id": "wa_123",
        "contact_phone": "+6281234567890",
        "message_count": 0,
        "engine_mode": "cs",
    }
    service.add_message.return_value = None
    service.is_cold_lead.return_value = False
    service.get_conversation_context.return_value = "User: Hello\nAgent: Hi there!"
    service.advance_stage.return_value = None
    service.get_stage_context.return_value = ""
    service.escalate.return_value = None
    return service


@pytest.fixture
def mock_outcomes_service():
    return Mock()


@pytest.fixture
def mock_playbook_service():
    return Mock()


class TestCSEngineService:
    def test_detect_language_indonesian(
        self,
        settings,
        mock_conversation_service,
        mock_outcomes_service,
        mock_playbook_service,
    ):
        service = CSEngineService(
            settings,
            mock_conversation_service,
            mock_outcomes_service,
            mock_playbook_service,
        )

        assert service._detect_language("Berapa harganya?") == "id"
        assert service._detect_language("Apa bisa kirim hari ini?") == "id"
        assert service._detect_language("Gimana cara belinya dong?") == "id"

    def test_detect_language_english(
        self,
        settings,
        mock_conversation_service,
        mock_outcomes_service,
        mock_playbook_service,
    ):
        service = CSEngineService(
            settings,
            mock_conversation_service,
            mock_outcomes_service,
            mock_playbook_service,
        )

        assert service._detect_language("What is the price?") == "en"
        assert service._detect_language("How can I order?") == "en"

    def test_detect_user_type_bulk(
        self,
        settings,
        mock_conversation_service,
        mock_outcomes_service,
        mock_playbook_service,
    ):
        service = CSEngineService(
            settings,
            mock_conversation_service,
            mock_outcomes_service,
            mock_playbook_service,
        )

        assert (
            service._detect_user_type("Mau beli banyak, ada harga grosir?", 1) == "bulk"
        )
        assert service._detect_user_type("Untuk reseller ada diskon?", 1) == "bulk"

    def test_detect_user_type_urgent(
        self,
        settings,
        mock_conversation_service,
        mock_outcomes_service,
        mock_playbook_service,
    ):
        service = CSEngineService(
            settings,
            mock_conversation_service,
            mock_outcomes_service,
            mock_playbook_service,
        )

        assert (
            service._detect_user_type("Butuh sekarang, bisa kirim hari ini?", 1)
            == "urgent"
        )
        assert service._detect_user_type("Kapan sampai? Buru-buru nih", 1) == "urgent"

    def test_detect_user_type_price_sensitive(
        self,
        settings,
        mock_conversation_service,
        mock_outcomes_service,
        mock_playbook_service,
    ):
        service = CSEngineService(
            settings,
            mock_conversation_service,
            mock_outcomes_service,
            mock_playbook_service,
        )

        assert (
            service._detect_user_type("Mahal banget, bisa kurangin?", 1)
            == "price_sensitive"
        )
        assert service._detect_user_type("Ada diskon gak?", 1) == "price_sensitive"

    def test_detect_user_type_friction(
        self,
        settings,
        mock_conversation_service,
        mock_outcomes_service,
        mock_playbook_service,
    ):
        service = CSEngineService(
            settings,
            mock_conversation_service,
            mock_outcomes_service,
            mock_playbook_service,
        )

        assert service._detect_user_type("Ragu nih, aman gak?", 1) == "friction"
        assert service._detect_user_type("Takut tipu, bisa COD?", 1) == "friction"

    def test_is_purchase_signal(
        self,
        settings,
        mock_conversation_service,
        mock_outcomes_service,
        mock_playbook_service,
    ):
        service = CSEngineService(
            settings,
            mock_conversation_service,
            mock_outcomes_service,
            mock_playbook_service,
        )

        assert service._is_purchase_signal("Sudah transfer ya") is True
        assert service._is_purchase_signal("Ini bukti bayarnya") is True
        assert service._is_purchase_signal("Udah dikirim belum?") is True
        assert service._is_purchase_signal("Mau tanya harga") is False

    def test_is_shipping_complaint(
        self,
        settings,
        mock_conversation_service,
        mock_outcomes_service,
        mock_playbook_service,
    ):
        service = CSEngineService(
            settings,
            mock_conversation_service,
            mock_outcomes_service,
            mock_playbook_service,
        )

        assert service._is_shipping_complaint("Ongkir mahal banget") is True
        assert service._is_shipping_complaint("Kemahalan ongkirnya") is True
        assert service._is_shipping_complaint("Jauh dari luar jawa") is True
        assert service._is_shipping_complaint("Berapa harganya?") is False

    def test_kb_search_sanitization(
        self,
        settings,
        mock_conversation_service,
        mock_outcomes_service,
        mock_playbook_service,
    ):
        service = CSEngineService(
            settings,
            mock_conversation_service,
            mock_outcomes_service,
            mock_playbook_service,
        )

        sanitized = service._sanitize_fts_query("What's the price? #urgent!")
        assert "#" not in sanitized
        assert "?" not in sanitized
        assert "!" not in sanitized

    def test_should_skip_cold_lead(
        self,
        settings,
        mock_conversation_service,
        mock_outcomes_service,
        mock_playbook_service,
    ):
        mock_conversation_service.is_cold_lead.return_value = True

        service = CSEngineService(
            settings,
            mock_conversation_service,
            mock_outcomes_service,
            mock_playbook_service,
        )

        assert service.should_skip("+6281234567890", "wa_123") is True

    def test_should_escalate_no_kb_results_multiple_turns(
        self,
        settings,
        mock_conversation_service,
        mock_outcomes_service,
        mock_playbook_service,
    ):
        mock_conversation_service.get_conversation_context.return_value = (
            "User: Question 1\nAgent: Answer 1\n"
            "User: Question 2\nAgent: Answer 2\n"
            "User: Question 3\nAgent: Answer 3\n"
            "User: Still confused"
        )

        service = CSEngineService(
            settings,
            mock_conversation_service,
            mock_outcomes_service,
            mock_playbook_service,
        )

        conversation = {"id": 1}
        assert service.should_escalate("I don't understand", [], conversation) is True

    def test_should_not_escalate_with_kb_results(
        self,
        settings,
        mock_conversation_service,
        mock_outcomes_service,
        mock_playbook_service,
    ):
        service = CSEngineService(
            settings,
            mock_conversation_service,
            mock_outcomes_service,
            mock_playbook_service,
        )

        kb_results = [{"question": "Q", "answer": "A"}]
        conversation = {"id": 1}
        assert service.should_escalate("Question", kb_results, conversation) is False
