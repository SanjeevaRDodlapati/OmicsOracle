"""Tests for PMC PDF URL validation."""

import pytest

from omics_oracle_v2.lib.pipelines.url_collection.sources.oa_sources import \
    pmc_client


class FakeResponse:
    def __init__(self, content_type: str):
        self.status = 200
        self.headers = {"Content-Type": content_type}


class FakeRequestContext:
    def __init__(self, response: FakeResponse):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc_value, traceback):
        return None


class FakeSession:
    def __init__(self, content_type: str):
        self.content_type = content_type

    def head(self, *args, **kwargs):
        return FakeRequestContext(FakeResponse(self.content_type))


@pytest.mark.asyncio
async def test_direct_pdf_rejects_html_interstitial():
    pmc_client._ensure_imports()
    client = pmc_client.PMCClient(pmc_client.PMCConfig())
    client.session = FakeSession("text/html; charset=utf-8")

    result = await client._try_direct_pdf("10166353")

    assert result.success is False


@pytest.mark.asyncio
async def test_europepmc_accepts_pdf_content_type():
    pmc_client._ensure_imports()
    client = pmc_client.PMCClient(pmc_client.PMCConfig())
    client.session = FakeSession("application/pdf")

    result = await client._try_europepmc("10166353")

    assert result.success is True
    assert result.metadata["pattern"] == "europepmc"
