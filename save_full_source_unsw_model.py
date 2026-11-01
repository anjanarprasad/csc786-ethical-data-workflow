"""Rebuild and persist the deterministic full-source UNSW Logistic Regression artifact."""
import json, pickle, time
from pathlib import Path
import pandas as pd
from phase2 import load_data, split_source, align_features, model_factory, pipe
ROOT=Path(__file__).resolve().parents[1]
def main():
 cfg=json.loads((ROOT/'configs/phase2.json').read_text())
 x,y,_=load_data(ROOT/'data/processed/NF-UNSW-NB15-v2.csv',cfg['label_column'],cfg['category_column'])
 tx,_,_=load_data(ROOT/'data/samples/NF-CSE-CIC-IDS2018-v2.csv',cfg['label_column'],cfg['category_column'])
 x,tx,features=align_features(x,tx,cfg.get('features'))
 (xtr,ytr),(xv,yv),(_, _),_=split_source(x,y,786)
 xdev=pd.concat([xtr,xv],ignore_index=True); ydev=pd.concat([ytr,yv],ignore_index=True)
 model=pipe(model_factory('logistic',786,ydev)); t=time.perf_counter(); model.fit(xdev,ydev)
 out=ROOT/'results/artifacts/full_source_unsw';out.mkdir(parents=True,exist_ok=True)
 dest=out/'logistic_full_source_development.pkl'
 with dest.open('wb') as f: pickle.dump(model,f,protocol=pickle.HIGHEST_PROTOCOL)
 rows=pd.read_csv(ROOT/'results/tables/full_source_NF_UNSW_NB15_v2.csv')
 meta={'seed':786,'source_dataset':'NF-UNSW-NB15-v2','source_total_rows':int(len(y)),
  'source_development_rows':int(len(ydev)),'source_test_rows':int(len(y)-len(ydev)),
  'target':'NF-CSE-CIC-IDS2018-v2 uniform sample','features':features,
  'threshold':float(rows.threshold.iloc[0]),'threshold_selection':'5-fold grouped out-of-fold source-development predictions',
  'fit_seconds_rebuild':time.perf_counter()-t,'serialized_bytes':dest.stat().st_size}
 (out/'metadata.json').write_text(json.dumps(meta,indent=2))
 print(json.dumps(meta,indent=2))
if __name__=='__main__': main()
