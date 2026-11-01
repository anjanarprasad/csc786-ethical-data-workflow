"""True full-dataset development fit on NF-UNSW-NB15-v2.
The original source test partition remains untouched. Threshold is selected from
out-of-fold source-development predictions grouped by exact feature duplicates.
"""
import json, time, pickle
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from phase2 import load_data, align_features, split_source, feature_groups, model_factory, pipe, best_f1_threshold, metrics, rss_bytes

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/processed/NF-UNSW-NB15-v2.csv'
TARGET=ROOT/'data/samples/NF-CSE-CIC-IDS2018-v2.csv'
OUT=ROOT/'results/tables/full_source_NF_UNSW_NB15_v2.csv'

def main():
 cfg=json.loads((ROOT/'configs/phase2.json').read_text())
 sx,sy,_=load_data(SOURCE,cfg['label_column'],cfg.get('category_column'))
 tx,ty,_=load_data(TARGET,cfg['label_column'],cfg.get('category_column'))
 sx,tx,features=align_features(sx,tx,cfg.get('features'))
 seed=786
 (xtr,ytr),(xv,yv),(xte,yte),ngroup=split_source(sx,sy,seed)
 xdev=pd.concat([xtr,xv],ignore_index=True); ydev=pd.concat([ytr,yv],ignore_index=True)
 groups=feature_groups(xdev); cv=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=seed)
 model=pipe(model_factory('logistic',seed,ydev))
 t0=time.perf_counter(); oof=cross_val_predict(model,xdev,ydev,groups=groups,cv=cv,method='predict_proba',n_jobs=1)[:,1]
 threshold=best_f1_threshold(ydev.to_numpy(),oof)
 rss0=rss_bytes(); final=pipe(model_factory('logistic',seed,ydev)); final.fit(xdev,ydev); rss1=rss_bytes(); fit_s=time.perf_counter()-t0
 rows=[]
 for split,X,y in [('source_test',xte,yte),('cross_dataset_sample',tx,ty)]:
  t1=time.perf_counter(); p=final.predict_proba(X)[:,1]; infer=time.perf_counter()-t1
  rows.append({'direction':'NF_UNSW_NB15_v2_to_NF_CSE_CIC_IDS2018_v2','model':'logistic','seed':seed,
    'training_scope':'full_source_development_85pct','source_total_rows':len(sy),'source_train_rows':len(ydev),
    'source_test_rows':len(yte),'target_sample_rows':len(ty),'target_sample_prevalence':float(ty.mean()),
    'n_features':len(features),'duplicate_rows_grouped':ngroup,'threshold_selection':'5-fold grouped out-of-fold source-development predictions',
    'threshold':threshold,'fit_and_threshold_calibration_seconds':fit_s,'inference_seconds':infer,
    'inference_rows_per_second':len(y)/max(infer,1e-9),'serialized_model_bytes':len(pickle.dumps(final,protocol=pickle.HIGHEST_PROTOCOL)),
    'rss_before_final_fit_bytes':rss0,'rss_after_final_fit_bytes':rss1,
    'rss_final_fit_delta_bytes':rss1-rss0 if rss0 is not None and rss1 is not None else np.nan,
    'split':split,'dataset':'NF-UNSW-NB15-v2' if split=='source_test' else 'NF-CSE-CIC-IDS2018-v2_uniform_sample',
    'n_eval':len(y),'prevalence':float(np.mean(y)),**metrics(y.to_numpy(),p,threshold)})
 OUT.parent.mkdir(parents=True,exist_ok=True); pd.DataFrame(rows).to_csv(OUT,index=False)
 (ROOT/'artifacts/full_source_unsw_run.json').write_text(json.dumps({'status':'completed','dataset_rows':len(sy),
   'train_development_rows':len(ydev),'source_test_rows':len(yte),'target_sample_rows':len(ty),
   'feature_columns':features,'seed':seed,'threshold':threshold,'fit_and_threshold_calibration_seconds':fit_s},indent=2))
 print(pd.DataFrame(rows).to_string(index=False))
if __name__=='__main__':main()
