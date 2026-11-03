"""Vocabulary discovery cannot inspect selection, stopping, or test cohorts."""
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from expand_regression_vocabulary import fitting_rows


def test_small_cohort_excludes_reserved_training_selection():
    rows=[(1,0,False,.05,'macho',0),(2,1,False,.2,'macho',0),
          (3,1,False,.8,'macho',0),(4,1,True,.2,'macho',0)]
    assert fitting_rows(rows)==[(2,1)]


def test_large_development_cohort_keeps_full_fitting_partition():
    rows=[(1,0,False,.05,'macho',0),(2,1,False,.2,'macho',0),
          (3,1,False,.8,'macho',0)]
    for label in (0,1):
        for bucket in (.2,.8):
            rows.extend((100+len(rows)+i,label,True,bucket,'macho',0) for i in range(30))
    assert fitting_rows(rows)==[(2,1),(3,1)]
