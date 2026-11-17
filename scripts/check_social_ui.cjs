/* Publication UI tests without network accounts or a running service. */
const {JSDOM}=require('jsdom'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),dom=new JSDOM(fs.readFileSync(path.join(root,'studio/static/index.html'),'utf8'),{url:'http://127.0.0.1:8511/',runScripts:'outside-only'}),w=dom.window,$=id=>w.document.getElementById(id),calls=[];
w.TextDecoder=TextDecoder;w.setInterval=()=>0;w.scrollTo=()=>{};w.HTMLElement.prototype.scrollIntoView=function(){};w.HTMLMediaElement.prototype.pause=function(){};
const popup={location:{href:''},close(){}};w.open=()=>popup;
const video={id:'a'.repeat(32),title:'Une vidéo de test',description:'Une explication suffisamment claire.',status:'done',stage:'done',progress:100,theme:'dark',duration:60,format:'reel',created:Date.now()/1000};
const state={jobs:[video],batches:[],settings:{theme:'dark',duration:60,format:'reel',voice:'Narrateur-Homme-01'}};
let config={enabled:false,youtube_client_id:'client-id',youtube_privacy:'public',youtube_made_for_kids:false,instagram_user_id:'1234',instagram_version:'v27.0',buffer_tiktok_channel:'b'.repeat(24),buffer_channels:[{id:'b'.repeat(24),name:'Mon TikTok',service:'tiktok'}],cloudinary_cloud_name:'test-cloud',ai_disclosure:true,tiktok_cover:true,youtube_connected:true,youtube_channel_name:'Ma chaîne',instagram_username:'moncompte',credentials:{youtube_client_secret:true,instagram_token:true,buffer_token:true,cloudinary_api_key:true,cloudinary_api_secret:true},ready:{youtube:true,instagram:true,tiktok:true},protection:'Windows DPAPI',youtube_redirect_uri:'http://127.0.0.1:8511/api/social/youtube/callback'};
let metadata={title:'Le DevOps en équipe',description:'Une équipe partage la responsabilité du service et apprend de chaque changement.',hashtags:['#DevOps','#Collaboration','#Apprentissage'],thumbnail_text:'Pourquoi travailler ensemble ?'};
let publication={status:'not_sent',targets:{}};
const answer=data=>({ok:true,json:async()=>structuredClone(data)});
w.fetch=async(url,options={})=>{const body=options.body?JSON.parse(options.body):null;calls.push({url,body,method:options.method||'GET'});
 if(url==='/api/state')return answer(state);if(url==='/api/health')return answer({ready:true,llm:true,voice:true,whisper:true});
 if(url==='/api/social/settings'){if(options.method==='PUT'){for(const [key,value] of Object.entries(body))if(!['youtube_client_secret','instagram_token','buffer_token','instagram_app_secret','cloudinary_api_key','cloudinary_api_secret'].includes(key))config[key]=value;}return answer(config);}
 if(url==='/api/social/youtube/connect')return answer({url:'https://accounts.google.com/o/oauth2/v2/auth?state=test'});
 if(url.startsWith('/api/social/test/'))return answer({message:'Connexion validée.'});
 if(url.endsWith('/social/metadata')){metadata=body;return answer(metadata);}
 if(url.endsWith('/social/publish')){publication={status:'submitted',targets:{youtube:{status:'processing',post_id:'youtube-id',url:'https://www.youtube.com/watch?v=id'},instagram:{status:'published',post_id:'instagram-id',url:'https://www.instagram.com/reel/test/'}}};return answer(publication);}
 if(url.endsWith('/social/refresh')){publication.targets.youtube.status='published';publication.status='published';return answer(publication);}
 if(url.endsWith('/social'))return answer({metadata,publication,busy:false});
 throw new Error('URL inattendue : '+url);
};
const settle=async()=>{for(let i=0;i<12;i++)await new Promise(resolve=>setImmediate(resolve));};
const event=(node,type)=>node.dispatchEvent(new w.Event(type,{bubbles:true,cancelable:true}));
(async()=>{
 vm.runInContext(fs.readFileSync(path.join(root,'studio/static/app.js'),'utf8'),dom.getInternalVMContext());vm.runInContext(fs.readFileSync(path.join(root,'studio/static/social.js'),'utf8'),dom.getInternalVMContext());vm.runInContext(fs.readFileSync(path.join(root,'studio/static/design.js'),'utf8'),dom.getInternalVMContext());await settle();
 assert.match($('youtube-connection').textContent,/Ma chaîne/);assert.equal($('buffer-token').value,'');assert.match($('buffer-token').placeholder,/enregistré/);assert.equal($('steps').children.length,6);
 assert.equal(w.document.querySelectorAll('.api-notice').length,4);assert.equal($('youtube-redirect').textContent,config.youtube_redirect_uri);
 $('integration-enabled').checked=true;$('buffer-token').value='secret-de-test';event($('integration-form'),'submit');await settle();assert.equal(calls.filter(c=>c.url==='/api/social/settings'&&c.method==='PUT').at(-1).body.buffer_token,'secret-de-test');assert.equal($('buffer-token').value,'');
 $('connect-youtube').click();await settle();assert.match(popup.location.href,/^https:\/\/accounts.google.com/);
 $('auto-publish').checked=true;$('auto-youtube').checked=true;w.document.querySelector('[name=format][value=standard]').checked=true;event($('auto-publish'),'change');assert.equal(w.settings().format,'standard');assert.equal(w.settings().auto_publish,true);assert.deepEqual([...w.settings().publish_platforms],['youtube']);
 w.selectJob(video);await settle();assert.equal($('social-card').classList.contains('hidden'),false);assert.equal($('social-title').value,metadata.title);assert.match($('social-thumb-reel').src,/Miniature-Reel.jpg/);
 $('social-title').value='<img src=x onerror=alert(1)> DevOps';event($('social-title'),'input');$('send-youtube').checked=true;$('send-social').click();await settle();assert.match($('social-error').textContent,/Enregistrer/);assert.equal(calls.filter(c=>c.url.endsWith('/social/publish')).length,0);
 event($('metadata-form'),'submit');await settle();assert.equal(w.document.querySelector('[onerror]'),null);assert.equal(metadata.title,'<img src=x onerror=alert(1)> DevOps');
 $('send-instagram').checked=true;$('send-social').click();await settle();assert.deepEqual(calls.find(c=>c.url.endsWith('/social/publish')).body.platforms,['youtube','instagram']);assert.equal($('publication-receipts').children.length,2);assert.equal($('publication-receipts').querySelectorAll('a').length,2);assert.match($('publication-receipts').textContent,/Traitement par le réseau/);
 $('refresh-social').click();await settle();assert.equal($('publication-receipts').querySelectorAll('.published').length,2);
 console.log('OK : notices, secrets masqués, OAuth, options automatiques, édition locale, miniatures, envois et reçus.');dom.window.close();
})().catch(error=>{console.error(error);dom.window.close();process.exitCode=1;});
