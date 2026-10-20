"""Independent read-only numerical audit. Run using project's .venv/bin/python."""
from pathlib import Path
import json, hashlib
import numpy as np
import pandas as pd
from scipy.special import betainc
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[2]
report={'method':'numpy.linalg.lstsq; manually assembled design; manual HAC Bartlett(7), correction n/(n-k); t p-values from incomplete beta; t critical from root finding','checks':{},'differences':{},'errors':[]}
def check(name,condition,detail=None):
 report['checks'][name]={'pass':bool(condition),'detail':detail}
 if not condition: report['errors'].append(name)
def compare(name,a,b,tol=1e-7):
 a=np.asarray(a);b=np.asarray(b)
 if a.shape!=b.shape: check(name,False,{'shapes':[list(a.shape),list(b.shape)]});return
 if a.dtype.kind in 'biufc' and b.dtype.kind in 'biufc':
  delta=float(np.max(np.abs(a.astype(float)-b.astype(float)))) if a.size else 0
  report['differences'][name]=delta
  check(name,np.allclose(a,b,rtol=1e-10,atol=tol),{'max_abs_difference':delta})
 else: check(name,np.array_equal(a,b))
r=pd.read_csv(ROOT/'dados/brutos/day.csv').sort_values('dteday').reset_index(drop=True)
dates=pd.to_datetime(r.dteday)
check('raw_shape',r.shape==(731,16),list(r.shape))
compare('raw_dates_complete',r.dteday,pd.date_range('2011-01-01','2012-12-31').strftime('%Y-%m-%d'))
check('raw_no_missing',not r.isna().any().any())
check('raw_no_duplicates',not r.duplicated().any() and not r.dteday.duplicated().any())
compare('raw_instant',r.instant,np.arange(1,732))
compare('raw_month_dates',r.mnth,dates.dt.month)
compare('raw_year_dates',r.yr,dates.dt.year-2011)
compare('raw_weekday_dates',r.weekday,(dates.dt.dayofweek+1)%7)
compare('raw_workingday_logic',r.workingday,((dates.dt.dayofweek<5)&(r.holiday==0)).astype(int))
compare('raw_total_counts',r.cnt,r.casual+r.registered)
check('raw_nonnegative_counts',bool((r[['cnt','casual','registered']]>=0).all().all()))
for col in ['temp','atemp','hum','windspeed']: check('raw_normalized_'+col,r[col].between(0,1).all())
for col,vals in [('season',[1,2,3,4]),('yr',[0,1]),('mnth',range(1,13)),('holiday',[0,1]),('weekday',range(7)),('workingday',[0,1]),('weathersit',[1,2,3,4])]: check('raw_domain_'+col,r[col].isin(vals).all())
t_anos=(dates-pd.Timestamp('2011-01-01')).dt.days.to_numpy()/365.25
types=np.where(r.workingday==1,'Dia útil','Fim de semana ou feriado')
tr=pd.read_csv(ROOT/'dados/tratados/day_tratado.csv',sep=';')
check('treated_shape',tr.shape==(731,18),list(tr.shape))
for col in r.columns: compare('treated_'+col,tr[col],r[col])
compare('treated_tipo_dia',tr.tipo_dia,types)
compare('treated_t_anos',tr.t_anos,t_anos)
train=(dates<=pd.Timestamp('2012-06-30')).to_numpy();test=~train
check('split_sizes',int(train.sum())==547 and int(test.sum())==184)
y=r.cnt.to_numpy(dtype=float)
X=np.column_stack([np.ones(len(r)),r.temp,r.workingday,*[(r.mnth==m).astype(float) for m in range(2,13)],t_anos])
Xs=np.column_stack([np.ones(len(r)),r.temp])
A=X[train];yt=y[train];n,k=A.shape
b,_,rank,_=np.linalg.lstsq(A,yt,rcond=None)
bs=np.linalg.lstsq(Xs[train],yt,rcond=None)[0]
check('design_full_rank',rank==k,{'n':n,'k':k,'rank':int(rank)})
res=yt-A@b;Z=A*res[:,None]
S=Z.T@Z
for lag in range(1,8):
 G=Z[lag:].T@Z[:-lag];S+=(1-lag/8)*(G+G.T)
bread=np.linalg.inv(A.T@A)
V=(n/(n-k))*bread@S@bread
se=np.sqrt(np.diag(V));df=n-k
def pvalue(t):return float(betainc(df/2,0.5,df/(df+t*t)))
crit=brentq(lambda t:pvalue(t)-0.05,1,4,xtol=1e-14)
h=pd.read_csv(ROOT/'resultados/testes_hipoteses.csv')
check('hypothesis_rows',h.variavel.tolist()==['workingday','temp'])
expected_h=[]
for variable,index in [('workingday',2),('temp',1)]:
 stat=b[index]/se[index]
 expected_h.append({'variavel':variable,'estimativa':b[index],'erro_padrao':se[index],'estatistica_t':stat,'p_valor':pvalue(stat),'ic_inferior':b[index]-crit*se[index],'ic_superior':b[index]+crit*se[index],'graus_liberdade':df,'metodo':'HAC Bartlett; 7 defasagens; correção amostral; t aproximada','nivel_confianca':0.95,'significancia':0.05,'inicio':'2011-01-01','fim':'2012-06-30','dias':n})
he=pd.DataFrame(expected_h)
for c in he.columns:compare('hypotheses_'+c,h[c],he[c])
p=pd.read_csv(ROOT/'resultados/previsoes.csv')
pe=r.loc[test,['dteday','cnt','workingday','temp']].reset_index(drop=True)
pe['tipo_dia']=types[test]
pe['previsto_simples']=Xs[test]@bs
pe['previsto_multiplo']=X[test]@b
pe['previsto_referencia']=np.full(int(test.sum()),np.sum(yt)/len(yt))
check('prediction_shape',p.shape==(184,8),list(p.shape))
for c in pe.columns:compare('predictions_'+c,p[c],pe[c])
m=pd.read_csv(ROOT/'resultados/metricas_modelos.csv')
expected_m=[]
for label,c in [('Simples','previsto_simples'),('Múltiplo','previsto_multiplo'),('Média do treino','previsto_referencia')]:
 pred=pe[c].to_numpy(); e=y[test]-pred
 expected_m.append({'modelo':label,'mae':np.sum(np.abs(e))/len(e),'rmse':np.linalg.norm(e)/np.sqrt(len(e)),'r2':1-np.dot(e,e)/np.dot(y[test]-np.mean(y[test]),y[test]-np.mean(y[test])),'inicio':'2012-07-01','fim':'2012-12-31','dias':len(e),'previsoes_negativas':int(np.count_nonzero(pred<0))})
me=pd.DataFrame(expected_m)
check('metric_shape',m.shape==(3,8),list(m.shape))
for c in me.columns:compare('metrics_'+c,m[c],me[c])
report['coefficients']={'simple':dict(zip(['intercept','temp'],bs.tolist())),'multiple':dict(zip(['intercept','temp','workingday',*[f'month_{m}' for m in range(2,13)],'t_anos'],b.tolist()))}
report['hypotheses_recomputed']=he.to_dict('records');report['metrics_recomputed']=me.to_dict('records')
report['residual_diagnostics']={'durbin_watson':float(np.dot(np.diff(res),np.diff(res))/np.dot(res,res)),'acf_1':float(np.dot((res-res.mean())[1:],(res-res.mean())[:-1])/np.dot(res-res.mean(),res-res.mean()))}
report['input_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'dados/brutos/day.csv',ROOT/'dados/tratados/day_tratado.csv',*sorted((ROOT/'resultados').glob('*.csv')),ROOT/'notebooks/analise_bicicletas.ipynb']}
report['scope']='Checks internal numerical consistency against supplied raw CSV; does not authenticate raw CSV against original publisher.'
Path(__file__).with_name('2026-10-19-numeros.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({'checks':len(report['checks']),'errors':report['errors'],'max_differences':report['differences'],'hypotheses':expected_h,'metrics':expected_m,'diagnostics':report['residual_diagnostics']},indent=2,ensure_ascii=False))

if __name__ == "__main__":
 raise SystemExit(bool(report["errors"]))
