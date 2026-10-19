"""Exact float32 export of schema-3 Chromatique; no Stockfish NNUE weights."""
import argparse,hashlib,json,struct,gzip
from pathlib import Path
import numpy as np

def export(model,out):
    raw=Path(model).read_bytes();raw=gzip.decompress(raw) if str(model).endswith(".gz") else raw;p=json.loads(raw)
    assert p['schema']==3 and p['evaluation_kind']=='fully_neural' and not p['classical_evaluation'] and not p['fixed_material']
    assert p['input_dim']==820 and p['architecture'][1]==512 and p['policy_input']=='first_hidden_layer'
    assert 'classical_blend' not in p and p['architecture']==[820,512,32]
    assert p['feature_version']=='chromatique-pure-v1' and p['value_target']=='sf19_direct_cp'
    assert p['score_perspective']=='side_to_move' and p['output_scale_cp']==600 and p['output_limit_cp']==10000
    assert len(p['policy_moves'])==1968 and len(set(p['policy_moves']))==1968
    for layer,ni,no in [(p['layers'][0],820,512),(p['layers'][1],512,32),(p['value_head'],32,1),(p['linear_head'],820,1),(p['policy_head'],512,1968)]:
        assert layer['input']==ni and layer['output']==no
        assert len(layer['weight'])==ni*no and len(layer['bias'])==no
        assert np.isfinite(layer['weight']).all() and np.isfinite(layer['bias']).all()
    assert np.isfinite(p['policy_temperature']) and p['policy_temperature']>0
    arrays=[np.asarray(p['layers'][0]['weight'],np.float32).reshape(512,820).T.copy(),p['layers'][0]['bias'],p['layers'][1]['weight'],p['layers'][1]['bias'],p['value_head']['weight'],p['value_head']['bias'],p['linear_head']['weight'],p['linear_head']['bias'],p['policy_head']['weight'],p['policy_head']['bias'],[p['policy_temperature']]]
    payload=b''.join(np.asarray(a,dtype='<f4').tobytes() for a in arrays)
    for name in p['policy_moves']:payload+=name.encode().ljust(6,b'\0')
    checksum=14695981039346656037
    for b in payload:checksum=((checksum^b)*1099511628211)&((1<<64)-1)
    header=struct.pack('<8sIIII64sQ',b'CHROMA3\0',820,512,32,1968,hashlib.sha256(raw).hexdigest().encode(),checksum)
    dest=Path(out);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(header+payload)
    record={'format':'CHROMA3 float32 little-endian','source_model':str(model),'source_model_sha256':hashlib.sha256(raw).hexdigest(),'native_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'classical_evaluation':False,'fixed_material':False,'policy_vocabulary':1968,'bytes':dest.stat().st_size}
    dest.with_suffix(dest.suffix+'.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('model');p.add_argument('out');a=p.parse_args();export(a.model,a.out)
