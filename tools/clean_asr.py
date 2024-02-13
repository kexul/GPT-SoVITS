import sys
from scipy.io import wavfile

def main(asr_path):
    with open(asr_path, 'rt', encoding='utf-8') as f:
        content = f.read()
    new_content = []
    for item in content.split('\n'):
        parts = item.split('|')
        file_name = parts[0]
        sr, data = wavfile.read(file_name)
        length = data.shape[0] / sr
        if length <= 10:
            new_content.append(item)
    with open(asr_path, 'wt', encoding='utf-8') as f:
        f.write('\n'.join(new_content))

if __name__ == '__main__':
    main(input('path:'))
