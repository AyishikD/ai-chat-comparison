import gradio as gr
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer
)
import torch
from threading import Thread

# Smaller + faster model for free CPU Spaces
model_id = "Qwen/Qwen2.5-0.5B-Instruct"

# Device selection
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Using device: {device}")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    model_id,
    trust_remote_code=True
)

# Load model
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    dtype=torch.float32 if device == "cpu" else torch.float16,
    low_cpu_mem_usage=True
).to(device)

model.eval()


def chat_logic(message, history, system_prompt):

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Compatible with older gradio history format
    # history = [(user_message, assistant_message), ...]

    for user_msg, assistant_msg in history:

        messages.append({
            "role": "user",
            "content": user_msg
        })

        messages.append({
            "role": "assistant",
            "content": assistant_msg
        })

    messages.append({
        "role": "user",
        "content": message
    })

    try:

        # Convert chat to prompt
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Tokenize
        inputs = tokenizer(
            text,
            return_tensors="pt"
        ).to(device)

        # Streamer
        streamer = TextIteratorStreamer(
            tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )

        # Generation settings
        generation_kwargs = {
            **inputs,
            "streamer": streamer,
            "max_new_tokens": 64,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "pad_token_id": tokenizer.eos_token_id
        }

        # Run generation in separate thread
        thread = Thread(
            target=model.generate,
            kwargs=generation_kwargs
        )

        thread.start()

        partial_text = ""

        # Stream output
        for new_text in streamer:
            partial_text += new_text
            yield partial_text

    except Exception as e:
        yield f"Error: {str(e)}"


# UI
with gr.Blocks() as demo:

    gr.Markdown("# Qwen Chatbot")

    system_prompt = gr.Textbox(
        value="You are a helpful AI assistant.",
        label="System Prompt",
        visible=False
    )

    gr.ChatInterface(
        fn=chat_logic,
        additional_inputs=[system_prompt]
    )

# Launch app
if __name__ == "__main__":
    demo.launch()