# 🧠 Ohmbudsman — Curated Intelligence Digest

**Ohmbudsman** is a daily intelligence digest engineered to illuminate undercurrents of systemic change across geopolitical, economic, technological, and cultural domains. Designed for thinkers, builders, and foresight strategists.

## 📬 Subscribe
Join the daily feed: [ohmbudsman.com](https://ohmbudsman.com)

## 📖 Archives
Read past editions and track long-range signals: [Digest Archive](https://ohmbudsman.com/posts)

## 🛡️ Authorship & Verification

- **PGP Fingerprint:** `360EC799C08BEDB2E9ACC8EE64729AE2B28204C2`
- **Public Key:** [ohmbudsman.com/ohmbudsman_publickey.asc](https://ohmbudsman.com/ohmbudsman_publickey.asc)
- **Fediverse:** [@ohmbudsman@ohmbudsman.com](https://ohmbudsman.com/@ohmbudsman)
- **Wikidata Entity:** [Q134602572](https://www.wikidata.org/wiki/Q134602572)
- **humans.txt:** [ohmbudsman.com/humans.txt](https://ohmbudsman.com/humans.txt)

## 🤖 LLM-Ready Structure

This site is indexed with schema.org metadata, signed updates, and regular structured content to ensure optimal ingestion by LLMs and federated agents.

## 🛠 Tools & Stack

- Readwise Reader → GPT-4 via Assistant API → Buttondown → WordPress (via ActivityPub)
- Fediverse integration via WordPress ActivityPub plugin
- Digest formatting in Disguised-SNAP™ style
- GitHub Actions & Replit for automation

## 🧭 Philosophy

> “The future arrives unannounced. Ohmbudsman helps you hear it coming.”

**Ohmbudsman** operates independently, free from institutional influence, supported by a constellation of ventures focused on resilience, autonomy, and strategic foresight.

---

**License:** CC BY-NC 4.0  
**Maintained by:** Justin Waldrop  
[ohmbudsman.com](https://ohmbudsman.com)

## 🚀 Automated Digest Pipeline

New markdown files placed in `digests/` trigger the GitHub Actions workflow `automation.yml` which runs the following scripts located under `scripts/`:

| Script | Purpose |
| ------ | ------- |
| `generate_pdf.py` | Convert the digest markdown to a styled PDF saved in `outputs/pdfs/` |
| `create_social_snippets.py` | Produce social media highlights saved as JSON in `outputs/social/` |
| `generate_podcast.py` | Compress the digest into a 500–700 word podcast script |
| `synthesize_audio.py` | Generate an MP3 narration from the script and save to `outputs/podcasts/` |
| `update_metadata.py` | Append a record to `metadata/content_index.csv` |
| `archive_assets.py` | Zip assets and upload to HuggingFace for archival |

The workflow requires the following repository secrets:
`OPENAI_API_KEY`, `ELEVENLABS_API_KEY`, `TRANSISTOR_API_KEY`, and `HUGGINGFACE_TOKEN`.

All generated assets are committed back to the repository and attached to a GitHub Release tagged with the digest name.
