import logging
from typing import List, Dict

from .workload import Label, Query, load_queryset, dump_labels
from ..estimator.estimator import Oracle
from ..dataset.dataset import Table, load_table

L = logging.getLogger(__name__)

def generate_labels_for_queries(table: Table, queryset: Dict[str, List[Query]]) -> Dict[str, List[Label]]:
    oracle = Oracle(table)
    labels = {}
    for group, queries in queryset.items():
        l = []
        for i, q in enumerate(queries):
            card, _ = oracle.query(q)
            l.append(Label(cardinality=card, selectivity=card/table.row_num))
            if (i+1) % 10000 == 0:
                L.info(f"{i+1} labels generated for {group}")
        labels[group] = l

    return labels

def generate_labels(dataset: str, version: str, workload: str) -> None:

    L.info("Load table...")
    table = load_table(dataset, version)

    L.info("Load queryset from disk...")
    queryset = load_queryset(dataset, workload)

    L.info("Start generate ground truth labels for the workload...")
    labels = generate_labels_for_queries(table, queryset)

    L.info("Dump labels to disk...")
    dump_labels(dataset, version, workload, labels)


