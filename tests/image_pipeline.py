"""HTTP/DB regression tests with a controllable provider; no paid calls or credentials."""
import base64
import io
import json
import os
import sys
import tempfile
import threading
import time
import types
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
TMP = tempfile.TemporaryDirectory()
os.environ['DATABASE_PATH'] = str(Path(TMP.name)/'images.db')
os.environ.pop('DATABASE_URL', None)
if os.getenv('PLOT_IMAGE_TEST_DATABASE_URL'):os.environ['DATABASE_URL']=os.environ['PLOT_IMAGE_TEST_DATABASE_URL']
os.environ.pop('OPENAI_API_KEY', None)
import kyc_server as k
import kyc_image_jobs as jobs
import kyc_visuals as visuals


def image(fmt='JPEG', color='blue'):
    b = io.BytesIO()
    Image.new('RGB', (128, 128), color).save(b, format=fmt)
    return 'data:image/'+{'JPEG':'jpeg','PNG':'png','WEBP':'webp'}[fmt]+';base64,'+base64.b64encode(b.getvalue()).decode()

PHOTO = image()
ART = image(color='green')
k.init()
k.generate_pack = lambda *a, **kw: []
SERVER = k.ThreadingHTTPServer(('127.0.0.1', 0), k.H)
threading.Thread(target=SERVER.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{SERVER.server_port}'


def request(path, data=None, expect=200, raw=False):
    req = Request(BASE+path, data=None if data is None else json.dumps(data).encode(),
                  headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=3) as r:
            code, headers, body = r.status, r.headers, r.read()
    except HTTPError as e:
        code, headers, body = e.code, e.headers, e.read()
    assert code == expect, (path, code, body[:300])
    return (body, headers) if raw else json.loads(body)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.calls=[]; self.entered=threading.Event(); self.release=threading.Event(); self.provider_fail=False
        def generate(**kw):
            self.calls.append(kw); self.entered.set()
            if not self.release.wait(3): raise TimeoutError('test provider blocked')
            if self.provider_fail: raise RuntimeError('provider failed')
            return ART
        k.generate_many=generate
        os.environ['OPENAI_API_KEY']='test-only'

    def tearDown(self):
        self.release.set()

    def room(self, count=2, photos=1):
        c=request('/api/create',{'name':'Alice','rounds':6,'language':'en'})
        self.code,self.host=c['code'],c['host'];self.tokens={'Alice':c['token']}
        for name in ['Bob','Cara','Dan'][:count-1]:
            self.tokens[name]=request('/api/join',{'code':self.code,'name':name})['token']
        for name in list(self.tokens)[:photos]:
            self.post('photo',{'token':self.tokens[name],'data_url':PHOTO,'consent':True})
        self.g=k.game(self.code)
        self.post('start',{'host':self.host})
        self.g=k.game(self.code)
        return self.state()

    def post(self,action,data,expect=200):return request(f'/api/{self.code}/{action}',data,expect)
    def state(self):return request(f'/api/state/{self.code}?token={self.tokens["Alice"]}&host={self.host}')

    def reveal(self, st=None):
        st=st or self.state(); answer=st['options'][0]
        self.post('answer',{'token':self.tokens[st['subject']['name']],'answer':answer})
        self.assertFalse(self.entered.is_set(), 'must not generate before Reveal')
        for name,token in self.tokens.items():
            if name!=st['subject']['name']:self.post('guess',{'token':token,'guess':answer})
        return self.state()

    def wait_status(self,status,final=False):
        until=time.monotonic()+3
        while time.monotonic()<until:
            st=self.state()
            if st['final_hero_status' if final else 'hero_status']==status:return st
            time.sleep(.01)
        self.fail_test(status)

    def fail_test(self,status):raise AssertionError('did not reach '+status)

    def test_single_photo_nonblocking_refresh_reconnect_duplicate(self):
        self.room(); start=time.monotonic();st=self.reveal()
        self.assertLess(time.monotonic()-start,1)
        self.assertTrue(st['reveal']);self.assertTrue(self.entered.wait(1))
        self.assertIn(st['hero_status'],['queued','running']);self.assertIsNone(st['hero'])
        body={'host':self.host,'round':0,'image_run':st['image_run']}
        with ThreadPoolExecutor(max_workers=10) as pool:
            responses=list(pool.map(lambda _: self.post('hero',body,202),range(10)))
        for _ in range(8):self.state()
        reconnect=request(f'/api/state/WRONG?token={self.tokens["Alice"]}')
        self.assertEqual(reconnect['code'],self.code)
        self.assertEqual(len(self.calls),1)
        self.assertEqual([x[0] for x in self.calls[0]['items']],['Alice'])
        self.release.set();st=self.wait_status('ready')
        self.assertNotIn('base64',json.dumps(st));self.assertLess(len(json.dumps(st)),20000)
        data,headers=request(st['hero'],raw=True)
        self.assertEqual(data,base64.b64decode(ART.split(',')[1]))
        self.assertEqual(headers['Content-Type'],'image/jpeg')
        self.assertEqual(self.post('hero',body)['image'],st['hero']);self.assertEqual(len(self.calls),1)
        request(st['subject']['photo_url'],raw=True)
        # Reload job recovery never re-runs completed jobs.
        jobs.recover(k.cn,k.generate_many);self.assertEqual(len(self.calls),1)

    def test_group_two_relevant_references(self):
        self.room(4,4)
        with k.cn() as c:
            c.execute('UPDATE games SET custom_questions=? WHERE id=?',(json.dumps([['room','Who would {s} choose for a trip?',['x']]]),self.g['id']))
        with patch.object(k,'general_pack',return_value=[]):
            self.reveal();self.assertTrue(self.entered.wait(1))
        self.assertEqual([x[0] for x in self.calls[0]['items']],['Alice','Bob'])
        self.assertEqual(self.calls[0]['selected'],'Bob')
        self.assertIn('Bob',self.calls[0]['answer'])
        self.release.set();self.wait_status('ready')

    def test_no_photo_and_no_consent(self):
        self.room(2,0);st=self.reveal()
        self.assertEqual(self.calls,[]);self.assertTrue(st['reveal'])
        self.assertEqual(self.post('hero',{'host':self.host})['status'],'no_photo')
        self.post('photo',{'token':self.tokens['Alice'],'data_url':PHOTO,'consent':False},400)
        with k.cn() as c:c.execute('UPDATE players SET photo_data=?,photo_consent=0 WHERE game_id=?',(PHOTO,self.g['id']))
        self.assertEqual(self.post('hero',{'host':self.host})['status'],'no_photo')
        self.assertEqual(self.calls,[])

    def test_ai_failure_is_terminal_and_game_continues(self):
        self.room();self.provider_fail=True;self.release.set();self.reveal();st=self.wait_status('failed')
        self.assertIsNone(st['hero']);self.assertTrue(st['subject']['photo_url'])
        for _ in range(3):self.assertEqual(self.post('hero',{'host':self.host})['status'],'failed')
        self.post('next',{'host':self.host});self.assertEqual(self.state()['round'],1)
        self.assertEqual(len(self.calls),1)

    def test_replay_during_generation_discards_old_result_and_url(self):
        self.room();st=self.reveal();self.assertTrue(self.entered.wait(1))
        oldrun=st['image_run']
        with k.cn() as c:c.execute("UPDATE games SET status='finished' WHERE id=?",(self.g['id'],))
        self.post('replay',{'host':self.host});self.post('start',{'host':self.host})
        self.release.set();time.sleep(.08)
        st=self.state();self.assertGreater(st['image_run'],oldrun);self.assertIsNone(st['hero'])
        self.post('hero',{'host':self.host,'image_run':oldrun},409)
        request(f'/api/hero-image/{self.code}/0?run={oldrun}',expect=404,raw=True)
        with k.cn() as c:self.assertIsNone(c.execute('SELECT 1 FROM hero_scenes WHERE game_id=?',(self.g['id'],)).fetchone())
        self.entered.clear();self.reveal();self.wait_status('ready');self.assertEqual(len(self.calls),2)

    def test_final_hero_async_winner_first_prize_and_cache(self):
        self.room(4,4)
        with k.cn() as c:
            c.execute("UPDATE games SET status='finished',prize='a tropical holiday' WHERE id=?",(self.g['id'],))
            c.execute("UPDATE players SET score=10 WHERE game_id=? AND name='Cara'",(self.g['id'],))
        start=time.monotonic();self.post('finalhero',{'host':self.host},202)
        self.assertLess(time.monotonic()-start,1);self.assertEqual(self.state()['status'],'finished')
        self.assertTrue(self.entered.wait(1));self.assertEqual(self.calls[0]['items'][0][0],'Cara')
        self.assertTrue(self.calls[0]['final'])
        self.assertEqual(self.calls[0]['focus'],'Cara');self.assertIn('tropical holiday',self.calls[0]['answer'])
        self.post('finalhero',{'host':self.host},202);self.assertEqual(len(self.calls),1)
        self.release.set();st=self.wait_status('ready',True)
        self.assertEqual(self.post('finalhero',{'host':self.host})['image'],st['final_hero'])
        request(st['final_hero'],raw=True);self.assertNotIn('base64',json.dumps(st))

    def test_winner_without_photo_falls_back(self):
        self.room(2,1)
        with k.cn() as c:
            c.execute("UPDATE games SET status='finished' WHERE id=?",(self.g['id'],))
            c.execute("UPDATE players SET score=10 WHERE game_id=? AND name='Bob'",(self.g['id'],))
        self.assertEqual(self.post('finalhero',{'host':self.host})['status'],'no_photo')
        self.assertEqual(self.calls,[])

    def test_invalid_mime_and_upload_save_read(self):
        self.room(2,0)
        for invalid in ['data:image/jpeg;base64,broken', image('PNG').replace('image/png','image/jpeg'), 'data:image/svg+xml;base64,PHN2Zz4=']:
            self.post('photo',{'token':self.tokens['Alice'],'data_url':invalid,'consent':True},400)
        for fmt in ['JPEG','PNG','WEBP']:
            data=image(fmt);self.post('photo',{'token':self.tokens['Alice'],'data_url':data,'consent':True})
            st=self.state();raw,headers=request(st['players'][0]['photo_url'],raw=True)
            self.assertEqual(raw,base64.b64decode(data.split(',')[1]))
            self.assertEqual(headers['Cache-Control'],'private, no-cache')
            self.assertEqual(visuals._file(data,0)[2],headers['Content-Type'])

    def test_interrupted_job_expires_without_new_ai(self):
        self.room();self.reveal();self.assertTrue(self.entered.wait(1))
        with k.cn() as c:c.execute('UPDATE image_jobs SET deadline=0 WHERE game_id=?',(self.g['id'],))
        st=self.state();self.assertEqual(st['hero_status'],'failed')
        self.release.set();time.sleep(.05)
        self.assertIsNone(self.state()['hero']);self.assertEqual(len(self.calls),1)
        self.assertEqual(self.post('hero',{'host':self.host})['status'],'failed')

    def test_queued_restart_recovery_claims_once(self):
        self.room()
        with patch.object(jobs.POOL,'submit'):
            self.reveal()
        self.assertEqual(self.calls,[])
        self.assertEqual(self.state()['hero_status'],'queued')
        jobs.recover(k.cn,k.generate_many);jobs.recover(k.cn,k.generate_many)
        self.assertTrue(self.entered.wait(1));self.release.set();self.wait_status('ready')
        self.assertEqual(len(self.calls),1)

    def test_storage_retry_retains_generated_bytes(self):
        self.room()
        with patch.object(jobs.POOL,'submit'):
            self.reveal()
        with k.cn() as c:
            row=c.execute('SELECT * FROM image_jobs WHERE game_id=?',(self.g['id'],)).fetchone()
        original=k.cn;inserts=[]
        class Store:
            def __enter__(inner):inner.c=original();inner.c.__enter__();return inner
            def __exit__(inner,*args):return inner.c.__exit__(*args)
            def execute(inner,sql,args=()):
                if sql.startswith('INSERT INTO hero_scenes'):
                    inserts.append(1)
                    if len(inserts)==1:raise RuntimeError('temporary storage failure')
                return inner.c.execute(sql,args)
        self.release.set()
        jobs.work(Store,self.g['id'],row['image_run'],row['round_no'],row['job_id'],k.generate_many)
        self.wait_status('ready');self.assertEqual(len(inserts),2);self.assertEqual(len(self.calls),1)


class ProviderTests(unittest.TestCase):
    def test_story_prompt_does_not_inherit_final_awards(self):
        question='Who would Alice call after sending an embarrassing message?'
        story=visuals.prompt_for(question,'Bob',['Alice','Bob'],'Alice','Bob')
        self.assertIn(question,story);self.assertIn('ROUND STORY SCENE',story)
        self.assertNotIn('trophy',story);self.assertNotIn('FINAL WINNER POSTER',story)
        poster=visuals.prompt_for('Prize: holiday','Winner: Bob',['Bob','Alice'],'Bob',final=True)
        self.assertIn('FINAL WINNER POSTER: Bob is the winner',poster)
        self.assertIn('trophy',poster);self.assertNotIn('ROUND STORY SCENE',poster)

    def call(self,outcomes):
        calls=[];constructor=[]
        class Client:
            def __init__(self,**kw):constructor.append(kw);self.images=self
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def edit(self,**kw):
                calls.append(kw);result=outcomes.pop(0)
                if isinstance(result,Exception):raise result
                return result
        with patch.dict(sys.modules,{'openai':types.SimpleNamespace(OpenAI=Client)}),patch.object(visuals.time,'sleep'):
            try:result=visuals.generate_many([('Alice',PHOTO)],'Question','Answer','Alice')
            except Exception as e:result=e
        return result,calls,constructor

    def test_request_parse_and_retry_policy(self):
        os.environ['OPENAI_API_KEY']='test-only'
        good=types.SimpleNamespace(data=[types.SimpleNamespace(b64_json=ART.split(',')[1])],usage=None)
        error=RuntimeError('temporary');error.status_code=429
        result,calls,ctor=self.call([error,good]);self.assertEqual(result,ART);self.assertEqual(len(calls),2)
        self.assertEqual(ctor[0]['max_retries'],0);self.assertEqual(calls[0]['model'],'gpt-image-2')
        self.assertNotIn('input_fidelity',calls[0]);self.assertEqual(calls[0]['image'][0][2],'image/jpeg')
        self.assertIn('EXACTLY 1 distinct people',calls[0]['prompt']);self.assertEqual(calls[0]['n'],1)
        for err in [TimeoutError('timeout'),RuntimeError('empty')]:
            _,calls,_=self.call([err,good]);self.assertEqual(len(calls),1)
        empty=types.SimpleNamespace(data=[])
        result,calls,_=self.call([empty]);self.assertIsInstance(result,ValueError);self.assertEqual(len(calls),1)
        quota=RuntimeError('quota');quota.status_code=429;quota.code='insufficient_quota'
        _,calls,_=self.call([quota,good]);self.assertEqual(len(calls),1)


if __name__=='__main__':
    try:unittest.main(verbosity=2)
    finally:SERVER.shutdown();jobs.POOL.shutdown(wait=True)
