"""
app.py — SIFRA
Gradio web interface for the dangerous goods compliance assistant.

Run with:
    python app.py
"""

import gradio as gr
from rag import load_chain, query_compliance

# Load RAG chain once at startup
print("Loading SIFRA...")
try:
    chain = load_chain()
    print("✅ SIFRA ready.")
except FileNotFoundError as e:
    print(f"❌ {e}")
    chain = None

TRANSPORT_MODES = ["Road (ADR)", "Sea (IMDG)", "Air (IATA DGR)"]

EXAMPLES = [
    ["Acetone", "Road (ADR)"],
    ["Lithium batteries", "Air (IATA DGR)"],
    ["Diesel fuel", "Sea (IMDG)"],
    ["Ethanol", "Road (ADR)"],
    ["Paint", "Sea (IMDG)"],
]


def check_compliance(chemical: str, transport_mode: str) -> tuple:
    if not chemical.strip():
        return "⚠️ Please enter a chemical name or UN number.", ""

    if chain is None:
        return (
            "❌ Vector store not loaded. Run `python ingest.py` first.",
            "",
        )

    try:
        result = query_compliance(chemical.strip(), transport_mode, chain)
        answer = result["answer"]
        sources_text = f"📚 Sources consulted: {', '.join(result['sources'])} ({result['num_chunks']} chunks retrieved)"
        return answer, sources_text
    except Exception as e:
        return f"❌ Error: {str(e)}", ""


# ── UI ──────────────────────────────────────────────────────────────────────

with gr.Blocks(
    title="SIFRA — Dangerous Goods Compliance",
    theme=gr.themes.Base(
        primary_hue="blue",
        neutral_hue="slate",
    ),
    css="""
    .verdict-box { font-family: monospace; font-size: 14px; }
    #title { text-align: center; margin-bottom: 8px; }
    #subtitle { text-align: center; color: #64748b; margin-bottom: 24px; }
    """,
) as demo:

    gr.Markdown("# 🚛 SIFRA", elem_id="title")
    gr.Markdown(
        "**Shipment Intelligence for Regulatory Compliance** — ADR · IMDG · IATA DGR",
        elem_id="subtitle",
    )

    with gr.Row():
        with gr.Column(scale=1):
            chemical_input = gr.Textbox(
                label="Chemical Name or UN Number",
                placeholder="e.g. Acetone  or  UN1090",
                lines=1,
            )
            mode_input = gr.Dropdown(
                label="Transport Mode",
                choices=TRANSPORT_MODES,
                value="Road (ADR)",
            )
            submit_btn = gr.Button("Check Compliance", variant="primary")

            gr.Examples(
                examples=EXAMPLES,
                inputs=[chemical_input, mode_input],
                label="Quick Examples",
            )

        with gr.Column(scale=2):
            output_box = gr.Textbox(
                label="Compliance Report",
                lines=16,
                interactive=False,
                elem_classes=["verdict-box"],
            )
            sources_box = gr.Textbox(
                label="Sources",
                lines=1,
                interactive=False,
            )

    submit_btn.click(
        fn=check_compliance,
        inputs=[chemical_input, mode_input],
        outputs=[output_box, sources_box],
    )
    chemical_input.submit(
        fn=check_compliance,
        inputs=[chemical_input, mode_input],
        outputs=[output_box, sources_box],
    )

    gr.Markdown(
        """
        ---
        ⚠️ **Disclaimer:** SIFRA is an AI assistant for educational purposes.
        Always verify compliance with official regulatory sources before shipping dangerous goods.
        
        *ECS Data Science & AI Program — Capstone 2026 · Deniz Tosunoglu*
        """
    )

if __name__ == "__main__":
    demo.launch(share=False)
