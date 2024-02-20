import os
import random
import string
import gradio as gr

from pathlib import Path
from scipy.io import wavfile

from inference_webui import get_tts_wav, GPT_names, SoVITS_names, \
    change_choices, change_gpt_weights, change_sovits_weights, \
    custom_sort_key, gpt_path, sovits_path, cut5

from tools.i18n.i18n import I18nAuto

i18n = I18nAuto()

def get_random_ref(list_file, wav_dir, speech_speed):
    with open(list_file, 'rt', encoding='utf-8') as f:
        content = f.read().strip().split('\n')

    audio_speeds = []
    filtered_content = []
    for line in content:
        splits = line.split('|')
        audio_path, lang, text = splits[0], splits[2], splits[3]
        sr, wav_arr = wavfile.read(audio_path)
        wav_duration = wav_arr.shape[0] / sr
        if wav_duration < 10:
            text_without_punctuation = text.translate(str.maketrans('', '', string.punctuation))
            audio_speed = len(text_without_punctuation) / wav_duration
            audio_speeds.append(audio_speed)
            filtered_content.append(line)

    sorted_content = [x for _, x in sorted(zip(audio_speeds, filtered_content))]
    roi = sorted_content[int((speech_speed - 1) / 5 * len(filtered_content)): int((speech_speed) / 5 * len(filtered_content))]
    line = random.choice(roi).split('|')
    audio_path, language, text = line[0], line[2], line[3]
    if Path(audio_path).exists():
        return audio_path, i18n('中文'), text, audio_path
    else:
        if Path(wav_dir).exists():
            audio_path = os.path.join(wav_dir, Path(audio_path).name)
            return audio_path, i18n('中文'), text, audio_path
        else:
            raise ValueError('Path not exist.')

def save_inp_text(input_path, file_name):
    with open(file_name, 'wt', encoding='utf-8') as f:
        f.write(input_path)

def load_inp_text(file_name):
    if Path(file_name).exists():
        inp_path = Path(file_name).read_text()
        return inp_path
    else:
        return None


with gr.Blocks() as app:
    with gr.Row():
        GPT_dropdown = gr.Dropdown(label=i18n("GPT模型列表"), choices=sorted(GPT_names, key=custom_sort_key), value=gpt_path, interactive=True)
        SoVITS_dropdown = gr.Dropdown(label=i18n("SoVITS模型列表"), choices=sorted(SoVITS_names, key=custom_sort_key), value=sovits_path, interactive=True)
        refresh_button = gr.Button(i18n("刷新模型路径"))

    refresh_button.click(fn=change_choices, inputs=[], outputs=[SoVITS_dropdown, GPT_dropdown])
    SoVITS_dropdown.change(change_sovits_weights, [SoVITS_dropdown], [])
    GPT_dropdown.change(change_gpt_weights, [GPT_dropdown], [])

    with gr.Row():
        inp_text = gr.Textbox(label="*文本标注文件",interactive=True, value=load_inp_text('inp_text.txt'))
        inp_wav_dir = gr.Textbox(label="*训练集音频文件目录",interactive=True, value=load_inp_text('inp_wav.txt'))
        speech_speed = gr.Slider(minimum=1, maximum=5, value=3, step=1)
        random_btn = gr.Button('随机')

    with gr.Row():
        random_audio = gr.Audio(label='音频', autoplay=True, interactive=True)
        inp_ref = gr.Textbox(visible=False)
        prompt_language = gr.Textbox(label='语言')
        prompt_text = gr.Textbox(label='文本')

    inp_text.change(save_inp_text, inputs=[inp_text, gr.Text('inp_text.txt', visible=False)])
    inp_wav_dir.change(save_inp_text, inputs=[inp_wav_dir, gr.Text('inp_wav.txt', visible=False)])
    random_btn.click(get_random_ref, inputs=[inp_text, inp_wav_dir, speech_speed],
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