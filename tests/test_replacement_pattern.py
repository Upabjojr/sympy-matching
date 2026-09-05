"""SymPyReplacementPattern is a plain dataclass: no pydantic anywhere."""
import subprocess
import sys

import pytest
from sympy import Ne, Symbol, cos, sin

from sympy_matching.matching_rule import SymPyReplacementPattern, build_replacer, to_omnimatch_expression
from sympy_matching.conversion import omnimatch_to_sympy
from sympy_matching.wild import WildSymbol

x = Symbol('x')
a_ = WildSymbol('a_')


def test_keyword_only_with_defaults_and_coercions():
    rule = SymPyReplacementPattern(pattern=sin(a_)**2, replacement=1 - cos(a_)**2)
    assert rule.constraints == () and rule.module_name == '' and rule.rule_number == 0
    rule = SymPyReplacementPattern(pattern=x**a_, constraints=[Ne(a_, -1)], replacement=x**(a_ + 1)/(a_ + 1),
                                   module_name='doc', rule_number='7')
    assert rule.constraints == (Ne(a_, -1),) and isinstance(rule.constraints, tuple)
    assert rule.rule_number == 7 and rule.module_name == 'doc'
    with pytest.raises(TypeError):
        SymPyReplacementPattern(sin(a_)**2, 1 - cos(a_)**2)          # positional: refused, as before
    with pytest.raises(TypeError):
        SymPyReplacementPattern(pattern=sin(a_)**2)                  # replacement is required


def test_equality_and_repr_hold_sympy_objects():
    r1 = SymPyReplacementPattern(pattern=sin(a_)**2, replacement=1 - cos(a_)**2, module_name='m', rule_number=1)
    r2 = SymPyReplacementPattern(pattern=sin(a_)**2, replacement=1 - cos(a_)**2, module_name='m', rule_number=1)
    assert r1 == r2 and 'SymPyReplacementPattern(' in repr(r1) and 'module_name=' in repr(r1)


def test_the_replacer_still_takes_it():
    rule = SymPyReplacementPattern(pattern=x**a_, constraints=(Ne(a_, -1),), replacement=x**(a_ + 1)/(a_ + 1))
    replacer = build_replacer([rule])
    rewritten, _fired = replacer.replace(to_omnimatch_expression(x**3))
    assert omnimatch_to_sympy(rewritten) == x**4/4


def test_the_package_imports_without_pydantic():
    """pydantic is not a dependency any more: importing the package with
    pydantic made unavailable must work."""
    code = "import sys; sys.modules['pydantic'] = None; import sympy_matching, sympy_matching.matching_rule; print('ok')"
    out = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, cwd=None)
    assert out.returncode == 0 and out.stdout.strip() == 'ok', out.stderr
