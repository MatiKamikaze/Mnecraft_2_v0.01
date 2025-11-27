def test_imports():
    import importlib
    importlib.import_module('game.terrain')
    importlib.import_module('game.player')
    importlib.import_module('game.ui')
    importlib.import_module('game.chunks')
    importlib.import_module('game.save')
    assert True
