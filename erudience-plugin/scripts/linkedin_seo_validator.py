"""Compatibility shim — canonical implementation moved to modules/topic_intelligence/linkedin_seo_validator.py.

Preserves the historical import path. Do not add new behaviour here;
edit the canonical module instead.
"""
import sys as _sys
from pathlib import Path as _Path
import importlib.util as _ilu

_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / "modules/topic_intelligence"))
_p = _Path(__file__).resolve().parent.parent / "modules/topic_intelligence" / "linkedin_seo_validator.py"
if __name__ == "__main__":
    import runpy as _runpy
    _runpy.run_path(str(_p), run_name="__main__")
else:
    _spec = _ilu.spec_from_file_location("_canonical_linkedin_seo_validator", _p)
    _mod = _ilu.module_from_spec(_spec)
    _sys.modules["_canonical_linkedin_seo_validator"] = _mod
    _spec.loader.exec_module(_mod)
    globals().update({k: v for k, v in vars(_mod).items() if not k.startswith("__")})
