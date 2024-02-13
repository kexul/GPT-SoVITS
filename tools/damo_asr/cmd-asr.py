# -*- coding:utf-8 -*-

import sys,os,traceback
dir=sys.argv[1]
opt_name=os.path.basename(dir)

from funasr import AutoModel

model = AutoModel(model="paraformer-zh", model_revision="v2.0.4",
                  vad_model="fsmn-vad", vad_model_revision="v2.0.4",
                  punc_model="ct-punc-c", punc_model_revision="v2.0.4",
                  )


opt=[]
for name in os.listdir(dir):
    try:
        text = model.generate(input="%s/%s"%(dir,name))[0]["text"]
        opt.append("%s/%s|%s|ZH|%s"%(dir,name,opt_name,text))
    except:
        print(traceback.format_exc())

opt_dir="output/asr_opt"
os.makedirs(opt_dir,exist_ok=True)
with open("%s/%s.list"%(opt_dir,opt_name),"w",encoding="utf-8")as f:
    f.write("\n".join(opt))

