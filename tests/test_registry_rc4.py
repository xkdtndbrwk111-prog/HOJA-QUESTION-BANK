"""Local registered-cartridge integrity checks, including negative cases; no remote writes."""
import sys, unittest,copy,tempfile,shutil,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from register_cartridge import catalog,entry,unpack,write_catalog,dump
from classification_rc4 import check,key
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);shutil.copytree(ROOT,self.root/'bank',ignore=shutil.ignore_patterns('.git','__pycache__'));self.r=self.root/'bank';self.p=self.r/'cartridges/eng5-ham-u10'
 def tearDown(self):self.tmp.cleanup()
 def change(self,name,fn):p=self.p/name;x=json.loads(p.read_text());fn(x);dump(p,x)
 def test_catalog(self):c=catalog(self.r);self.assertEqual(c,json.loads((self.r/'catalog.json').read_text()));self.assertEqual((c['approvedCount'],c['legacyHeldCount']),(1,76));self.assertEqual(c['cartridges'][0]['deliveryStatus'],'HOLD')
 def test_approval_mismatch(self):self.change('approval.json',lambda x:x.update(version='bad'));self.assertRaises(ValueError,catalog,self.r)
 def test_approval_pending(self):self.change('approval.json',lambda x:x.update(teacherApproval='PENDING'));self.assertRaises(ValueError,catalog,self.r)
 def test_asset_tamper(self):p=self.p/'assets/bed_clock_9_40.webp';p.write_bytes(p.read_bytes()+b'X');self.assertRaises(ValueError,catalog,self.r)
 def test_legacy_tamper(self):p=next((self.r/'cartridges').glob('legacy-*/cartridge.json'));p.write_bytes(p.read_bytes()+b' ');self.assertRaises(ValueError,catalog,self.r)
 def test_publish_block(self):self.change('approval.json',lambda x:x.update(deliveryStatus='PUBLISHED'));self.assertRaises(ValueError,catalog,self.r)
 def test_history_tamper(self):self.change('history/rev3/cartridge.json',lambda x:x.update(title='tampered'));self.assertRaises(ValueError,catalog,self.r)
 # standalone zip test
 def test_zip_traversal(self):
  z=self.root/'unsafe.zip';d=self.root/'out';d.mkdir()
  with zipfile.ZipFile(z,'w') as f:f.writestr('version.json','{"files":{}}');f.writestr('../bad','x')
  self.assertRaises(ValueError,unpack,z,d);self.assertFalse((self.root/'bad').exists())
if __name__=='__main__':unittest.main(verbosity=2)
