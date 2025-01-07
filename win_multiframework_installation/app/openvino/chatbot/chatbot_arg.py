import torch
import sys
from threading import Event, Thread
from uuid import uuid4
from typing import List, Tuple
import gradio as gr
from transformers import (
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer,
)

from threading import Event, Thread
import time
from pathlib import Path
from optimum.intel.openvino import OVModelForCausalLM
from transformers import AutoConfig, AutoTokenizer
import webbrowser
import openvino as ov
import argparse

core=ov.Core()

max_new_tokens = 256

def initialize_arg_parser():
    """Initialize argument parser for the script."""
    parser = argparse.ArgumentParser(
        description="Detection Example - Tracker with ByteTrack and Supervision"
    )
    parser.add_argument(
        "-m", "--model", help="Path for the HEF model.", default="yolov5m_wo_spp_60p.hef"
    )
    parser.add_argument(
        "-d", "--device", default="input_video.mp4", help="Path to the input video."
    )
    return parser

english_examples = [
    ["Hello there! How are you doing?"],
    ["What is OpenVINO?"],
    ["Who are you?"],
    ["Can you explain to me briefly what is Python programming language?"],
    ["Explain the plot of Cinderella in a sentence."],
    ["What are some common mistakes to avoid when writing code?"],
    ["Write a 100-word blog post on “Benefits of Artificial Intelligence and OpenVINO“"],
]

def request_cancel():
    ov_model.request.cancel()
    
def get_uuid():
    """
    universal unique identifier for thread
    """
    return str(uuid4())

def bot(history, temperature, top_p, top_k, repetition_penalty, conversation_id):
    """
    callback function for running chatbot on submit button click

    Params:
      history: conversation history
      temperature:  parameter for control the level of creativity in AI-generated text.
                    By adjusting the `temperature`, you can influence the AI model's probability distribution, making the text more focused or diverse.
      top_p: parameter for control the range of tokens considered by the AI model based on their cumulative probability.
      top_k: parameter for control the range of tokens considered by the AI model based on their cumulative probability, selecting number of tokens with highest probability.
      repetition_penalty: parameter for penalizing tokens based on how frequently they occur in the text.
      conversation_id: unique conversation identifier.

    """

    # Construct the input message string for the model by concatenating the current system message and conversation history
    # Tokenize the messages string
    input_ids = convert_history_to_token(history)
    if input_ids.shape[1] > 2000:
        history = [history[-1]]
        input_ids = convert_history_to_token(history)
    streamer = TextIteratorStreamer(tok, timeout=30.0, skip_prompt=True, skip_special_tokens=True)
    generate_kwargs = dict(
        input_ids=input_ids,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=temperature > 0.0,
        top_p=top_p,
        top_k=top_k,
        repetition_penalty=repetition_penalty,
        streamer=streamer,
    )
    if stop_tokens is not None:
        generate_kwargs["stopping_criteria"] = StoppingCriteriaList(stop_tokens)

    stream_complete = Event()

    def generate_and_signal_complete():
        """
        genration function for single thread
        """
        global start_time
        ov_model.generate(**generate_kwargs)
        stream_complete.set()

    t1 = Thread(target=generate_and_signal_complete)
    t1.start()

    # Initialize an empty string to store the generated text
    partial_text = ""
    for new_text in streamer:
        partial_text = text_processor(partial_text, new_text)
        history[-1][1] = partial_text
        yield history

def convert_history_to_token(history: List[Tuple[str, str]]):
    """
    function for conversion history stored as list pairs of user and assistant messages to tokens according to model expected conversation template
    Params:
      history: dialogue history
    Returns:
      history in token format
    """
    if pt_model_name == "baichuan2":
        system_tokens = tok.encode(start_message)
        history_tokens = []
        for old_query, response in history[:-1]:
            round_tokens = []
            round_tokens.append(195)
            round_tokens.extend(tok.encode(old_query))
            round_tokens.append(196)
            round_tokens.extend(tok.encode(response))
            history_tokens = round_tokens + history_tokens
        input_tokens = system_tokens + history_tokens
        input_tokens.append(195)
        input_tokens.extend(tok.encode(history[-1][0]))
        input_tokens.append(196)
        input_token = torch.LongTensor([input_tokens])
    elif history_template is None:
        messages = [{"role": "system", "content": start_message}]
        for idx, (user_msg, model_msg) in enumerate(history):
            if idx == len(history) - 1 and not model_msg:
                messages.append({"role": "user", "content": user_msg})
                break
            if user_msg:
                messages.append({"role": "user", "content": user_msg})
            if model_msg:
                messages.append({"role": "assistant", "content": model_msg})

        input_token = tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=True, return_tensors="pt")
    else:
        text = start_message + "".join(
            ["".join([history_template.format(num=round, user=item[0], assistant=item[1])]) for round, item in enumerate(history[:-1])]
        )
        text += "".join(
            [
                "".join(
                    [
                        current_message_template.format(
                            num=len(history) + 1,
                            user=history[-1][0],
                            assistant=history[-1][1],
                        )
                    ]
                )
            ]
        )
        input_token = tok(text, return_tensors="pt", **tokenizer_kwargs).input_ids
    return input_token
    
def user(message, history):
    """
    callback function for updating user messages in interface on submit button click

    Params:
      message: current message
      history: conversation history
    Returns:
      None
    """
    # Append the user's message to the conversation history
    return "", history + [[message, ""]]

DEFAULT_SYSTEM_PROMPT = """\
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.
If a question does not make any sense or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\
"""

DEFAULT_RAG_PROMPT = """\
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.\
"""

def llama_partial_text_processor(partial_text, new_text):
    new_text = new_text.replace("[INST]", "").replace("[/INST]", "")
    partial_text += new_text
    return partial_text

def default_partial_text_processor(partial_text: str, new_text: str):
    """
    helper for updating partially generated answer, used by default

    Params:
      partial_text: text buffer for storing previosly generated text
      new_text: text update for the current step
    Returns:
      updated text string

    """
    partial_text += new_text
    return partial_text


have_model = {
    "tiny-llama-1b-chat": {
            "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            "remote_code": False,
            "start_message": f"<|system|>\n{DEFAULT_SYSTEM_PROMPT}</s>\n",
            "history_template": "<|user|>\n{user}</s> \n<|assistant|>\n{assistant}</s> \n",
            "current_message_template": "<|user|>\n{user}</s> \n<|assistant|>\n{assistant}",
            "rag_prompt_template": f"""<|system|> {DEFAULT_RAG_PROMPT }</s>"""
            + """
            <|user|>
            Question: {input} 
            Context: {context} 
            Answer: </s>
            <|assistant|>""",
            },
    "mpt-7b-chat": {
            "model_id": "mosaicml/mpt-7b-chat",
            "remote_code": False,
            "start_message": f"<|im_start|>system\n {DEFAULT_SYSTEM_PROMPT }<|im_end|>",
            "history_template": "<|im_start|>user\n{user}<im_end><|im_start|>assistant\n{assistant}<|im_end|>",
            "current_message_template": '"<|im_start|>user\n{user}<im_end><|im_start|>assistant\n{assistant}',
            "stop_tokens": ["<|im_end|>", "<|endoftext|>"],
            "rag_prompt_template": f"""<|im_start|>system 
            {DEFAULT_RAG_PROMPT }<|im_end|>"""
            + """
            <|im_start|>user
            Question: {input} 
            Context: {context} 
            Answer: <im_end><|im_start|>assistant""",
            },
    "mistral-7b": {
            "model_id": "mistralai/Mistral-7B-v0.1",
            "remote_code": False,
            "start_message": f"<s>[INST] <<SYS>>\n{DEFAULT_SYSTEM_PROMPT }\n<</SYS>>\n\n",
            "history_template": "{user}[/INST]{assistant}</s><s>[INST]",
            "current_message_template": "{user} [/INST]{assistant}",
            "tokenizer_kwargs": {"add_special_tokens": False},
            "partial_text_processor": llama_partial_text_processor,
            "rag_prompt_template": f"""<s> [INST] {DEFAULT_RAG_PROMPT } [/INST] </s>"""
            + """ 
            [INST] Question: {input} 
            Context: {context} 
            Answer: [/INST]""",
            },
    "zephyr-7b-beta": {
            "model_id": "HuggingFaceH4/zephyr-7b-beta",
            "remote_code": False,
            "start_message": f"<|system|>\n{DEFAULT_SYSTEM_PROMPT}</s>\n",
            "history_template": "<|user|>\n{user}</s> \n<|assistant|>\n{assistant}</s> \n",
            "current_message_template": "<|user|>\n{user}</s> \n<|assistant|>\n{assistant}",
            "rag_prompt_template": f"""<|system|> {DEFAULT_RAG_PROMPT }</s>"""
            + """ 
            <|user|>
            Question: {input} 
            Context: {context} 
            Answer: </s>
            <|assistant|>""",
            },
    "notus-7b-v1": {
            "model_id": "argilla/notus-7b-v1",
            "remote_code": False,
            "start_message": f"<|system|>\n{DEFAULT_SYSTEM_PROMPT}</s>\n",
            "history_template": "<|user|>\n{user}</s> \n<|assistant|>\n{assistant}</s> \n",
            "current_message_template": "<|user|>\n{user}</s> \n<|assistant|>\n{assistant}",
            "rag_prompt_template": f"""<|system|> {DEFAULT_RAG_PROMPT }</s>"""
            + """
            <|user|>
            Question: {input} 
            Context: {context} 
            Answer: </s>
            <|assistant|>""",
            },
    "neural-chat-7b-v3-1": {
            "model_id": "Intel/neural-chat-7b-v3-3",
            "remote_code": False,
            "start_message": f"<s>[INST] <<SYS>>\n{DEFAULT_SYSTEM_PROMPT }\n<</SYS>>\n\n",
            "history_template": "{user}[/INST]{assistant}</s><s>[INST]",
            "current_message_template": "{user} [/INST]{assistant}",
            "tokenizer_kwargs": {"add_special_tokens": False},
            "partial_text_processor": llama_partial_text_processor,
            "rag_prompt_template": f"""<s> [INST] {DEFAULT_RAG_PROMPT } [/INST] </s>"""
            + """
            [INST] Question: {input} 
            Context: {context} 
            Answer: [/INST]""",
            },
}


def open_web():
    time.sleep(1)
    #edge_path="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    #webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
    webbrowser.open_new("http://127.0.0.1:7860")
    
#model_list=["tiny-llama-1b-chat","mpt-7b-chat","mistral-7b","zephyr-7b-beta","notus-7b-v1","neural-chat-7b-v3-1"]
model_list=["tiny-llama-1b-chat"]

def main(argv):
    global model_id,model_name,start_message,history_template,current_message_template,stop_tokens,tokenizer_kwargs,pt_model_name
    global tok,ov_model,text_processor
    
    # print("select you wanted model:\n")
    # for i in range(0,len(model_list)):
    #     print(str(i) +" : "   + model_list[i])
    # model_sel=int(input())
    model_sel=0
    model_id=model_list[model_sel]
    model_configuration=have_model[str(model_list[model_sel])]

    model_name = model_configuration["model_id"]
    start_message = model_configuration["start_message"]
    history_template = model_configuration.get("history_template")
    current_message_template = model_configuration.get("current_message_template")
    stop_tokens = model_configuration.get("stop_tokens")
    tokenizer_kwargs = model_configuration.get("tokenizer_kwargs", {})

    # int4_model_dir=Path(str(model_list[model_sel]))/ "INT4_compressed_weights"
    int4_model_dir=argv.model

    pt_model_name = model_list[model_sel].split("-")[0]

    ov_config = {"PERFORMANCE_HINT": "LATENCY", "NUM_STREAMS": "1", "CACHE_DIR": ""}
    model_dir=int4_model_dir
    
    examples = english_examples
    tok = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
    text_processor = model_configuration.get("partial_text_processor", default_partial_text_processor)
    # while(1):
    #     print("Select you wanted running device:")
    #     detect=core.available_devices
    #     index=1
    #     device_dict={}
    #     for i in detect:
    #         print(str(index)+"."+str(i))
    #         device_dict[str(index)]=str(i)
    #         index+=1
    #     print(str(index)+"."+"AUTO")
    #     device_dict[str(index)]="AUTO"
    
    #     sel_dev=input()
    #     if(int(sel_dev)>0 and int(sel_dev) <= index):
    #         print("select " +device_dict[str(sel_dev)]+ " to running" )
    #         break
    #     else:
    #         os.system("cls")
    #         print("Not invild input!!!!!!!!!!!!!!!!!")
            
    ov_model = OVModelForCausalLM.from_pretrained(
    model_dir,
    device=argv.device,
    ov_config=ov_config,
    config=AutoConfig.from_pretrained(model_dir, trust_remote_code=True),
    trust_remote_code=True,
    )
    
    with gr.Blocks(
        theme=gr.themes.Soft(),
        css=".disclaimer {font-variant-caps: all-small-caps;}",
    ) as demo:
        conversation_id = gr.State(get_uuid)
        gr.Markdown(f"""<h1><center>OpenVINO {model_id} Chatbot</center></h1>""")
        chatbot = gr.Chatbot(height=500)
        with gr.Row():
            with gr.Column():
                msg = gr.Textbox(
                    label="Chat Message Box",
                    placeholder="Chat Message Box",
                    show_label=False,
                    container=False,
                )
            with gr.Column():
                with gr.Row():
                    submit = gr.Button("Submit")
                    stop = gr.Button("Stop")
                    clear = gr.Button("Clear")
        with gr.Row():
            with gr.Accordion("Advanced Options:", open=False):
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            temperature = gr.Slider(
                                label="Temperature",
                                value=0.1,
                                minimum=0.0,
                                maximum=1.0,
                                step=0.1,
                                interactive=True,
                                info="Higher values produce more diverse outputs",
                            )
                    with gr.Column():
                        with gr.Row():
                            top_p = gr.Slider(
                                label="Top-p (nucleus sampling)",
                                value=1.0,
                                minimum=0.0,
                                maximum=1,
                                step=0.01,
                                interactive=True,
                                info=(
                                    "Sample from the smallest possible set of tokens whose cumulative probability "
                                    "exceeds top_p. Set to 1 to disable and sample from all tokens."
                                ),
                            )
                    with gr.Column():
                        with gr.Row():
                            top_k = gr.Slider(
                                label="Top-k",
                                value=50,
                                minimum=0.0,
                                maximum=200,
                                step=1,
                                interactive=True,
                                info="Sample from a shortlist of top-k tokens — 0 to disable and sample from all tokens.",
                            )
                    with gr.Column():
                        with gr.Row():
                            repetition_penalty = gr.Slider(
                                label="Repetition Penalty",
                                value=1.1,
                                minimum=1.0,
                                maximum=2.0,
                                step=0.1,
                                interactive=True,
                                info="Penalize repetition — 1.0 to disable.",
                            )
        gr.Examples(examples, inputs=msg, label="Click on any example and press the 'Submit' button")

        submit_event = msg.submit(
            fn=user,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
            queue=False,
        ).then(
            fn=bot,
            inputs=[
                chatbot,
                temperature,
                top_p,
                top_k,
                repetition_penalty,
                conversation_id,
            ],
            outputs=chatbot,
            queue=True,
        )
        submit_click_event = submit.click(
            fn=user,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
            queue=False,
        ).then(
            fn=bot,
            inputs=[
                chatbot,
                temperature,
                top_p,
                top_k,
                repetition_penalty,
                conversation_id,
            ],
            outputs=chatbot,
            queue=True,
        )
        stop.click(
            fn=request_cancel,
            inputs=None,
            outputs=None,
            cancels=[submit_event, submit_click_event],
            queue=False,
        )
        clear.click(lambda: None, None, chatbot, queue=False)

    # if you are launching remotely, specify server_name and server_port
    #  demo.launch(server_name='your server name', server_port='server port in int')
    # if you have any issue to launch on your platform, you can pass share=True to launch method:
    # demo.launch(share=True)
    # it creates a publicly shareable link for the interface. Read more in the docs: https://gradio.app/docs/
    t=Thread(target=open_web)
    t.start()
    demo.launch(server_name="127.0.0.1",server_port=7860)



if __name__ == "__main__":
    args = initialize_arg_parser().parse_args()
    main(args)
