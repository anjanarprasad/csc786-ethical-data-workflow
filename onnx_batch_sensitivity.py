"""Check whether ONNX dynamic quantization changes predictions with batch size."""
import time
from pathlib import Path
import numpy as np, pandas as pd, onnxruntime as ort
from sklearn.metrics import average_precision_score, roc_auc_score, confusion_matrix
from phase2 import load_data
ROOT=Path(__file__).resolve().parents[1]
def main():
 cfg={'label':'Label','category':'Attack'}; rows=[]
 dirs=[('NF_CSE_CIC_IDS2018_v2_to_NF_UNSW_NB15_v2','NF-UNSW-NB15-v2.csv'),('NF_UNSW_NB15_v2_to_NF_CSE_CIC_IDS2018_v2','NF-CSE-CIC-IDS2018-v2.csv')]
 for direction,targetfile in dirs:
  x,y,_=load_data(ROOT/'data/samples'/targetfile,cfg['label'],cfg['category']); x=x.to_numpy(np.float32,copy=False); y=y.to_numpy()
  root=ROOT/'results/artifacts'/direction
  threshold=float(pd.read_csv(ROOT/'results/tables'/f'onnx_int8_{direction}.csv').iloc[0].threshold)
  for precision,filename in [('fp32','mlp_fp32.onnx'),('int8_dynamic','mlp_int8_dynamic.onnx')]:
   sess=ort.InferenceSession(str(root/filename),providers=['CPUExecutionProvider']); key=sess.get_inputs()[0].name
   reference=None
   for batch_size in (256,1024,8192):
    pieces=[];start=time.perf_counter()
    for i in range(0,len(x),batch_size):
     pieces.append(sess.run(None,{key:x[i:i+batch_size]})[1][:,1])
    elapsed=time.perf_counter()-start;p=np.concatenate(pieces)
    if reference is None: reference=p.copy()
    delta=float(np.max(np.abs(p-reference)))
    tn,fp,fn,tp=confusion_matrix(y,p>=threshold,labels=[0,1]).ravel()
    rows.append({'direction':direction,'precision':precision,'batch_size':batch_size,'n_eval':len(y),
     'pr_auc':float(average_precision_score(y,p)),'roc_auc':float(roc_auc_score(y,p)),
     'score_std':float(np.std(p)),'max_abs_score_diff_vs_256_batch':delta,
     'precision_at_mlp_source_threshold':tp/max(tp+fp,1),'recall_at_mlp_source_threshold':tp/max(tp+fn,1),
     'fpr_at_mlp_source_threshold':fp/max(fp+tn,1),'inference_seconds':elapsed,'rows_per_second':len(y)/elapsed})
   del sess
 out=pd.DataFrame(rows); dest=ROOT/'results/tables/onnx_batch_sensitivity.csv';out.to_csv(dest,index=False);print(out.to_string(index=False))
if __name__=='__main__':main()
