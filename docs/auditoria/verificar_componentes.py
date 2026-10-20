from pathlib import Path
import base64,contextlib,io,json,runpy
from datetime import date
import nbformat
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[2]
report={'notebook_figures':[], 'dashboard_states':[], 'errors':[]}
with contextlib.redirect_stdout(io.StringIO()):
 g=runpy.run_path(str(ROOT/'docs/auditoria/recalculo_independente.py'), run_name='auditoria_importada')

def vector(a):
 if isinstance(a,dict) and 'bdata' in a:
  x=np.frombuffer(base64.b64decode(a['bdata']),dtype=a['dtype'])
  if 'shape' in a:x=x.reshape(tuple(int(d.strip()) for d in a['shape'].split(',')))
  return x
 return np.asarray(a)

def equal(a,b):np.testing.assert_allclose(vector(a),np.asarray(b),atol=1e-7,rtol=1e-10,equal_nan=True)

raw=g['r'];train=g['train'];test=g['test'];pred=g['pe']
notebook=nbformat.read(ROOT/'notebooks/analise_bicicletas.ipynb',as_version=4)
figures=[o.data['application/vnd.plotly.v1+json'] for c in notebook.cells for o in c.get('outputs',[]) if 'application/vnd.plotly.v1+json' in o.get('data',{})]
assert len(figures)==7
f=figures[0];equal(f['data'][0]['y'],raw.cnt)
np.testing.assert_array_equal(pd.to_datetime(f['data'][0]['x']),pd.to_datetime(raw.dteday))
f=figures[1];equal(f['data'][0]['x'],raw.temp);equal(f['data'][0]['y'],raw.cnt)
f=figures[2];equal(f['data'][0]['x'],raw.loc[train,'temp']);equal(f['data'][0]['y'],raw.loc[train,'cnt'])
order=np.argsort(raw.loc[train,'temp'].to_numpy(),kind='stable')
equal(f['data'][1]['x'],raw.loc[train,'temp'].to_numpy()[order]);equal(f['data'][1]['y'],(g['Xs'][train]@g['bs'])[order])
f=figures[3];equal(f['data'][0]['y'],raw.loc[train,'cnt']);equal(f['data'][1]['y'],g['A']@g['b'])
f=figures[4];equal(f['data'][0]['x'],g['A']@g['b']);equal(f['data'][0]['y'],g['res'])
f=figures[5];res=g['res']-g['res'].mean();equal(f['data'][0]['x'],np.arange(1,29));equal(f['data'][0]['y'],[np.dot(res[k:],res[:-k])/np.dot(res,res) for k in range(1,29)])
f=figures[6]
for trace,col in zip(f['data'],['cnt','previsto_simples','previsto_multiplo','previsto_referencia']):equal(trace['y'],pred[col])
for f in figures:report['notebook_figures'].append({'title':f['layout']['title']['text'],'status':'passed; all plotted values match independent raw-data recomputation'})

app=AppTest.from_file(str(ROOT/'dashboard/app.py'),default_timeout=20).run()
original_metrics=app.dataframe[1].value.copy();original_tests=app.dataframe[2].value.copy()
for label,period,types in [
 ('serie_completa',(date(2011,1,1),date(2012,12,31)),['Dia útil','Fim de semana ou feriado']),
 ('janeiro_dias_uteis',(date(2011,1,1),date(2011,1,31)),['Dia útil']),
 ('um_dia_nao_util',(date(2011,1,1),date(2011,1,1)),['Fim de semana ou feriado']),
 ('sem_resultados',(date(2011,1,1),date(2011,1,1)),['Dia útil']),
 ('sem_tipo_dia',(date(2011,1,1),date(2012,12,31)),[]),
 ('data_incompleta',(date(2011,1,1),),['Dia útil'])
]:
 app.date_input[0].set_value(period)
 app.multiselect[0].set_value(types).run()
 assert not app.exception
 charts=[json.loads(c.proto.spec) for c in app.get('plotly_chart')]
 pd.testing.assert_frame_equal(app.dataframe[-2].value,original_metrics)
 pd.testing.assert_frame_equal(app.dataframe[-1].value,original_tests)
 if len(period)==2:
  dates=pd.to_datetime(raw.dteday)
  mask=dates.between(pd.Timestamp(period[0]),pd.Timestamp(period[1])) & pd.Series(g['types']).isin(types)
  selected=raw.loc[mask]
  if len(selected):
   assert len(charts)==3
   expected=selected.assign(dteday=pd.to_datetime(selected.dteday)).set_index('dteday').reindex(pd.date_range(*period))
   equal(charts[0]['data'][0]['y'],expected.cnt)
   for trace in charts[1]['data']:
    daykind=1 if trace['name']=='Dia útil' else 0
    rows=selected.loc[selected.workingday==daykind]
    equal(trace['x'],rows.temp);equal(trace['y'],rows.cnt)
   expected_table=selected.assign(tipo_dia=np.where(selected.workingday==1,'Dia útil','Fim de semana ou feriado')).groupby('tipo_dia',as_index=False).agg(dias_observados=('cnt','size'),media_diaria=('cnt','mean'),mediana_diaria=('cnt','median'),desvio_padrao=('cnt','std'))
   pd.testing.assert_frame_equal(app.dataframe[0].value,expected_table)
  else:assert len(charts)==1 and app.info
 else:assert len(charts)==1 and app.info
 for trace,col in zip(charts[-1]['data'],['cnt','previsto_simples','previsto_multiplo','previsto_referencia']):equal(trace['y'],pred[col])
 report['dashboard_states'].append({'state':label,'status':'passed; values and chart data checked, not just element presence'})
report['visual_limit']='Native Chrome screenshot inspected at 512px and after closing emulation; full desktop and lower-section visual inspection interrupted by noWindowsAvailable. Runtime control and chart data checks completed via AppTest.'
Path(__file__).with_name('2026-10-19-componentes.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps(report,indent=2,ensure_ascii=False))
