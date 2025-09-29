# fmt: off
import pathlib
import xml.etree.ElementTree as ET

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]


def test_robots_and_sitemap_placeholders():
    robots = (REPO_ROOT / "frontend" / "robots.txt").read_text(encoding="utf-8")
    assert "Sitemap: https://crm.example.com/sitemap.xml" in robots
    # Ensure we are disallowing internal pages but allow root
    assert "Disallow: /login.html" in robots
    assert "Allow: /" in robots

    sitemap_path = REPO_ROOT / "frontend" / "sitemap.xml"
    xml_text = sitemap_path.read_text(encoding="utf-8")
    # Basic XML sanity
    root = ET.fromstring(xml_text)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [loc.text for loc in root.findall("sm:url/sm:loc", ns)]
    assert "https://crm.example.com/" in urls
    assert "https://crm.example.com/index.html" in urls


def test_index_html_canonical_and_og_url():
    index_path = REPO_ROOT / "frontend" / "index.html"
    text = index_path.read_text(encoding="utf-8")
    # crude checks without parsing HTML
    assert "<link rel=\"canonical\" href=\"https://crm.example.com/\">" in text
    assert "<meta property=\"og:url\" content=\"https://crm.example.com/\">" in text
# fmt: on
