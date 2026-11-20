"""Meaningful deterministic-seek, composition, and invalid-input regressions. No provider calls."""
import copy,importlib.util,io,json,sys,tempfile,unittest
from PIL import Image,ImageChops
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'scripts'));import render

class Validation(unittest.TestCase):
 def setUp(self):self.base=BASE/'examples'/'tandem';self.job=json.loads((self.base/'promo-vertical.json').read_text())
 def test_missing_claim_is_blocked(self):
  self.job['claimIds']=['not-shipped']
  with self.assertRaisesRegex(ValueError,'no usable video evidence'):render.validate(self.job,self.base)
 def test_captions_cannot_overlap(self):
  self.job['captions'][1]['start']=1
  with self.assertRaisesRegex(ValueError,'nonoverlapping'):render.validate(self.job,self.base)
 def test_changed_product_source_is_blocked(self):
  self.job['sourceHashes']['fixture/product.js']='0'*64
  with self.assertRaisesRegex(ValueError,'Source hash mismatch'):render.validate(self.job,self.base)
 def test_new_brand_cannot_silently_use_sample_interface(self):
  self.job['brand']['name']='Another product'
  with self.assertRaisesRegex(ValueError,'brand tokens alone'):render.validate(self.job,self.base)
 def test_template_cannot_silently_miss_resources(self):
  for html in ['<img src="missing.png">','<style>.p{background:url(private.png)}</style>','<link rel=stylesheet href="https://example.org/remote.css">','<style>@import "missing.css";</style>']:
   with self.subTest(html=html),self.assertRaises(ValueError):render.validate_template(html)
  render.validate_template('<style>.p{background:url(data:image/png;base64,AAAA)}</style><img src="data:image/png;base64,AAAA">')
 def test_missing_paid_provider_is_irrelevant(self):render.validate(self.job,self.base)

class Composition(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  try:from playwright.sync_api import sync_playwright
  except ImportError:raise unittest.SkipTest('Python playwright missing; install to run browser tests')
  cls.p=sync_playwright().start()
  try:cls.b=cls.p.chromium.launch(executable_path=render.browser_path(),headless=True,args=['--no-sandbox'])
  except Exception as exc:cls.p.stop();raise unittest.SkipTest('Chromium unavailable: '+str(exc))
  cls.job=json.loads((BASE/'examples/tandem/promo-vertical.json').read_text());cls.html=(BASE/'examples/tandem/composition.html').read_text()
 @classmethod
 def tearDownClass(cls):cls.b.close();cls.p.stop()
 def page(self,w,h,hook=None):
  page=self.b.new_page(viewport={'width':w,'height':h},device_scale_factor=1);page.set_content(self.html);job=copy.deepcopy(self.job)
  if hook:job['hook']=hook
  page.evaluate('(c)=>configure(c)',job);return page
 def test_nonsequential_seek_geometry_and_raster_match(self):
  with self.page(540,960) as page:
   state=page.evaluate('seek(6)');before=page.screenshot();page.evaluate('seek(1)');self.assertEqual(state,page.evaluate('seek(6)'));after=page.screenshot();diff=ImageChops.difference(Image.open(io.BytesIO(before)),Image.open(io.BytesIO(after)));self.assertLessEqual(max(high for low,high in diff.getextrema()),1) # Chromium glyph antialiasing may round one channel by one level; geometry/state must be exact.
 def test_four_native_compositions_have_readable_nonoverlapping_headings(self):
  for w,h in [(1080,1920),(1920,1080),(1080,1080),(1080,1350)]:
   with self.subTest(ratio=(w,h)),self.page(w,h,'Turn a request into a clear next step.') as page:
    page.evaluate('seek(6)');rects=page.evaluate("""() => Object.fromEntries(['headline','lede','chapter','app-wrap','caption','mode'].map(id=>{const e=document.getElementById(id),r=e.getBoundingClientRect();return [id,{x:r.x,y:r.y,right:r.right,bottom:r.bottom,visible:getComputedStyle(e).display!=='none'}]}))""")
    for key,r in rects.items():
     if r['visible']:self.assertTrue(r['x']>=0 and r['y']>=0 and r['right']<=w+1 and r['bottom']<=h+1,(key,r))
    self.assertLessEqual(rects['headline']['bottom'],rects['lede']['y'] if rects['lede']['visible'] else rects['chapter']['y'])
    if rects['lede']['visible']:self.assertLessEqual(rects['lede']['bottom'],rects['chapter']['y'] if h>=w else rects['app-wrap']['bottom'])
 def test_review_control_is_not_clipped_in_landscape(self):
  with self.page(1920,1080) as page:
   page.evaluate('seek(6)');self.assertLessEqual(page.locator('#approve').bounding_box()['y']+page.locator('#approve').bounding_box()['height'],page.locator('#app-wrap').bounding_box()['y']+page.locator('#app-wrap').bounding_box()['height']-2)
 def test_action_precedes_result_and_approval(self):
  with self.page(1080,1920) as page:
   self.assertEqual(page.evaluate('seek(2).chapter'),'A request comes in');self.assertIn('Organize',page.evaluate('seek(3).chapter'));self.assertIn('Review',page.evaluate('seek(6).chapter'));page.evaluate('seek(10)');self.assertIn('Ready for review',page.locator('#approve').inner_text())



class FootageCrop(unittest.TestCase):
 def test_crop_selects_requested_pixel_region(self):
  import shutil
  if not shutil.which('ffmpeg'):self.skipTest('FFmpeg unavailable')
  from PIL import Image,ImageDraw
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);image=Image.new('RGB',(512,512),'red');ImageDraw.Draw(image).rectangle((256,0,511,255),fill=(0,200,0));image.save(root/'input.png')
   render.run(['ffmpeg','-v','error','-y','-loop','1','-i',root/'input.png','-t','1','-r','12','-c:v','libx264','-pix_fmt','yuv420p',root/'source.mp4'])
   j={'width':640,'height':360,'fps':12,'duration':1,'hook':'Selected proof','cta':'Inspect','brand':{'name':'Fixture','background':'#ffffff','ink':'#000000','accent':'#222222'},'source':{'path':'source.mp4','start':0,'audioPolicy':'mute','crop':[256,0,256,256]},'captions':[]}
   work=root/'work';work.mkdir();render.render_footage(j,root,root/'out.mp4',work);render.run(['ffmpeg','-v','error','-i',root/'out.mp4','-frames:v','1','-c:v','png','-pix_fmt','rgb24','-threads','1','-y',root/'decoded.png']);pixel=Image.open(root/'decoded.png').getpixel((320,160));self.assertGreater(pixel[1],150);self.assertLess(pixel[0],40)

if __name__=='__main__':unittest.main(verbosity=2)
