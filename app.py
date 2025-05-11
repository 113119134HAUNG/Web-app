# app.py

import gradio as gr
from config import PROMPT_PRESETS
from inference import generate_image


def main():
    with gr.Blocks(css="""
        body {background-color: #f5f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
        .header {font-size: 2.5rem; font-weight: 700; color: #4a90e2; margin-bottom: 0.2rem;}
        .subheader {font-size: 1.1rem; color: #666; margin-bottom: 1.5rem;}
        .input-box, .output-box {
            background: white; 
            border-radius: 10px; 
            padding: 20px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .gr-button {background-color: #4a90e2 !important; color: white !important; font-weight: 600;}
        .gr-button:hover {background-color: #357ABD !important;}
        .footer {font-size: 0.8rem; color: #999; margin-top: 20px; text-align: center;}
    """) as demo:

        with gr.Row():
            with gr.Column():
                gr.Markdown(
                    """
                    <div class="header">  國安的自訂義：Stable Diffusion 3 圖像生成</div>
                    <div class="subheader">
                    ⚠️ <b>注意：</b>生成內容請自行承擔合規風險，請勿輸入違法、不當描述。
                    </div>
                    """, 
                    elem_id="page-header"
                )

        with gr.Row():
            with gr.Column(scale=6):
                with gr.Box(elem_classes="input-box"):
                    txt_prompt = gr.Textbox(
                        label="請輸入 Prompt",
                        placeholder="例如：A dragon flying over mountains",
                        lines=3,
                        max_lines=6,
                        interactive=True,
                        elem_id="prompt-input"
                    )
                    style = gr.Dropdown(
                        choices=list(PROMPT_PRESETS.keys()),
                        label="選擇風格",
                        value=list(PROMPT_PRESETS.keys())[0],
                        interactive=True
                    )
                    with gr.Row():
                        width = gr.Slider(
                            minimum=512, maximum=1024, step=64, value=768,
                            label="圖片寬度 (px)",
                            interactive=True
                        )
                        height = gr.Slider(
                            minimum=512, maximum=1024, step=64, value=768,
                            label="圖片高度 (px)",
                            interactive=True
                        )
                    seed = gr.Number(
                        label="隨機種子 (Seed)",
                        value=42,
                        precision=0,
                        interactive=True
                    )
                    btn = gr.Button("生成圖片", variant="primary", elem_id="generate-btn")

            with gr.Column(scale=6):
                with gr.Box(elem_classes="output-box"):
                    img = gr.Image(label="輸出圖像", interactive=False)
                    stats = gr.Textbox(label="系統訊息", interactive=False, lines=2)

        def on_generate(prompt, style, width, height, seed):
            if not prompt.strip():
                return None, "請輸入有效的 Prompt。"
            if width % 64 != 0 or height % 64 != 0:
                return None, "寬度與高度必須是 64 的倍數。"
            try:
                seed_int = int(seed)
            except Exception:
                return None, "隨機種子必須是整數。"

            image, message = generate_image(prompt, style, int(width), int(height), seed_int)
            return image, message

        btn.click(
            fn=on_generate,
            inputs=[txt_prompt, style, width, height, seed],
            outputs=[img, stats],
            show_progress=True
        )

        with gr.Row():
            with gr.Column():
                gr.Markdown(
                    """
                    <div class="footer">
                    © 2025 國安的自訂義平台 | Powered by Stable Diffusion 3 & Gradio
                    </div>
                    """
                )

    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)

if __name__ == "__main__":
    main()