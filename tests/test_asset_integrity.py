import hashlib,tempfile,unittest
from pathlib import Path
from scripts.check_assets import verify_asset
class AssetIntegrityTests(unittest.TestCase):
 def test_changed_or_missing_asset_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);p=root/'license.txt';p.write_bytes(b'original notice');h=hashlib.sha256(p.read_bytes()).hexdigest();verify_asset(root,'license.txt',h);p.write_bytes(b'changed notice')
   with self.assertRaises(ValueError):verify_asset(root,'license.txt',h)
   with self.assertRaises(ValueError):verify_asset(root,'missing.txt',h)
