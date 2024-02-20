import sys
import gradio as gr
from scipy.io import wavfile

LIST_FILE = sys.argv[1]
with open(LIST_FILE, 'rt', encoding='utf-8') as f:
    CONTENT = f.read().strip().split('\n')
    
def get_line(idx):
    global CONTENT
    line = CONTENT[idx]
    splits = line.split('|')
    audio_path, text = splits[0], splits[3]
    return audio_path, text

def add1(idx):
    return idx + 1

def save_list():
    global LIST_FILE
    print(f'Saving file to {LIST_FILE}')
    with open(LIST_FILE, 'wt', encoding='utf-8') as f:
        f.write('\n'.join(CONTENT))

def update_text(text, idx):
    global CONTENT
    ori = CONTENT[idx]
    ori_splits = ori.split('|')
    if ori_splits[3] != text:
        ori_splits[3] = text
        new_line = '|'.join(ori_splits)
        CONTENT[idx] = new_line
        save_list()

def update_audio(audio, idx):
    global CONTENT
    ori = CONTENT[idx]
    ori_splits = ori.split('|')
    audio_path = ori_splits[0]
    sr, data = wavfile.read(audio_path)
    if data.shape[0] != audio[1].shape[0]:
        print(f'Saving file to {audio_path}')
        wavfile.write(audio_path, audio[0], audio[1])


def delete_idx(idx):
    global CONTENT
    CONTENT.pop(idx)
    save_list()

def update_slider(idx):
    global CONTENT
    return gr.Slider(minimum=0, maximum=len(CONTENT) - 1, value=idx, step=1)

# TODO: Add Stats, distribution

if __name__ == '__main__':
    with gr.Blocks() as app:
        au0, text0 = get_line(0)
        audio = gr.Audio(au0, interactive=True, autoplay=True)
        with gr.Row():
            text = gr.Textbox(text0)
            delete = gr.Button('Delete')
        progress = gr.Slider(minimum=0, maximum=len(CONTENT) - 1, value=0, step=1)

        progress.change(get_line, inputs=progress, outputs=[audio, text])


        delete.click(delete_idx, inputs=[progress])
        delete.click(get_line, inputs=[progress], outputs=[audio, text])
        # TODO: Not correctly updated. 
        delete.click(update_slider, inputs=progress, outputs=[progress])

        text.submit(update_text, inputs=[text, progress])
        text.submit(update_audio, inputs=[audio, progress])
        text.submit(add1, inputs=[progress], outputs=progress)


    app.launch(inbrowser=True)