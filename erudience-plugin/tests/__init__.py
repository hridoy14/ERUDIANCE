"""Test package bootstrap.

Inserts the canonical module directories into ``sys.path`` so the
historical bare imports used by the test files (``from gate_chain_v41
import ...`` etc.) keep resolving after the consolidation move.
``unittest discover`` imports this package before the test modules.
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
for _d in ("core", "core/legacy", "rendering",
           "modules/brand_claims_qa", "modules/creative_brief",
           "modules/competitor_intelligence", "modules/linkedin_copywriting",
           "modules/topic_intelligence", "modules/analytics_learning",
           "modules/marketing_strategy", "tests"):
    _p = str(_ROOT / _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)
