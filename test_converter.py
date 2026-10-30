import sys, pathlib, unittest
sys.path.insert(0,str(next(pathlib.Path('docs/vendor').glob('*.whl'))))
sys.path.insert(0,'docs')
from converter import convert
class ConverterTests(unittest.TestCase):
 def test_functions(self):
  r=convert("SELECT NVL(salary, 0), DECODE(status, 'A', 'Active', 'Other') FROM employees")
  self.assertIn('COALESCE',r['sql']);self.assertIn('CASE',r['sql'])
 def test_literals(self):
  self.assertIn("'NVL(SYSDATE)'",convert("SELECT 'NVL(SYSDATE)' FROM dual")['sql'])
 def test_joins(self):
  self.assertIn('LEFT JOIN',convert('SELECT a.id FROM a, b WHERE a.id = b.id(+)')['sql'])
 def test_dual(self):
  self.assertNotIn('FROM dual',convert('SELECT 1 FROM dual')['sql'])
 def test_multi(self):
  self.assertEqual(convert('SELECT 1 FROM dual; SELECT 2 FROM dual')['count'],2)
 def test_rownum_block(self):
  with self.assertRaises(ValueError):convert('SELECT * FROM employees WHERE ROWNUM <= 5')
 def test_invalid(self):
  with self.assertRaises(Exception):convert('SELECT ( FROM')
 def test_empty(self):
  self.assertEqual(convert('')['sql'],'')
if __name__=='__main__':unittest.main()
