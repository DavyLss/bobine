"""Offline checks for publication-gated Cloudinary cleanup."""
import sys,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))
import publishing as p
with tempfile.TemporaryDirectory() as folder:
    out=Path(folder)
    config={'cloudinary_cloud_name':'test','cloudinary_api_key':'key','cloudinary_api_secret':'secret'}
    record={'targets':{'instagram':{'status':'published'},'tiktok':{'status':'scheduled'}},'assets':{'Video.mp4':{'cloud':'test','public_id':'local-video-studio/'+out.name+'/digest'}}}
    with patch.object(p.api,'request_json',return_value=({'result':'ok'},None)) as request:
        p.cleanup_hosted(out,record,config,lambda r:None);assert not request.called
        record['targets']['tiktok']['status']='error'
        p.cleanup_hosted(out,record,config,lambda r:None);assert not request.called
        record['targets']['tiktok']['status']='published'
        p.cleanup_hosted(out,record,config,lambda r:None)
        assert request.call_count==1 and record['cleanup_status']=='done'
        assert record['assets']['Video.mp4']['deleted_at']
        p.cleanup_hosted(out,record,config,lambda r:None);assert request.call_count==1
        record['assets']['Video.mp4'].pop('deleted_at');record['assets']['Video.mp4']['public_id']='unrelated/asset'
        p.cleanup_hosted(out,record,config,lambda r:None);assert request.call_count==1 and record['cleanup_status']=='error'
print('OK: pending/error block cleanup, confirmed deletion, idempotence, asset ownership.')
