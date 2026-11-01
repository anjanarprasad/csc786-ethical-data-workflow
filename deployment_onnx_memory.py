"""Isolated process RSS and batched inference measurements for ONNX MLP artifacts."""
import json, os, resource, subprocess, sys, time
from pathlib import Path
import numpy as np, pandas as pd, onnxruntime as ort
from sklearn.metrics import average_precision_score, roc_auc_score
from phase2 import load_data
ROOT=Path(__file__).resolve().parents[1]
PAIRS=[('NF_CSE_CIC_IDS2018_v2_to_NF_UNSW_NB15_v2','NF-UNSW-NB15-v2.csv'),
       ('NF_UNSW_NB15_v2_to_NF_CSE_CIC_IDS2018_v2','NF-CSE-CIC-IDS2018-v2.csv')]
def rss():
    for line in open('/proc/self/status',encoding='utf-8'):
        if line.startswith('VmRSS:'): return int(line.split()[1])*1024
    return None
def worker(direction,targetfile,precision):
    before_data=rss(); x,y,_=load_data(ROOT/'data/samples'/targetfile,'Label','Attack')
    data_rss=rss(); x=x.to_numpy(dtype=np.float32,copy=False); y=y.to_numpy()
    filename='mlp_fp32.onnx' if precision=='fp32' else 'mlp_int8_dynamic.onnx'
    model_path=ROOT/'results/artifacts'/direction/filename
    threshold=float(pd.read_csv(ROOT/'results/tables'/f'onnx_int8_{direction}.csv').iloc[0].threshold)
    before_session=rss(); sess=ort.InferenceSession(str(model_path),providers=['CPUExecutionProvider']); after_session=rss()
    key=sess.get_inputs()[0].name; batch=8192; scores=[]; t0=time.perf_counter()
    for i in range(0,len(x),batch): scores.append(sess.run(None,{key:x[i:i+batch]})[1][:,1])
    elapsed=time.perf_counter()-t0; p=np.concatenate(scores)
    return {'direction':direction,'precision':precision,'batch_size':batch,'n_eval':len(y),
      'model_bytes':model_path.stat().st_size,'pr_auc':float(average_precision_score(y,p)),
      'roc_auc':float(roc_auc_score(y,p)),'score_std':float(np.std(p)),
      'threshold_from_source_validation':threshold,'inference_seconds':elapsed,
      'rows_per_second':len(y)/elapsed,'rss_before_data_bytes':before_data,
      'rss_after_data_bytes':data_rss,'rss_before_session_bytes':before_session,
      'rss_after_session_bytes':after_session,
      'process_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
def main():
    if len(sys.argv)>1 and sys.argv[1]=='--worker':
        print(json.dumps(worker(sys.argv[2],sys.argv[3],sys.argv[4])))
        return
    rows=[]
    for direction,targetfile in PAIRS:
        for precision in ('fp32','int8_dynamic'):
            proc=subprocess.run([sys.executable,__file__,'--worker',direction,targetfile,precision],
               cwd=ROOT,text=True,capture_output=True,check=True)
            rows.append(json.loads(proc.stdout.strip().splitlines()[-1]))
    out=pd.DataFrame(rows);out.to_csv(ROOT/'results/tables/onnx_deployment_memory.csv',index=False)
    print(out.to_string(index=False))
if __name__=='__main__': main()
