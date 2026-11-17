"""Publication contracts and crash safety; all external services are mocked."""
import base64,hashlib,json,os,sys,tempfile,subprocess,time
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse,parse_qs
from unittest.mock import patch
import requests
from fastapi.testclient import TestClient
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'studio'))

def response(data=None,status=200,headers=None):return SimpleNamespace(status_code=status,headers=headers or {},json=lambda:data or {})

with tempfile.TemporaryDirectory() as directory:
    root=Path(directory);os.environ.update(STUDIO_DATA_DIR=str(root/'state'),STUDIO_JOBS_DIR=str(root/'jobs'),STUDIO_PORT='8514')
    import integrations as api,publishing as pub,social_assets as assets,server
    from batches import BatchRequest,validate_batch
    headers={'X-Studio-Request':'1','Origin':'http://127.0.0.1:8514'}
    settings={'enabled':True,'youtube_client_id':'test-client','youtube_client_secret':'fake-google-secret','instagram_token':'fake-instagram-token','instagram_app_secret':'fake-instagram-secret','instagram_user_id':'123456','buffer_token':'fake-buffer-token','buffer_tiktok_channel':'a'*24,'cloudinary_cloud_name':'test-cloud','cloudinary_api_key':'fake-cloud-key','cloudinary_api_secret':'fake-cloud-secret','tiktok_cover':False}
    # No test is permitted to accidentally call a real external service.
    with patch('requests.sessions.Session.request',side_effect=AssertionError('Réseau externe interdit dans ces tests')):
        with TestClient(server.app) as client:
            assert client.put('/api/social/settings',json=settings).status_code==403
            result=client.put('/api/social/settings',json=settings,headers=headers);assert result.status_code==200,result.text
            assert 'fake-' not in result.text and 'fake-' not in client.get('/api/social/settings').text
            assert api.load()['buffer_token']=='fake-buffer-token'
            assert 'fake-' not in api.FILE.read_text(encoding='utf-8')
            api.save_settings(api.SettingsInput(**{**settings,'buffer_token':''}));assert api.load()['buffer_token']=='fake-buffer-token'
            assert client.get('/api/social/youtube/callback?state=invalid&code=fake').status_code==400
            assert client.get('/api/social/guide').status_code==200
            bad={'title':'Test','description':'Description suffisamment longue.','auto_publish':True,'publish_platforms':['youtube'],'format':'reel'}
            with patch.object(server.PENDING,'put'):
                for overrides in [{},{'publish_platforms':[]},{'format':'standard'}]:
                    result=client.post('/api/jobs',json={**bad,**overrides},headers=headers)
                    assert result.status_code==201,result.text
                    job=result.json()
                    assert job['status']=='queued' and not job['auto_publish']
                    assert job['publication']['status']=='blocked' and not job.get('publish_accounts')
                assert server.SOCIAL_PENDING.empty()
        # PKCE + state + code exchange, without any user account.
        authorization=api.youtube_authorize();query=parse_qs(urlparse(authorization['url']).query)
        assert query['code_challenge_method']==['S256'] and query['access_type']==['offline']
        state=query['state'][0]
        with patch.object(api,'request_json',side_effect=[({'access_token':'fake-access','refresh_token':'fake-refresh','expires_in':3600},None),({'items':[{'id':'test-channel','snippet':{'title':'Chaîne de test'}}]},None)]) as remote:
            api.youtube_callback('fake-code',state)
            assert remote.call_args_list[0].kwargs['data']['code_verifier']
        try:api.youtube_callback('fake-code',state);raise AssertionError('Réutilisation OAuth acceptée')
        except ValueError:pass
        config=api.load();assert api.public_settings()['youtube_connected']
        assert not api.missing(config,['youtube','instagram','tiktok'])
        # CSV publication values inherit or override the common settings.
        items,_=validate_batch(BatchRequest(csv='titre;description;publication_auto;reseaux;mode_publication\nTitre;Une description assez longue;oui;youtube|instagram;now',defaults={'format':'reel'}))
        assert items[0]['auto_publish'] and items[0]['publish_platforms']==['youtube','instagram'] and items[0]['publish_mode']=='now'
        items,_=validate_batch(BatchRequest(items=[{'title':'Test','description':'Une description assez longue','auto_publish':True}]))
        assert items[0]['auto_publish'] and not items[0]['publish_platforms']
        # Generate real local JPGs and validate that the only text call targets Ollama.
        out=root/'asset-test';out.mkdir();Image.new('RGB',(1080,1920),'#29221e').save(out/'Poster.jpg')
        model_text={'title':'Le DevOps expliqué simplement','description':'Une équipe partage la responsabilité du service et apprend de chaque changement. Voici un exemple concret pour comprendre.','hashtags':['DevOps','Collaboration','Apprentissage'],'thumbnail_text':'Pourquoi travailler ensemble ?'}
        with patch.object(assets.requests,'post',return_value=SimpleNamespace(raise_for_status=lambda:None,json=lambda:{'message':{'content':json.dumps(model_text)}})) as local:
            text=assets.create(out,{'title':'Le DevOps','format':'reel','theme':'dark'},{'scenes':[{'text':'Une équipe collabore et apprend.'}]})
            assert local.call_args.args[0].startswith('http://127.0.0.1:11434/')
        assert Image.open(out/'Miniature-Reel.jpg').size==(1080,1920)
        assert Image.open(out/'Miniature-YouTube.jpg').size==(1280,720)
        assert text['hashtags']==['#DevOps','#Collaboration','#Apprentissage']
        (out/'Video.mp4').write_bytes(b'fake-media')
        # Native YouTube upload; Buffer and a public host are never involved.
        with patch.object(api,'youtube_token',return_value='fake-access'),patch.object(pub.requests,'post',side_effect=[response(headers={'Location':'https://www.googleapis.com/upload/session?upload_id=test'}),response()]) as post,patch.object(pub.requests,'put',return_value=response({'id':'video-id'})),patch.object(api,'buffer_query',side_effect=AssertionError('YouTube ne doit pas passer par Buffer')):
            result=pub.run(out,['youtube'],'queue');assert result['targets']['youtube']['post_id']=='video-id'
            assert post.call_args_list[0].kwargs['json']['snippet']['title']==text['title']
            assert post.call_args_list[0].kwargs['json']['status']['privacyStatus']=='public'
            assert 'youtube_session' not in json.dumps(result)
            pub.run(out,['youtube'],'queue');assert post.call_count==2
        with patch.object(api,'youtube_token',return_value='fake-access'),patch.object(api,'request_json',return_value=({'items':[{'status':{'uploadStatus':'processed','privacyStatus':'public'}}]},None)):
            assert pub.refresh(out)['status']=='published'
        # A timeout on the final YouTube chunk resumes the existing session.
        resume=root/'resume';resume.mkdir();(resume/'Video.mp4').write_bytes(b'fake-media');(resume/'Publication.json').write_text(json.dumps(text),encoding='utf-8');(resume/'Miniature-YouTube.jpg').write_bytes((out/'Miniature-YouTube.jpg').read_bytes())
        with patch.object(api,'youtube_token',return_value='fake-access'),patch.object(pub.requests,'post',return_value=response(headers={'Location':'https://www.googleapis.com/upload/session?upload_id=resume'})),patch.object(pub.requests,'put',side_effect=requests.Timeout('test')):
            assert pub.run(resume,['youtube'],'now')['targets']['youtube']['status']=='uncertain'
        with patch.object(api,'youtube_token',return_value='fake-access'),patch.object(pub.requests,'post',return_value=response()) as post,patch.object(pub.requests,'put',return_value=response({'id':'resumed-id'})):
            assert pub.run(resume,['youtube'],'now')['targets']['youtube']['post_id']=='resumed-id'
            assert post.call_count==1 and 'thumbnails/set' in post.call_args.args[0]
        # Instagram receives a native REELS container and the generated cover URL.
        with patch.object(pub,'hosted',side_effect=lambda out,name,*args:'https://res.cloudinary.com/test/'+name),patch.object(api,'request_json',side_effect=[({'id':'container-1'},None),({'status_code':'FINISHED'},None),({'id':'ig-media'},None),({'permalink':'https://www.instagram.com/reel/test/'},None)]) as remote:
            result=pub.run(out,['instagram'],'now');assert result['targets']['instagram']['status']=='published'
            payload=remote.call_args_list[0].kwargs['json'];assert payload['media_type']=='REELS' and payload['cover_url'].endswith('Miniature-Reel.jpg')
            count=remote.call_count;pub.run(out,['instagram'],'now');assert remote.call_count==count
        # A persisted pre-send intent is never resent after an interrupted response.
        uncertain=root/'uncertain';uncertain.mkdir();(uncertain/'Publication.json').write_text(json.dumps(text),encoding='utf-8')
        assets.write_json(uncertain/'Publishing.json',{'status':'sending','assets':{},'targets':{'tiktok':{'account_id':'a'*24,'publish_attempted':True,'status':'sending'}}})
        with patch.object(api,'buffer_query',side_effect=AssertionError('Ne pas dupliquer une publication incertaine')):
            assert pub.run(uncertain,['tiktok'],'queue')['targets']['tiktok']['status']=='uncertain'
        # Buffer is TikTok-only and requires confirmation before displaying published.
        with patch.object(pub,'hosted',return_value='https://res.cloudinary.com/test/video.mp4'),patch.object(api,'buffer_query',return_value={'createPost':{'post':{'id':'buffer-id','status':'scheduled','externalLink':None}}}) as remote:
            result=pub.run(out,['tiktok'],'queue');assert result['targets']['tiktok']['status']=='scheduled'
            payload=remote.call_args.args[1]['input'];assert payload['channelId']=='a'*24 and payload['mode']=='addToQueue' and payload['needsApproval'] is False
            assert payload['metadata']=={'tiktok':{'isAiGenerated':True}}
        with patch.object(api,'buffer_query',return_value={'post':{'id':'buffer-id','status':'sent','externalLink':'https://www.tiktok.com/@test/video/1'}}):
            result=pub.refresh(out);assert result['targets']['tiktok']['status']=='published'
        # A changed account blocks automatic sends before uploading anything.
        try:pub.run(out,['youtube'],'now',expected_accounts={'youtube':'another-channel'});raise AssertionError('Compte changé accepté')
        except ValueError:pass
        # Signed, bounded-memory Cloudinary chunks: two requests for an 11 MiB file.
        big=root/'chunk.mp4';big.write_bytes(b'0'*(11*1024*1024))
        with patch.object(api,'request_json',side_effect=[({'done':False},None),({'done':True,'secure_url':'https://res.cloudinary.com/test/video.mp4','public_id':'test'},None)]) as remote:
            pub.cloud_upload(big,config)
            assert remote.call_count==2
            first=remote.call_args_list[0];assert first.kwargs['headers']['Content-Range']==f'bytes 0-10485759/{11*1024*1024}'
            values=first.kwargs['data'];signed='&'.join(f'{key}={values[key]}' for key in sorted(['public_id','timestamp','overwrite']))+config['cloudinary_api_secret']
            assert values['signature']==hashlib.sha1(signed.encode()).hexdigest()
        assert 'fake-' not in json.dumps(api.public_settings())
        # Automatic publication is triggered after generation, with the captured account.
        fake=root/'pipeline_stub.py';fake.write_text("from pathlib import Path\nimport sys\nout=Path(sys.argv[1]);(out/'Video.mp4').write_bytes(b'test');(out/'Publication.json').write_text('{}')\n",encoding='utf-8')
        real_popen=subprocess.Popen;automatic=[]
        def pipeline(command,**kwargs):return real_popen([sys.executable,'-u',str(fake),command[3]],**kwargs)
        def send(folder,platforms,mode,changed,accounts):
            automatic.append((platforms,mode,accounts))
            report={'status':'published','targets':{'youtube':{'post_id':'auto-id','status':'published','account_id':accounts['youtube']}}}
            assets.write_json(folder/'Publishing.json',report);changed(report);return report
        with patch.object(server.subprocess,'Popen',side_effect=pipeline),patch.object(pub,'run',side_effect=send):
            job=server.create(server.VideoRequest(title='Automatisation',description='Une explication complète à publier.',auto_publish=True,publish_platforms=['youtube'],format='reel'))
            limit=time.monotonic()+10
            while time.monotonic()<limit and server.find(job['id']).get('publication',{}).get('status')!='published':time.sleep(.02)
            assert server.find(job['id'])['status']=='done' and server.find(job['id'])['publication']['status']=='published'
            assert automatic==[(['youtube'],'queue',pub.account_ids(api.load()))]
        # A real local TikTok copy keeps the original and adds silence + cover.
        import numpy as np
        from moviepy import ColorClip,AudioClip,VideoFileClip
        import encoding
        media=root/'media';media.mkdir();(media/'Miniature-Reel.jpg').write_bytes((out/'Miniature-Reel.jpg').read_bytes())
        os.environ['STUDIO_VIDEO_CODEC']='libx264';encoding.encoder.cache_clear()
        audio=AudioClip(lambda t:.1*np.sin(2*np.pi*220*t),duration=.4,fps=24000)
        clip=ColorClip(size=(1080,1920),color=(40,50,60),duration=.4).with_audio(audio)
        clip.write_videofile(str(media/'Video.mp4'),fps=30,codec='libx264',audio_codec='aac',logger=None);clip.close();audio.close()
        before=hashlib.sha256((media/'Video.mp4').read_bytes()).hexdigest();target=assets.tiktok_video(media)
        assert hashlib.sha256((media/'Video.mp4').read_bytes()).hexdigest()==before
        with VideoFileClip(str(target)) as check:
            assert check.size==[1080,1920] and abs(check.duration-1)<.1 and check.audio is not None
            assert np.max(np.abs(check.audio.subclipped(0,.4).to_soundarray(fps=24000)))<.01
            assert np.max(np.abs(check.audio.subclipped(.7,.9).to_soundarray(fps=24000)))>.02
print('OK : secrets, OAuth, métadonnées locales, YouTube natif reprenable, Instagram natif, Buffer TikTok, reçus et anti-doublon.')
