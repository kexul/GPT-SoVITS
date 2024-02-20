import os
import random
import gradio as gr

from pathlib import Path

from inference_webui import get_tts_wav, GPT_names, SoVITS_names, \
    change_choices, change_gpt_weights, change_sovits_weights, \
    custom_sort_key, gpt_path, sovits_path, cut5

from tools.i18n.i18n import I18nAuto

i18n = I18nAuto()

def get_random_ref(list_file, wav_dir):
    with open(list_file, 'rt', encoding='utf-8') as f:
        content = f.read().strip().split('\n')
    line = random.choice(content).split('|')
    audio_path, language, text = line[0], line[2], line[3]
    if Path(audio_path).exists():
        return audio_path, i18n('中文'), text, audio_path
    else:
        if Path(wav_dir).exists():
            audio_path = os.path.join(wav_dir, Path(audio_path).name)
            return audio_path, i18n('中文'), text, audio_path
        else:
            raise ValueError('Path not exist.')
    


with gr.Blocks() as app:
    with gr.Row():
        GPT_dropdown = gr.Dropdown(label=i18n("GPT模型列表"), choices=sorted(GPT_names, key=custom_sort_key), value=gpt_path, interactive=True)
        SoVITS_dropdown = gr.Dropdown(label=i18n("SoVITS模型列表"), choices=sorted(SoVITS_names, key=custom_sort_key), value=sovits_path, interactive=True)
        refresh_button = gr.Button(i18n("刷新模型路径"))

    refresh_button.click(fn=change_choices, inputs=[], outputs=[SoVITS_dropdown, GPT_dropdown])
    SoVITS_dropdown.change(change_sovits_weights, [SoVITS_dropdown], [])
    GPT_dropdown.change(change_gpt_weights, [GPT_dropdown], [])

    with gr.Row():
        inp_text = gr.Textbox(label="*文本标注文件",interactive=True)
        inp_wav_dir = gr.Textbox(label="*训练集音频文件目录",interactive=True)
        random_btn = gr.Button('随机')

    with gr.Row():
        random_audio = gr.Audio(label='音频', autoplay=True)
        inp_ref = gr.Textbox(visible=False)
        prompt_language = gr.Textbox(label='语言')
        prompt_text = gr.Textbox(label='文本')

    random_btn.click(get_random_ref, inputs=[inp_text, inp_wav_dir],
                                     outputs=[random_audio, prompt_language, prompt_text, inp_ref])
    
    with gr.Row():
        text = gr.Textbox(label=i18n("需要合成的文本"), value="")
    with gr.Row():
        cut_btn = gr.Button('Cut')
        top_k = gr.Slider(minimum=1,maximum=100,step=1,label=i18n("top_k"),value=5,interactive=True)
        top_p = gr.Slider(minimum=0,maximum=1,step=0.05,label=i18n("top_p"),value=1,interactive=True)
        temperature = gr.Slider(minimum=0,maximum=1,step=0.05,label=i18n("temperature"),value=1,interactive=True)
    
    cut_btn.click(cut5, inputs=text, outputs=text)

    inference_button = gr.Button(i18n("合成语音"))
    output = gr.Audio(label=i18n("输出的语音"), autoplay=True)
    
    inference_button.click(
        get_tts_wav,
        [inp_ref, prompt_text, prompt_language, text, top_k, top_p, temperature],
        [output],
    )


app.queue().launch(
    server_name="0.0.0.0",
    inbrowser=True,
    quiet=True,
)