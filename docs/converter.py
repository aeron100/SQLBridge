import json
import sqlglot
from sqlglot import exp
from sqlglot.errors import ErrorLevel
from sqlglot.transforms import eliminate_join_marks

def sanitize_comments(tree):
 # Comments are re-emitted as /* ... */ blocks, so a delimiter inside a body would end the
 # comment early (and PostgreSQL nests block comments). Neutralize both delimiters.
 for node in tree.walk():
  if node.comments: node.comments=[c.replace('*/','* /').replace('/*','/ *') for c in node.comments]

def validate_output(sql):
 # Fail closed: the generated text must re-parse as exactly one statement PostgreSQL understands.
 trees=[t for t in sqlglot.parse(sql,read='postgres',error_level=ErrorLevel.RAISE) if t is not None]
 if len(trees)!=1: raise ValueError('Conversion produced an unexpected number of statements, so the result was withheld. Simplify the query and try again.')
 if isinstance(trees[0],exp.Command) or trees[0].find(exp.Command): raise ValueError('Conversion produced a statement that could not be validated as PostgreSQL. This query needs manual migration.')
 return trees[0]

def convert(source, pretty=True):
 if not source.strip(): return {'sql':'','notes':[], 'count':0}
 if len(source)>150000: raise ValueError('Please use a query smaller than 150,000 characters.')
 trees=sqlglot.parse(source,read='oracle',error_level=ErrorLevel.RAISE)
 outputs=[];notes=[]
 for tree in trees:
  if tree is None: continue
  if isinstance(tree,exp.Command): raise ValueError('This statement needs manual migration. Use SQL queries rather than PL/SQL blocks or SQL*Plus commands.')
  if tree.find(exp.Connect): raise ValueError('CONNECT BY needs a recursive CTE rewrite. This converter cannot safely infer that rewrite.')
  if any(c.name.upper()=='ROWNUM' for c in tree.find_all(exp.Column)):
   raise ValueError('ROWNUM needs a manual rewrite using LIMIT or ROW_NUMBER(). Its placement relative to ORDER BY changes the result, so automatic conversion is paused.')
  if any(c.name.upper()=='ROWID' for c in tree.find_all(exp.Column)):
   notes.append('ROWID is Oracle-specific. Replace it with a stable primary key before running this query.')
  if any(n.args.get('join_mark') for n in tree.walk()):
   tree=eliminate_join_marks(tree);notes.append('Rewrote Oracle (+) join notation as explicit ANSI joins. Verify join conditions and expected rows.')
   if any(n.args.get('join_mark') for n in tree.walk()):raise ValueError('This Oracle (+) join could not be safely rewritten. Convert it to explicit ANSI joins first.')
  for table in list(tree.find_all(exp.Table)):
   if table.name.upper()=='DUAL' and not table.db:
    parent=table.parent
    if isinstance(parent,exp.From) and isinstance(parent.parent,exp.Select) and not parent.parent.args.get('joins'):
     parent.parent.set('from',None)
     parent.parent.set('from_',None)
     notes.append('Removed Oracle’s DUAL pseudo-table.')
  unknown=sorted({n.name for n in tree.find_all(exp.Anonymous)})
  if unknown:notes.append('Check these functions in your PostgreSQL environment: '+', '.join(unknown)+'. Custom and Oracle-specific functions may need manual replacements.')
  sanitize_comments(tree)
  result=tree.sql(dialect='postgres',pretty=pretty,unsupported_level=ErrorLevel.RAISE)
  validate_output(result)
  outputs.append(result.rstrip(';')+';')
 return {'sql':'\n\n'.join(outputs),'notes':list(dict.fromkeys(notes)), 'count':len(outputs)}
