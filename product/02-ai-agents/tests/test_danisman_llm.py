"""
danisman_llm.py testleri — execution.md §3b Phase 7 / 7.5.

`anthropic.Anthropic` mock'lanır (gerçek API çağrısı YOK, `ANTHROPIC_API_KEY`
gerekmez) — burada test edilen şey SDK'nın kendisi değil, agent'ın (a) hangi
koşulda hangi moda düştüğü ve (b) yanıt-sonrası doğrulama guard'ının gerçekten
uydurma sayıları yakaladığı.
"""
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from aks_core.agents import danisman_llm

_BAGLAM = {
    "aks_skor": 720, "risk_seviyesi": "düşük risk", "karar": "onaylanabilir",
    "klasik_skor": 650,
    "aciklama": {"riski_azaltan": [{"faktor": "bakiye_trendi", "kod": "bakiye_trendi"}],
                 "riski_artiran": [{"faktor": "gider_gelir_orani", "kod": "gider_gelir_orani"}]},
}


def _metin_bloğu(text):
    return SimpleNamespace(type="text", text=text)


def _tool_use_bloğu(name, input_, id_="toolu_1"):
    return SimpleNamespace(type="tool_use", name=name, input=input_, id=id_)


def _gemini_fc_bloğu(name, args):
    return SimpleNamespace(function_call=SimpleNamespace(name=name, args=args), text=None)


def _gemini_metin_bloğu(text):
    return SimpleNamespace(function_call=None, text=text)


def _gemini_yanit(parts):
    return SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=parts))])


class TestAnahtarVeBaglamKosullari:
    def test_anahtar_yoksa_kural_moduna_duser(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        sonuc = danisman_llm.yanitla("skorum neden düşük?", _BAGLAM)
        assert sonuc["mod"] == "kural"
        assert sonuc["saglayici"] == "kural"
        assert sonuc["arac_cagrilari"] == []

    def test_aks_skoru_yoksa_anahtar_olsa_bile_kural_moduna_duser(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sahte-anahtar")
        sonuc = danisman_llm.yanitla("merhaba", {})
        assert sonuc["mod"] == "kural"


class TestToolCallingAkisi:
    def test_basarili_arac_cagrisi_ve_dogrulanan_yanit(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sahte-anahtar")

        tur1 = SimpleNamespace(
            stop_reason="tool_use",
            content=[_tool_use_bloğu("skor_getir", {})],
        )
        tur2 = SimpleNamespace(
            stop_reason="end_turn",
            content=[_metin_bloğu("Skorun 720/850, düşük risk seviyesinde.")],
        )

        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value.messages.create.side_effect = [tur1, tur2]
            sonuc = danisman_llm.yanitla("skorum nedir?", _BAGLAM)

        assert sonuc["mod"] == "llm-arac"
        assert sonuc["anlati_reddedildi"] is False
        assert "720" in sonuc["yanit"]
        assert len(sonuc["arac_cagrilari"]) == 1
        assert sonuc["arac_cagrilari"][0]["arac"] == "skor_getir"

    def test_uydurma_sayi_iceren_yanit_reddedilir(self, monkeypatch):
        """Model, HİÇBİR araç çıktısında geçmeyen bir limit sayısı söylerse
        (ör. 999999) yanıt reddedilmeli — bu, 'LLM asla karar motoru olamaz'
        kuralının somut kanıtı (overview.md §6)."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sahte-anahtar")

        tur1 = SimpleNamespace(stop_reason="tool_use", content=[_tool_use_bloğu("skor_getir", {})])
        tur2 = SimpleNamespace(
            stop_reason="end_turn",
            content=[_metin_bloğu("Sana özel 999999 TL limit tanımlandı!")],  # uydurma
        )

        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value.messages.create.side_effect = [tur1, tur2]
            sonuc = danisman_llm.yanitla("limitim ne kadar?", _BAGLAM)

        assert sonuc["mod"] == "kural"
        assert sonuc["anlati_reddedildi"] is True
        # Reddedilen durumda bile deterministik bir yanıt döner (boş kalmaz)
        assert sonuc["yanit"]

    def test_maks_tur_asilirsa_guvenli_fallback(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sahte-anahtar")
        sonsuz_tool_use = SimpleNamespace(stop_reason="tool_use", content=[_tool_use_bloğu("skor_getir", {})])

        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value.messages.create.side_effect = [sonsuz_tool_use] * (danisman_llm.MAKS_TUR + 2)
            sonuc = danisman_llm.yanitla("skorum nedir?", _BAGLAM)

        assert sonuc["mod"] == "kural"
        assert sonuc["anlati_reddedildi"] is True
        assert len(sonuc["arac_cagrilari"]) == danisman_llm.MAKS_TUR

    def test_senaryo_calistir_araci_simulasyon_fn_cagirir(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sahte-anahtar")
        cagrildi = {}

        def sahte_simulasyon(degisiklikler):
            cagrildi["degisiklikler"] = degisiklikler
            return {"senaryo_aks_skor": 800}

        tur1 = SimpleNamespace(
            stop_reason="tool_use",
            content=[_tool_use_bloğu("senaryo_calistir", {"degisiklikler": {"gider_gelir_orani": 0.5}})],
        )
        tur2 = SimpleNamespace(stop_reason="end_turn", content=[_metin_bloğu("Senaryoda skorun 800 olur.")])

        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value.messages.create.side_effect = [tur1, tur2]
            sonuc = danisman_llm.yanitla("gider oranımı düşürsem ne olur?", _BAGLAM, simulasyon_fn=sahte_simulasyon)

        assert cagrildi["degisiklikler"] == {"gider_gelir_orani": 0.5}
        assert sonuc["mod"] == "llm-arac"

    def test_api_hatasinda_kural_moduna_guvenle_duser(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sahte-anahtar")
        with patch("anthropic.Anthropic") as MockAnthropic:
            MockAnthropic.return_value.messages.create.side_effect = RuntimeError("API çöktü")
            sonuc = danisman_llm.yanitla("skorum nedir?", _BAGLAM)
        assert sonuc["mod"] == "kural"
        assert sonuc["yanit"]


class TestGeminiToolCallingAkisi:
    """danisman_llm'in Gemini yolu (§3b Phase 7/7.10) — `google.genai.Client`
    mock'lanır (gerçek API çağrısı YOK), Claude testleriyle BİREBİR aynı
    senaryolar: başarılı araç çağrısı, uydurma-sayı reddi, API hatası. Ayrıca
    iki anahtar birden varsa Claude'un öncelikli olduğu doğrulanır."""

    def test_anthropic_yoksa_gemini_kullanilir(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("GEMINI_API_KEY", "sahte-anahtar")

        tur1 = _gemini_yanit([_gemini_fc_bloğu("skor_getir", {})])
        tur2 = _gemini_yanit([_gemini_metin_bloğu("Skorun 720/850, düşük risk seviyesinde.")])

        with patch("google.genai.Client") as MockClient:
            MockClient.return_value.models.generate_content.side_effect = [tur1, tur2]
            sonuc = danisman_llm.yanitla("skorum nedir?", _BAGLAM)

        assert sonuc["mod"] == "llm-arac"
        assert sonuc["saglayici"] == "gemini"
        assert sonuc["anlati_reddedildi"] is False
        assert "720" in sonuc["yanit"]
        assert len(sonuc["arac_cagrilari"]) == 1
        assert sonuc["arac_cagrilari"][0]["arac"] == "skor_getir"

    def test_gemini_uydurma_sayi_iceren_yanit_reddedilir(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("GEMINI_API_KEY", "sahte-anahtar")

        tur1 = _gemini_yanit([_gemini_fc_bloğu("skor_getir", {})])
        tur2 = _gemini_yanit([_gemini_metin_bloğu("Sana özel 999999 TL limit tanımlandı!")])

        with patch("google.genai.Client") as MockClient:
            MockClient.return_value.models.generate_content.side_effect = [tur1, tur2]
            sonuc = danisman_llm.yanitla("limitim ne kadar?", _BAGLAM)

        assert sonuc["mod"] == "kural"
        assert sonuc["saglayici"] == "gemini"
        assert sonuc["anlati_reddedildi"] is True
        assert sonuc["yanit"]

    def test_gemini_senaryo_calistir_araci_simulasyon_fn_cagirir(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("GEMINI_API_KEY", "sahte-anahtar")
        cagrildi = {}

        def sahte_simulasyon(degisiklikler):
            cagrildi["degisiklikler"] = degisiklikler
            return {"senaryo_aks_skor": 800}

        tur1 = _gemini_yanit([_gemini_fc_bloğu("senaryo_calistir", {"degisiklikler": {"gider_gelir_orani": 0.5}})])
        tur2 = _gemini_yanit([_gemini_metin_bloğu("Senaryoda skorun 800 olur.")])

        with patch("google.genai.Client") as MockClient:
            MockClient.return_value.models.generate_content.side_effect = [tur1, tur2]
            sonuc = danisman_llm.yanitla(
                "gider oranımı düşürsem ne olur?", _BAGLAM, simulasyon_fn=sahte_simulasyon
            )

        assert cagrildi["degisiklikler"] == {"gider_gelir_orani": 0.5}
        assert sonuc["mod"] == "llm-arac"
        assert sonuc["saglayici"] == "gemini"

    def test_gemini_maks_tur_asilirsa_guvenli_fallback(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("GEMINI_API_KEY", "sahte-anahtar")
        sonsuz_tool_use = _gemini_yanit([_gemini_fc_bloğu("skor_getir", {})])

        with patch("google.genai.Client") as MockClient:
            MockClient.return_value.models.generate_content.side_effect = [sonsuz_tool_use] * (danisman_llm.MAKS_TUR + 2)
            sonuc = danisman_llm.yanitla("skorum nedir?", _BAGLAM)

        assert sonuc["mod"] == "kural"
        assert sonuc["saglayici"] == "gemini"
        assert sonuc["anlati_reddedildi"] is True
        assert len(sonuc["arac_cagrilari"]) == danisman_llm.MAKS_TUR

    def test_gemini_api_hatasinda_kural_moduna_guvenle_duser(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("GEMINI_API_KEY", "sahte-anahtar")
        with patch("google.genai.Client") as MockClient:
            MockClient.return_value.models.generate_content.side_effect = RuntimeError("API çöktü")
            sonuc = danisman_llm.yanitla("skorum nedir?", _BAGLAM)
        assert sonuc["mod"] == "kural"
        assert sonuc["saglayici"] == "gemini"
        assert sonuc["yanit"]

    def test_iki_anahtar_da_varsa_claude_oncelikli(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sahte-anahtar")
        monkeypatch.setenv("GEMINI_API_KEY", "sahte-anahtar")

        tur1 = SimpleNamespace(stop_reason="tool_use", content=[_tool_use_bloğu("skor_getir", {})])
        tur2 = SimpleNamespace(stop_reason="end_turn", content=[_metin_bloğu("Skorun 720/850.")])

        with patch("anthropic.Anthropic") as MockAnthropic, patch("google.genai.Client") as MockGeminiClient:
            MockAnthropic.return_value.messages.create.side_effect = [tur1, tur2]
            sonuc = danisman_llm.yanitla("skorum nedir?", _BAGLAM)

        assert sonuc["saglayici"] == "anthropic"
        MockGeminiClient.assert_not_called()


class TestDogrulama:
    def test_arac_ciktisindaki_sayi_kabul_edilir(self):
        assert danisman_llm._dogrula("Skorun 720.", [{"aks_skor": 720}])

    def test_kucuk_sayilar_filtreden_muaf(self):
        assert danisman_llm._dogrula("İşte 3 öneri.", [{}])

    def test_uydurma_buyuk_sayi_reddedilir(self):
        assert not danisman_llm._dogrula("Limitin 999999 TL.", [{"aks_skor": 720}])
