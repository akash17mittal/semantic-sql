import sys

sys.path.append('sqlglot')
from dataclasses import dataclass
from functools import cached_property

import sqlglot.expressions as exp
from sqlglot import Parser, Tokenizer, parse_one


def _remove_semantic(node):
  if isinstance(node, exp.Semantic):
    return None
  return node


@dataclass(frozen=True)
class Query(object):
  """
  class to hold sql query related data
  """
  sql_str: str

  @cached_property
  def _tokens(self):
    return Tokenizer().tokenize(self.sql_str)

  @cached_property
  def _expression(self) -> exp.Expression:
    return Parser().parse(self._tokens)[0]

  @cached_property
  def sql_query_text(self):
    return self._expression.sql()

  @cached_property
  def semantic_predicate(self):
    value = None
    for node, _, key in self._expression.walk():
      if isinstance(node, exp.Semantic):
        if value is not None:
          raise Exception(f'Multiple unexpected keywords found')
        else:
          value = node.args['this'].args['this']
    return value

  @cached_property
  def base_query_without_semantic(self):
    _exp_no_semantic = self._expression.transform(_remove_semantic)
    return _exp_no_semantic.sql()


if __name__ == '__main__':
  q1 = Query("SELECT * from a SEMANTIC 'car is red'")
  assert q1.semantic_predicate == 'car is red'
  assert q1.base_query_without_semantic == 'SELECT * FROM a'

  q2 = Query("SELECT * from a WHERE b > 100")
  assert q2.semantic_predicate is None
  assert q2.base_query_without_semantic == "SELECT * FROM a WHERE b > 100"


