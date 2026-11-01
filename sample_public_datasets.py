"""Create deterministic uniform row samples from the UQ NetFlow-v2 CSVs.
Reads in chunks and stores only a bounded sample in memory.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

SEED=786
SAMPLE_N=250_000
CHUNK=250_000
DATASETS={
 "NF-UNSW-NB15-v2":"data/processed/NF-UNSW-NB15-v2.csv",
 "NF-CSE-CIC-IDS2018-v2":"data/processed/NF-CSE-CIC-IDS2018-v2.csv",
}

def sample_csv(name,src,out):
 rng=np.random.default_rng(SEED); best=pd.DataFrame(); keys=np.empty(0,dtype=np.float64)
 total=0; label_counts={}; attack_counts={}; cols=None
 for chunk in pd.read_csv(src,chunksize=CHUNK,low_memory=False,dtype={"Label":"uint8","Attack":"category"}):
  if cols is None:
   cols=[c for c in chunk.columns if c not in {"IPV4_SRC_ADDR","IPV4_DST_ADDR"}]
  chunk=chunk[cols]
  for c in chunk.columns:
   if c not in {"Label","Attack"}: chunk[c]=pd.to_numeric(chunk[c],errors="coerce").astype("float32")
  label_counts.update({k:int(v)+label_counts.get(k,0) for k,v in chunk.Label.value_counts().items()})
  counts=chunk.Attack.value_counts().to_dict()
  for k,v in counts.items(): attack_counts[str(k)]=attack_counts.get(str(k),0)+int(v)
  total+=len(chunk)
  k=min(SAMPLE_N,len(best)+len(chunk))
  candidates=pd.concat([best,chunk],ignore_index=True,copy=False)
  cand_keys=np.concatenate([keys,rng.random(len(chunk))])
  if len(candidates)>SAMPLE_N:
   ix=np.argpartition(cand_keys,SAMPLE_N-1)[:SAMPLE_N]
   best=candidates.iloc[ix].reset_index(drop=True); keys=cand_keys[ix]
  else: best=candidates; keys=cand_keys
  if total%1_000_000==0: print(name,"rows scanned",total,flush=True)
 Path(out).parent.mkdir(parents=True,exist_ok=True)
 best.to_csv(out,index=False)
 meta={"dataset":name,"source_csv":str(src),"sample_csv":str(out),"source_rows_scanned":total,
       "sample_rows":len(best),"seed":SEED,"sampling":"uniform reservoir via random priority keys",
       "source_label_counts":label_counts,"source_attack_counts":attack_counts,
       "sample_label_counts":{str(k):int(v) for k,v in best.Label.value_counts().items()},
       "sample_attack_counts":{str(k):int(v) for k,v in best.Attack.value_counts().items()},
       "feature_columns":[c for c in best.columns if c not in {"Label","Attack"}]}
 Path(out).with_suffix('.metadata.json').write_text(json.dumps(meta,indent=2))
 print("SAMPLED",name,"n",len(best),"prevalence",float(best.Label.mean()),"attack_categories",best.Attack.nunique(),flush=True)
 return meta

if __name__=='__main__':
 root=Path(__file__).resolve().parents[1]
 for n,rel in DATASETS.items(): sample_csv(n,root/rel,root/f'data/samples/{n}.csv')
