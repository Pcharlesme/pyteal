import pytest

from .. import *

# this is not necessary but mypy complains if it's not included
from .. import CompileOptions

options = CompileOptions()


def test_for_compiles():
    expr = For(Int(0), Int(1), Int(2)).Do(App.globalPut(Itob(Int(0)), Itob(Int(2))))
    assert expr.type_of() == TealType.none
    expr.__teal__(options)

    expr = For(Int(0), Int(1), Int(2)).Do(App.globalPut(Itob(Int(0)), Itob(Int(2))))
    assert expr.type_of() == TealType.none
    expr.__teal__(options)


def test_nested_for_compiles():
    i = ScratchVar()
    expr = For(Int(0), Int(1), Int(2)).Do(
        Seq([For(Int(0), Int(1), Int(2)).Do(Seq([i.store(Int(0))]))])
    )
    assert expr.type_of() == TealType.none


def test_continue_break():
    expr = For(Int(0), Int(1), Int(2)).Do(Seq([If(Int(1), Break(), Continue())]))
    assert expr.type_of() == TealType.none
    expr.__teal__(options)


def test_for():
    i = ScratchVar()
    items = [
        (i.store(Int(0))),
        i.load() < Int(10),
        i.store(i.load() + Int(1)),
        App.globalPut(Itob(i.load()), i.load() * Int(2)),
    ]
    expr = For(items[0], items[1], items[2]).Do(Seq([items[3]]))

    assert expr.type_of() == TealType.none

    expected, varEnd = items[0].__teal__(options)
    condStart, condEnd = items[1].__teal__(options)
    stepStart, stepEnd = items[2].__teal__(options)
    do, doEnd = Seq([items[3]]).__teal__(options)
    expectedBranch = TealConditionalBlock([])
    end = TealSimpleBlock([])

    varEnd.setNextBlock(condStart)
    doEnd.setNextBlock(stepStart)

    expectedBranch.setTrueBlock(do)
    expectedBranch.setFalseBlock(end)
    condEnd.setNextBlock(expectedBranch)
    stepEnd.setNextBlock(condStart)

    actual, _ = expr.__teal__(options)

    assert actual == expected


def test_invalid_for():
    with pytest.raises(TypeError):
        expr = For()

    with pytest.raises(TypeError):
        expr = For(Int(2))

    with pytest.raises(TypeError):
        expr = For(Int(1), Int(2))

    with pytest.raises(TealCompileError):
        expr = For(Int(0), Int(1), Int(2))
        expr.__teal__(options)

    with pytest.raises(TealCompileError):
        expr = For(Int(0), Int(1), Int(2))
        expr.type_of()

    with pytest.raises(TealCompileError):
        expr = For(Int(0), Int(1), Int(2))
        expr.__str__()

    with pytest.raises(TealTypeError):
        expr = For(Int(0), Int(1), Int(2)).Do(Int(0))

    with pytest.raises(TealCompileError):
        expr = For(Int(0), Int(1), Int(2)).Do(Continue()).Do(Continue())
        expr.__str__()