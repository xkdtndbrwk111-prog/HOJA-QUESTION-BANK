import sys, tempfile, unittest, json, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from verify_repository import cartridge_version, inventory, verify, ROOT

class Repository(unittest.TestCase):
    def test_baseline(self): verify(ROOT)
    def test_catalog_boundary(self):
        v=inventory(ROOT)
        self.assertEqual(len(v['cartridges']),76)
        self.assertEqual(len(v['samples']),2)
        self.assertTrue(all(x['status']=='held_for_review' for x in v['cartridges']))
        self.assertTrue(all(x['status']=='test_only' for x in v['samples']))
    def test_asset_mutation_changes_version(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sample'; shutil.copytree(ROOT/'samples/math5-fractions-demo',p)
            old=cartridge_version(p)['version']; f=next((p/'assets').glob('*.svg')); f.write_bytes(f.read_bytes()+b'\n')
            self.assertNotEqual(old,cartridge_version(p)['version'])
    def test_json_mutation_changes_version(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sample'; shutil.copytree(ROOT/'samples/math5-fractions-demo',p)
            old=cartridge_version(p)['version']; f=p/'cartridge.json'; f.write_bytes(f.read_bytes()+b'\n')
            self.assertNotEqual(old,cartridge_version(p)['version'])
    def test_missing_media_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sample'; shutil.copytree(ROOT/'samples/math5-fractions-demo',p)
            next((p/'assets').glob('*.svg')).unlink()
            with self.assertRaises(ValueError): cartridge_version(p)
    def test_path_escape_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sample'; shutil.copytree(ROOT/'samples/math5-fractions-demo',p)
            f=p/'cartridge.json'; q=json.loads(f.read_text())
            q['questions'][0]['content'].append({'kind':'image','src':'assets/../../outside.svg','alt':'x'})
            f.write_text(json.dumps(q))
            with self.assertRaises(ValueError): cartridge_version(p)
if __name__=='__main__': unittest.main(verbosity=2)
