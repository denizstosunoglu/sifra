# 🚛 SIFRA
### Shipment Intelligence for Regulatory Compliance

SIFRA is a RAG-powered dangerous goods compliance assistant for road transport under **ADR 2025**. It answers two operational questions that shippers face every day:

1. **Is this substance compliant for road transport, and what documents do I need?**
2. **Can these two substances be loaded together in the same transport unit?**

Built with a 3-layer architecture that combines a deterministic regulatory lookup with retrieval-augmented generation — so classifications are verifiable, not hallucinated.

---

## Demo

**Compliance Check** — enter a chemical name or UN number, get a full compliance report with UN number, hazard class, packing group, tunnel code, and required documents.

**Segregation Check** — enter two substances, find out if they can travel together (🟢 OK / 🟡 CAUTION / 🔴 FORBIDDEN) based on ADR mixed-loading rules.

---

## Architecture

SIFRA uses three layers working together:

**Layer 1 — Deterministic lookup (ADR Table A):** A verified reference set of common dangerous goods with their exact UN numbers, hazard classes, packing groups, labels, limited-quantity thresholds, and tunnel codes. This layer guarantees classification accuracy — no hallucination.

**Layer 2 — RAG retrieval (ADR 2025 full text):** The complete ADR 2025 regulation (both volumes, ~1,340 pages) is chunked and embedded into a FAISS vector store. Relevant regulatory passages are retrieved for transport conditions, documentation requirements, and exemptions.

**Layer 3 — LLM synthesis:** A large language model combines the verified facts (Layer 1) with the retrieved context (Layer 2) to produce a clear, structured compliance report. Every classification carries a ✅ *Verified against ADR Table A* badge.

For segregation, a compatibility matrix based on ADR 7.5.2 mixed-loading provisions determines whether two hazard classes can be transported together, with special handling for acid/base combinations.

---

## Tech Stack

| Layer | Tool |
|---|---|
| LLM | Llama 3.1 8B Instant (via Groq API) |
| Embeddings | all-MiniLM-L6-v2 (sentence-transformers) |
| Vector store | FAISS |
| RAG framework | LangChain |
| UI | Gradio |
| Environment | Google Colab |
| Language | Python 3 |

---

## Results

The key contribution of SIFRA is **eliminating classification hallucination**. A pure RAG+LLM approach can usually retrieve the right UN number, but its output is inconsistent and unverifiable — it sometimes returns multiple candidate UN numbers, hedges with "not in the text but general knowledge," or reformats classifications unpredictably. For an operational compliance tool, that ambiguity is unacceptable.

SIFRA's deterministic Table A layer removes this failure mode: every classification (UN number, hazard class, packing group) is looked up against a verified reference and carries a *✅ Verified against ADR Table A* badge. The result is a single, exact, traceable answer every time.

---

## How to Run

SIFRA runs in **Google Colab** — no local install needed:

1. Open `SIFRA.ipynb` in Google Colab
2. Add your Groq API key to Colab Secrets (🔑 icon) as `GROQ_API_KEY` — get a free key at [groq.com](https://groq.com)
3. Place the ADR 2025 PDFs in a Google Drive folder named `SIFRA`:
   - `2412006_E_ECE_TRANS_352_Vol.I_WEB_0.pdf` ([Volume 1](https://unece.org/transport/documents/2025/01/standards/adr-2025-volume-1))
   - `2412010_E_ECE_TRANS_352_Vol.II_WEB.pdf` ([Volume 2](https://unece.org/transport/documents/2025/01/standards/adr-2025-volume-2))
4. Run the cells in order (top to bottom). The first run builds the FAISS vector store from the PDFs and saves it to your Drive; on later runs it loads the saved store directly, so indexing only happens once.
5. Click the public Gradio link at the bottom to use SIFRA.

---

## Data Sources

- **ADR 2025** (Agreement concerning the International Carriage of Dangerous Goods by Road), UNECE — publicly available regulatory text
- **ADR Table A reference set** — compiled classification data for 40 common dangerous goods

PDFs are not included in this repository due to size; download links are provided above.

---

## Known Limitations

- The deterministic layer covers 40 common substances; a production version would need the full ADR Table A (~3,500 entries)
- Coverage is limited to **road transport (ADR)**; sea (IMDG) and air (IATA DGR) are not yet included
- The segregation matrix implements core ADR 7.5.2 principles but not every special provision
- Not a substitute for a certified Dangerous Goods Safety Advisor (DGSA)

## Next Steps

- Expand the deterministic layer to the full ADR Table A
- Add IMDG (sea) and IATA DGR (air) transport modes
- Add multi-substance load planning (more than two items)

---

## License

MIT — see [LICENSE](LICENSE)

---

*ECS Data Science & AI Program — Capstone Project · 2026*
*Deniz Tosunoglu*
