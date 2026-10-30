import sys, pathlib, unittest
sys.path.insert(0,str(next(pathlib.Path('docs/vendor').glob('*.whl'))))
sys.path.insert(0,'docs')
from converter import convert
import sqlglot
from sqlglot import exp
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
 def test_comment_cannot_add_statements(self):
  # A '--' comment is re-emitted as /* ... */; a '*/' inside its body must not close it early.
  r=convert('-- note */ ; DROP TABLE t; /* tail\nSELECT 1 FROM dual')
  stmts=[t for t in sqlglot.parse(r['sql'],read='postgres') if t is not None]
  self.assertEqual(len(stmts),1);self.assertIsInstance(stmts[0],exp.Select);self.assertEqual(r['count'],1)
 def test_comment_body_has_no_delimiters(self):
  # PostgreSQL nests block comments, so a '/*' inside a comment body would leave the output unterminated.
  r=convert('-- a /* b\nSELECT 1 FROM dual')
  bodies=[c for t in sqlglot.parse(r['sql'],read='postgres') if t is not None for n in t.walk() for c in (n.comments or [])]
  self.assertTrue(bodies);self.assertFalse([c for c in bodies if '/*' in c or '*/' in c],bodies)
 def test_output_check_rejects_multiple_statements(self):
  from converter import validate_output
  with self.assertRaises(ValueError):validate_output('SELECT 1; DROP TABLE t')
 def test_output_check_rejects_commands(self):
  from converter import validate_output
  with self.assertLogs('sqlglot',level='WARNING'),self.assertRaises(ValueError):validate_output('VACUUM t')
 def test_output_check_accepts_single_statement(self):
  from converter import validate_output
  validate_output('SELECT 1')
if __name__=='__main__':unittest.main()
