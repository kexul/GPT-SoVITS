import sys
import gradio as gr
import numpy as np
import pandas as pd
from scipy.io import wavfile
from difflib import Differ

LIST_FILE = sys.argv[1]
with open(LIST_FILE, 'rt', encoding='utf-8') as f:
    CONTENT = f.read().strip().split('\n')
ORIGINAL = '\n'.join(CONTENT)
    
def get_line(idx):
    global CONTENT
    line = CONTENT[idx]
    splits = line.split('|')
    audio_path, text = splits[0], splits[3]
    return audio_path, text

def save_list():
    global LIST_FILE
    print(f'Saving file to {LIST_FILE}')
    with open(LIST_FILE, 'wt', encoding='utf-8') as f:
        f.write('\n'.join(CONTENT))

def diff_text():
    global CONTENT
    global ORIGINAL
    d = Differ()
    current = '\n'.join(CONTENT)
    diff_result = []
    for token in d.compare(ORIGINAL, current):
        if token[0] != " ":
            diff_result.append((token[2:], token[0]))
        else:
            diff_result.append((token[2:], None))
    return diff_result

def get_durations():
    global CONTENT
    lens = []
    for line in CONTENT:
        splits = line.split('|')
        audio_path = splits[0]
        sr, data = wavfile.read(audio_path)
        audio_len = data.shape[0]/sr
        lens.append(audio_len)
    total_len = sum(lens) 
    hist, bins = np.histogram(lens, bins=10)
    xs, ys = [], []
    for idx, item in enumerate(hist):
        ys.append(item)
        xs.append(f'{bins[idx]:.1f}~{bins[idx+1]:.1f}')
    df = pd.DataFrame.from_dict({'duration':xs, 'samples':ys})
    return df, total_len



def update_control(audio, text, idx):
    global CONTENT
    if not text:
        CONTENT.pop(idx)
        save_list()
        audio_path, text = get_line(idx)
        new_slider = gr.Slider(minimum=0, maximum=len(CONTENT) - 1, value=idx, step=1)
        diffs = diff_text()
        return audio_path, text, new_slider, diffs

    ori = CONTENT[idx]
    ori_splits = ori.split('|')
    if ori_splits[3] != text:
        ori_splits[3] = text
        new_line = '|'.join(ori_splits)
        CONTENT[idx] = new_line
        save_list()

    audio_path = ori_splits[0]
    sr, data = wavfile.read(audio_path)
    if data.shape[0] != audio[1].shape[0]:
        print(f'Saving file to {audio_path}')
        wavfile.write(audio_path, audio[0], audio[1])
    
    audio_path, text = get_line(idx + 1) 
    diffs = diff_text()
    return audio_path, text, idx + 1, diffs

def update_status():
    diffs = diff_text()
    diff_hltext = gr.HighlightedText(diffs, label='Diff', combine_adjacent=True, show_legend=True, color_map={'+':'green', '-':'red'})
    df_duration, total_len = get_durations()
    duration_plot = gr.BarPlot(df_duration, x='duration', y='samples', title=f'Total {int(total_len//60)}min{total_len%60:.1f}s', 
                               vertical=False, tooltip=['duration', 'samples'], label='Durations')
    return duration_plot, diff_hltext


js = '''
function disablePropagation(){
    var textarea = document.querySelector('textarea[data-testid="textbox"]');
    if (textarea) {
        textarea.addEventListener('keydown', function(event) {
            if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
                event.stopPropagation();
            }
        });
    }
}
'''
if __name__ == '__main__':
    with gr.Blocks(js=js) as app:
        with gr.Tab('Console'):
            au0, text0 = get_line(0)
            audio = gr.Audio(au0, interactive=True, autoplay=True, label='Speech')
            text = gr.Textbox(text0, label='Label')
            progress = gr.Slider(label='Progress', minimum=0, maximum=len(CONTENT) - 1, value=0, step=1)
        with gr.Tab('Status') as status_tab:
            duration_plot = gr.BarPlot()
            diff_hltext = gr.HighlightedText()

        progress.input(get_line, inputs=progress, outputs=[audio, text])
        text.submit(update_control, inputs=[audio, text, progress], outputs=[audio, text, progress])
        status_tab.select(update_status, outputs=[duration_plot, diff_hltext])


    app.launch(inbrowser=True)