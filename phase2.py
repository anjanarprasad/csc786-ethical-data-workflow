"""Leakage-aware experiments for CSC 786 cross-dataset NIDS study.

Input CSVs must be already canonicalized to a shared flow feature schema. This
module never fits transforms on target data and never silently uses attack labels
as predictors. Results are emitted only after a successful run.
"""
from __future__ import annotations
import argparse, json, os, platform, sys, time, warnings, pickle
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, wasserstein_distance, t as student_t
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, precision_recall_curve,
    roc_auc_score, precision_score, recall_score, f1_score, confusion_matrix)
from sklearn.model_selection import train_test_split, StratifiedKFold, StratifiedGroupKFold, cross_val_predict
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SEED_DEFAULT = [13, 29, 47, 71, 101]
BAN = {"label", "class", "target", "attack", "attack_type", "category", "label_name", "binary_label", "y", "dataset", "domain"}

def canonical_label(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        vals=set(pd.Series(s.dropna().unique()).astype(float))
        if vals <= {0.0,1.0}: return s.astype("int8")
    text=s.astype(str).str.strip().str.lower()
    if set(text.dropna().unique()) <= {"0", "1"}: return text.astype("int8")
    benign=text.str.contains(r"benign|normal|background",regex=True)
    attack=text.notna() & ~benign & ~text.isin(["nan","none",""])
    return pd.Series(np.where(attack,1,0),index=s.index,dtype="int8")

def load_data(path, label_col, category_col=None):
    header=pd.read_csv(path,nrows=0).columns.tolist()
    if label_col not in header: raise ValueError(f"{path}: label column {label_col!r} missing")
    usecols=[c for c in header if c not in {"IPV4_SRC_ADDR","IPV4_DST_ADDR"}]
    dtype={c:np.float32 for c in usecols if c not in {label_col,category_col}}
    df=pd.read_csv(path,low_memory=False,usecols=usecols,dtype=dtype)
    y=canonical_label(df[label_col])
    cat=df[category_col].astype(str) if category_col and category_col in df else None
    X=df.drop(columns=[c for c in [label_col,category_col] if c and c in df],errors="ignore")
    X=X.select_dtypes(include=[np.number]).replace([np.inf,-np.inf],np.nan)
    X=X.loc[:,~X.columns.str.lower().isin(BAN)]
    if X.empty: raise ValueError(f"{path}: no numeric predictor columns after exclusions")
    X=X.astype(np.float32,copy=False)
    return X,y,cat

def align_features(a,b,requested=None):
    cols=[c for c in a.columns if c in b.columns]
    if requested:
        missing=sorted(set(requested)-set(cols))
        if missing: raise ValueError(f"Requested features not shared: {missing}")
        cols=list(requested)
    if not cols: raise ValueError("No shared numeric features; inspect canonical preprocessing.")
    return a[cols].copy(),b[cols].copy(),cols

def feature_groups(X):
    return pd.util.hash_pandas_object(X,index=False,categorize=True).to_numpy(dtype=np.uint64)

def split_source(X,y,seed):
    # Keep identical feature rows in one partition to prevent duplicate leakage.
    groups=feature_groups(X)
    group_frame=pd.DataFrame({"group":groups,"y":y.to_numpy()}).groupby("group",sort=False).y.agg(["sum","size"])
    group_y=((2*group_frame["sum"])>=group_frame["size"]).astype("int8")
    unique_groups=group_frame.index.to_numpy(dtype=np.uint64)
    tr_g,rest_g=train_test_split(unique_groups,test_size=.30,random_state=seed,stratify=group_y.to_numpy())
    rest_mask=np.isin(unique_groups,rest_g)
    rest_y=group_y.to_numpy()[rest_mask]
    va_g,te_g=train_test_split(rest_g,test_size=.50,random_state=seed,stratify=rest_y)
    tr_mask=pd.Series(groups).isin(tr_g).to_numpy(); va_mask=pd.Series(groups).isin(va_g).to_numpy(); te_mask=pd.Series(groups).isin(te_g).to_numpy()
    return (X.loc[tr_mask].reset_index(drop=True),y.loc[tr_mask].reset_index(drop=True)),(X.loc[va_mask].reset_index(drop=True),y.loc[va_mask].reset_index(drop=True)),(X.loc[te_mask].reset_index(drop=True),y.loc[te_mask].reset_index(drop=True)),int(len(y)-len(unique_groups))

def rss_bytes():
    try:
        # In this container, os.getpid() is remapped and psutil may fail to
        # resolve self. Reading procfs directly returns the current process RSS.
        with open('/proc/self/status', encoding='utf-8') as f:
            for line in f:
                if line.startswith('VmRSS:'):
                    return int(line.split()[1]) * 1024
        return None
    except Exception:
        return None

def latency_summary(estimator,X,batch_size=256,repeats=20):
    n=min(len(X),batch_size)
    sample=X.iloc[:n]
    try: estimator.predict_proba(sample)
    except Exception: return {"latency_batch_ms_p50":np.nan,"latency_batch_ms_p95":np.nan,"latency_batch_size":n}
    times=[]
    for _ in range(repeats):
        t0=time.perf_counter(); estimator.predict_proba(sample); times.append((time.perf_counter()-t0)*1000)
    return {"latency_batch_ms_p50":float(np.percentile(times,50)),"latency_batch_ms_p95":float(np.percentile(times,95)),"latency_batch_size":n}

def metrics(y,p,threshold):
    pred=(p>=threshold).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {"pr_auc":float(average_precision_score(y,p)),"roc_auc":float(roc_auc_score(y,p)) if len(np.unique(y))==2 else np.nan,
      "precision":float(precision_score(y,pred,zero_division=0)),"recall":float(recall_score(y,pred,zero_division=0)),
      "f1":float(f1_score(y,pred,zero_division=0)),"fpr":float(fp/(fp+tn)) if fp+tn else np.nan,
      "threshold":float(threshold),"tp":int(tp),"fp":int(fp),"fn":int(fn),"tn":int(tn)}

def best_f1_threshold(y,p):
    precision,recall,thresholds=precision_recall_curve(y,p)
    if not len(thresholds): return .5
    f=2*precision[:-1]*recall[:-1]/np.maximum(precision[:-1]+recall[:-1],1e-12)
    return float(thresholds[int(np.nanargmax(f))])

def model_factory(name,seed,y=None):
    if name=="logistic": return LogisticRegression(max_iter=1000,class_weight="balanced",solver="lbfgs",random_state=seed)
    if name=="mlp": return MLPClassifier(hidden_layer_sizes=(32,16),activation="relu",alpha=1e-4,
        learning_rate_init=1e-3,batch_size=2048,early_stopping=True,n_iter_no_change=6,max_iter=60,random_state=seed)
    if name=="xgboost":
        try: from xgboost import XGBClassifier
        except Exception as e: raise ImportError("Install xgboost to run XGBoost") from e
        return XGBClassifier(n_estimators=100,max_depth=5,learning_rate=.08,subsample=.8,colsample_bytree=.8,
            scale_pos_weight=float((np.asarray(y)==0).sum()/max((np.asarray(y)==1).sum(),1)) if y is not None else 1.0,
            objective="binary:logistic",eval_metric="logloss",n_jobs=2,random_state=seed)
    if name=="lightgbm":
        try: from lightgbm import LGBMClassifier
        except Exception as e: raise ImportError("Install lightgbm to run LightGBM") from e
        return LGBMClassifier(n_estimators=100,max_depth=-1,num_leaves=31,learning_rate=.08,
            subsample=.8,colsample_bytree=.8,class_weight="balanced",verbosity=-1,n_jobs=2,random_state=seed)
    raise ValueError(name)

def pipe(model):
    return Pipeline([("impute",SimpleImputer(strategy="median",add_indicator=True)),
                     ("scale",StandardScaler()),("model",model)])

def bh_adjust(pvals):
    p=np.asarray(pvals,float); n=len(p); order=np.argsort(p); q=np.empty(n)
    ranked=p[order]*n/np.arange(1,n+1); ranked=np.minimum.accumulate(ranked[::-1])[::-1]
    q[order]=np.minimum(ranked,1); return q

def shift_analysis(Xs,Xt,source_name,target_name,out):
    rows=[]
    for c in Xs.columns:
        a=Xs[c].dropna().to_numpy(); b=Xt[c].dropna().to_numpy()
        if not len(a) or not len(b): continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            p=float(mannwhitneyu(a,b,alternative="two-sided").pvalue)
        pooled=np.sqrt((np.var(a)+np.var(b))/2)
        rows.append({"feature":c,"source_mean":float(np.mean(a)),"target_mean":float(np.mean(b)),
          "source_median":float(np.median(a)),"target_median":float(np.median(b)),
          "standardized_mean_difference":float((np.mean(b)-np.mean(a))/pooled) if pooled else 0.,
          "wasserstein":float(wasserstein_distance(a,b)),"mann_whitney_p":p})
    df=pd.DataFrame(rows); df["mann_whitney_q_bh"]=bh_adjust(df.mann_whitney_p) if len(df) else []
    df["source_dataset"]=source_name; df["target_dataset"]=target_name
    df.sort_values(["mann_whitney_q_bh","wasserstein"],ascending=[True,False]).to_csv(out,index=False)
    # Domain classifier learns dataset identity using a held-out split. No target labels used.
    domain=pd.concat([Xs.assign(_domain=0),Xt.assign(_domain=1)],ignore_index=True)
    y=domain.pop("_domain")
    # Duplicate feature vectors are removed before splitting the domain task so
    # exact copies cannot inflate held-out domain discrimination.
    dg=feature_groups(domain); unique=~pd.Series(dg).duplicated(keep=False).to_numpy()
    domain=domain.loc[unique].reset_index(drop=True); y=y.loc[unique].reset_index(drop=True)
    ix=np.arange(len(y)); tr,te=train_test_split(ix,test_size=.25,random_state=73,stratify=y)
    dm=Pipeline([("impute",SimpleImputer(strategy="median",add_indicator=True)),
      ("model",ExtraTreesClassifier(n_estimators=80,min_samples_leaf=2,class_weight="balanced",n_jobs=1,random_state=73))])
    dm.fit(domain.iloc[tr],y.iloc[tr]); pr=dm.predict_proba(domain.iloc[te])[:,1]
    auc=float(roc_auc_score(y.iloc[te],pr))
    imp=permutation_importance(dm,domain.iloc[te],y.iloc[te],scoring="roc_auc",n_repeats=2,random_state=73,n_jobs=1,max_samples=5000)
    fi=pd.DataFrame({"feature":domain.columns,"importance_mean":imp.importances_mean,"importance_std":imp.importances_std}).sort_values("importance_mean",ascending=False)
    fi.to_csv(Path(out).with_name(f"domain_feature_importance_{source_name}_to_{target_name}.csv"),index=False)
    return df,{"domain_auc":auc,"domain_n":int(len(domain)),"domain_train_n":len(tr),"domain_test_n":len(te)},fi

def benchmark_onnx_int8(estimator,X,y,threshold,artifact_dir):
    """Optional dynamic INT8 ONNX benchmark for the sklearn MLP pipeline."""
    out={"status":"unavailable","reason":None}
    try:
        from skl2onnx import to_onnx
        from skl2onnx.common.data_types import FloatTensorType
        from onnxruntime.quantization import quantize_dynamic, QuantType
        import onnxruntime as ort
        artifact_dir=Path(artifact_dir); artifact_dir.mkdir(parents=True,exist_ok=True)
        fp=artifact_dir/"mlp_fp32.onnx"; q8=artifact_dir/"mlp_int8_dynamic.onnx"
        converted=to_onnx(estimator,initial_types=[("input",FloatTensorType([None,X.shape[1]]))],
                          options={id(estimator.named_steps["model"]):{"zipmap":False}},target_opset=17)
        fp.write_bytes(converted.SerializeToString())
        quantize_dynamic(str(fp),str(q8),weight_type=QuantType.QInt8)
        sess=ort.InferenceSession(str(q8),providers=["CPUExecutionProvider"])
        name=sess.get_inputs()[0].name; arr=X.to_numpy(dtype=np.float32)
        warm=sess.run(None,{name:arr[:min(32,len(arr))]})
        t0=time.perf_counter(); outputs=sess.run(None,{name:arr}); elapsed=time.perf_counter()-t0
        prob=np.asarray(outputs[-1]); prob=prob[:,1] if prob.ndim==2 else prob.reshape(-1)
        out={"status":"completed","n_eval":len(y),"serialized_int8_bytes":q8.stat().st_size,
             "serialized_fp32_bytes":fp.stat().st_size,"int8_inference_seconds":elapsed,
             "int8_rows_per_second":len(y)/max(elapsed,1e-9),**metrics(np.asarray(y),prob,threshold)}
        (artifact_dir/"onnx_int8_metrics.json").write_text(json.dumps(out,indent=2))
    except Exception as e:
        out={"status":"unavailable","reason":f"{type(e).__name__}: {e}"}
    return out

def run_pair(src_path,tgt_path,source_name,target_name,cfg,outdir):
    outdir=Path(outdir); tables=outdir/"tables"; tables.mkdir(parents=True,exist_ok=True)
    sx,sy,sc=load_data(src_path,cfg["label_column"],cfg.get("category_column")); tx,ty,tc=load_data(tgt_path,cfg["label_column"],cfg.get("category_column"))
    sx,tx,features=align_features(sx,tx,cfg.get("features"))
    # Shift analysis is exploratory and uses only unlabeled target feature values.
    shift,domain,domain_fi=shift_analysis(sx,tx,source_name,target_name,tables/f"shift_{source_name}_to_{target_name}.csv")
    seeds=cfg.get("seeds",SEED_DEFAULT); models=cfg.get("models",["logistic","mlp","xgboost","lightgbm"])
    ratios=cfg.get("train_fractions",[.25,.5,1.]); results=[]; skipped=[]; pred_cache={}
    results_path=tables/f"model_results_{source_name}_to_{target_name}.csv"
    for seed in seeds:
        (xtr,ytr),(xv,yv),(xte,yte),ndup=split_source(sx,sy,seed)
        for ratio in ratios:
            if ratio<1:
                chosen, _=train_test_split(np.arange(len(ytr)),train_size=ratio,random_state=seed,stratify=ytr)
                xr,yr=xtr.iloc[chosen],ytr.iloc[chosen]
            else: xr,yr=xtr,ytr
            for name in models:
                try: estimator=pipe(model_factory(name,seed,yr))
                except ImportError as e:
                    skipped.append({"model":name,"reason":str(e)}); continue
                rss_before=rss_bytes(); t0=time.perf_counter(); estimator.fit(xr,yr); fit_seconds=time.perf_counter()-t0
                rss_after=rss_bytes(); pv=estimator.predict_proba(xv)[:,1]; threshold=best_f1_threshold(yv,pv)
                for split_name,X,y in [("source_test",xte,yte),("cross_dataset",tx,ty)]:
                    t1=time.perf_counter(); p=estimator.predict_proba(X)[:,1]; elapsed=time.perf_counter()-t1
                    row={"direction":f"{source_name}_to_{target_name}","model":name,"seed":seed,"train_fraction":ratio,"training_scope":"source_train_fraction",
                      "n_train":len(yr),"source_n":len(sy),"target_n":len(ty),"n_features":len(features),"duplicate_rows_grouped":ndup,
                      "fit_seconds":fit_seconds,"inference_seconds":elapsed,"inference_rows_per_second":len(y)/max(elapsed,1e-9),
                      "serialized_model_bytes":len(pickle.dumps(estimator,protocol=pickle.HIGHEST_PROTOCOL)),
                      "rss_before_fit_bytes":rss_before,"rss_after_fit_bytes":rss_after,
                      "rss_fit_delta_bytes":(rss_after-rss_before) if rss_before is not None and rss_after is not None else np.nan,
                      **latency_summary(estimator,X),
                      "split":split_name,"dataset":source_name if split_name=="source_test" else target_name,
                      "n_eval":len(y),"prevalence":float(np.mean(y)),**metrics(y.to_numpy(),p,threshold)}
                    results.append(row)
                    pd.DataFrame(results).to_csv(results_path,index=False)
                    if seed==seeds[0] and ratio==1 and split_name=="cross_dataset":
                        pred_cache[name]=(estimator,p,threshold)
                print(f"FIT {source_name}->{target_name} seed={seed} fraction={ratio:g} model={name} seconds={fit_seconds:.1f}",flush=True)
    # Full-source development fit: reserve the source test partition; pool only
    # source train+validation for the final fit. Calibrate the threshold from
    # 5-fold out-of-fold source-development predictions, then refit on all 85%.
    full_models=cfg.get("full_source_models",models)
    for seed in cfg.get("full_source_seeds",seeds[:1]):
        (xtr,ytr),(xv,yv),(xte,yte),ndup=split_source(sx,sy,seed)
        xdev=pd.concat([xtr,xv],ignore_index=True); ydev=pd.concat([ytr,yv],ignore_index=True)
        folds=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=seed)
        dev_groups=feature_groups(xdev)
        for name in full_models:
            try: proto=pipe(model_factory(name,seed,ydev))
            except ImportError: continue
            t0=time.perf_counter()
            oof=cross_val_predict(proto,xdev,ydev,groups=dev_groups,cv=folds,method="predict_proba",n_jobs=1)[:,1]
            threshold=best_f1_threshold(ydev.to_numpy(),oof)
            estimator=pipe(model_factory(name,seed,ydev)); rss_before=rss_bytes(); estimator.fit(xdev,ydev); rss_after=rss_bytes()
            fit_seconds=time.perf_counter()-t0
            if seed==seeds[0] and name=="mlp": pred_cache[name]=(estimator,estimator.predict_proba(tx)[:,1],threshold)
            for split_name,X,y in [("source_test",xte,yte),("cross_dataset",tx,ty)]:
                t1=time.perf_counter(); p=estimator.predict_proba(X)[:,1]; elapsed=time.perf_counter()-t1
                full_row={"direction":f"{source_name}_to_{target_name}","model":name,"seed":seed,
                  "train_fraction":1.0,"training_scope":"full_source_development_85pct","n_train":len(ydev),
                  "source_n":len(sy),"target_n":len(ty),"n_features":len(features),"duplicate_rows_grouped":ndup,
                  "fit_seconds":fit_seconds,"inference_seconds":elapsed,"inference_rows_per_second":len(y)/max(elapsed,1e-9),
                  "serialized_model_bytes":len(pickle.dumps(estimator,protocol=pickle.HIGHEST_PROTOCOL)),
                  "rss_before_fit_bytes":rss_before,"rss_after_fit_bytes":rss_after,
                  "rss_fit_delta_bytes":(rss_after-rss_before) if rss_before is not None and rss_after is not None else np.nan,
                  **latency_summary(estimator,X),"split":split_name,"dataset":source_name if split_name=="source_test" else target_name,
                  "n_eval":len(y),"prevalence":float(np.mean(y)),**metrics(y.to_numpy(),p,threshold)}
                results.append(full_row); pd.DataFrame(results).to_csv(results_path,index=False)
            print(f"FULL-SOURCE {source_name}->{target_name} seed={seed} model={name} seconds={fit_seconds:.1f}",flush=True)
    pd.DataFrame(results).to_csv(results_path,index=False)
    # Exploratory ablation: remove five features most useful for dataset identity,
    # retrain/evaluate the MLP. Selection uses unlabeled target X, never target y.
    drop_features=domain_fi.feature.head(min(5,len(domain_fi))).tolist()
    ablation=[]
    for seed in seeds:
        (xtr,ytr),(xv,yv),(xte,yte),_ = split_source(sx,sy,seed)
        for ab_name,cols in [("all_features",features),("drop_top5_domain_features",[c for c in features if c not in drop_features])]:
            if not cols: continue
            est=pipe(model_factory("mlp",seed,ytr)); est.fit(xtr[cols],ytr)
            th=best_f1_threshold(yv,est.predict_proba(xv[cols])[:,1])
            for split_name,xx,yy in [("source_test",xte,yte),("cross_dataset",tx,ty)]:
                pp=est.predict_proba(xx[cols])[:,1]
                ablation.append({"direction":f"{source_name}_to_{target_name}","seed":seed,"ablation":ab_name,
                    "n_features":len(cols),"removed_features":";".join(drop_features) if ab_name!="all_features" else "",
                    "split":split_name,**metrics(yy.to_numpy(),pp,th)})
    pd.DataFrame(ablation).to_csv(tables/f"feature_ablation_{source_name}_to_{target_name}.csv",index=False)
    if tc is not None and pred_cache:
        category_rows=[]
        # Best default: per-model held-out target predictions from first seed only,
        # with source-validation threshold, to avoid using category labels in fitting.
        for name,(est,p,thr) in pred_cache.items():
            frame=pd.DataFrame({"category":tc.astype(str).to_numpy(),"y":ty.to_numpy(),"p":p})
            frame["predicted_attack"]=(frame.p>=thr)
            for cat,g in frame.groupby("category"):
                if str(cat).strip().lower() in {"benign","normal"} or not len(g): continue
                category_rows.append({"model":name,"attack_category":cat,"n":len(g),
                    "detected_n":int(g.predicted_attack.sum()),"missed_n":int((~g.predicted_attack).sum()),
                    "recall_at_source_threshold":float(g.predicted_attack.mean()),
                    "mean_attack_score":float(g.p.mean()),"median_attack_score":float(g.p.median()),
                    "source_validation_threshold":float(thr)})
        pd.DataFrame(category_rows).to_csv(tables/f"attack_category_{source_name}_to_{target_name}.csv",index=False)
    if "mlp" in pred_cache:
        est,p,thr=pred_cache["mlp"]
        comp=benchmark_onnx_int8(est,tx,ty.to_numpy(),thr,outdir/"artifacts"/f"{source_name}_to_{target_name}")
        pd.DataFrame([comp]).to_csv(tables/f"onnx_int8_{source_name}_to_{target_name}.csv",index=False)
    else: comp={"status":"skipped","reason":"MLP missing or required optional dependencies unavailable"}
    meta={"source":source_name,"target":target_name,"features":features,"source_rows":len(sy),"target_rows":len(ty),
      "source_prevalence":float(sy.mean()),"target_prevalence":float(ty.mean()),"domain_analysis":domain,
      "skipped_models":skipped,"onnx_int8":comp,"status":"completed" if results else "no_models_ran"}
    (outdir/f"run_metadata_{source_name}_to_{target_name}.json").write_text(json.dumps(meta,indent=2))
    return pd.DataFrame(results),shift,domain,domain_fi,meta

def aggregate(results_path,out):
    d=pd.read_csv(results_path)
    keys=[c for c in ["direction","model","train_fraction","training_scope","split","dataset"] if c in d]
    metrics_=[c for c in ["pr_auc","roc_auc","precision","recall","f1","fpr","inference_rows_per_second"] if c in d]
    rows=[]
    for group_key,g in d.groupby(keys):
        if not isinstance(group_key,tuple): group_key=(group_key,)
        row=dict(zip(keys,group_key))
        for m in metrics_:
            x=g[m].dropna().to_numpy(); n=len(x); mean=float(np.mean(x)) if n else np.nan
            sd=float(np.std(x,ddof=1)) if n>1 else np.nan
            half=float(student_t.ppf(.975,n-1)*sd/np.sqrt(n)) if n>1 else np.nan
            row.update({f"{m}_mean":mean,f"{m}_std":sd,f"{m}_n_seeds":n,
                        f"{m}_ci95_low":mean-half if n>1 else np.nan,
                        f"{m}_ci95_high":mean+half if n>1 else np.nan})
        rows.append(row)
    pd.DataFrame(rows).to_csv(out,index=False)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--config",default="configs/phase2.json"); a=ap.parse_args()
    cfg=json.loads(Path(a.config).read_text()); base=Path(cfg.get("output_dir","results")); allr=[]
    pairs=cfg["pairs"]
    for pair in pairs:
        r,*_=run_pair(pair["source_csv"],pair["target_csv"],pair["source_name"],pair["target_name"],cfg,base)
        if len(r): allr.append(r)
    if allr:
        joined=pd.concat(allr,ignore_index=True); p=base/"tables"/"phase2_results_all.csv"; joined.to_csv(p,index=False); aggregate(p,base/"tables"/"phase2_summary_mean_std.csv")
    print(f"Finished. Outputs: {base.resolve()}")
if __name__=="__main__": main()
