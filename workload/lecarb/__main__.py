"""Le Carb - LEarned CARdinality estimator Benchmark

Usage:
  lecarb workload gen [-s <seed>] [-d <dataset>] [-v <version>] [-w <workload>] [--params <params>] [--no-label] [-o <old_version>] [-r <ratio>]
  lecarb workload label [-d <dataset>] [-v <version>] [-w <workload>]
  lecarb workload quicksel [-d <dataset>] [-v <version>] [-w <workload>] [--params <params>] [--overwrite]

Options:
  -s, --seed <seed>                Random seed.
  -d, --dataset <dataset>          The input dataset [default: census13].
  -v, --dataset-version <version>  Dataset version [default: original].
  -w, --workload <workload>        Name of the workload [default: base].
  -e, --estimator <estimator>      Name of the estimator [default: naru].
  --params <params>                Parameters that are needed.
  --sizelimit <sizelimit>          Size budget of method, percentage to data size [default: 0.015].
  --no-label                       Do not generate ground truth label when generate workload.
  --overwrite                      Overwrite the result.
  -o, --old-version <old_version>  When data updates, query should focus more on the new data. The <old version> is what QueryGenerator refers to.
  -r, --win-ratio <ratio>          QueryGen only touch last <win_ratio> * size_of(<old version>).
  -h --help                        Show this screen.
"""
from ast import literal_eval
from time import time

from docopt import docopt

from .workload.gen_workload import generate_workload
from .workload.gen_label import generate_labels
from .workload.dump_quicksel import dump_quicksel_query_files, generate_quicksel_permanent_assertions
from .workload.workload import dump_sqls

if __name__ == "__main__":
    args = docopt(__doc__, version="Le Carb 0.1")

    seed = args["--seed"]
    if seed is None:
        seed = int(time())
    else:
        seed = int(seed)

    if args["workload"]:
        if args["gen"]:
            generate_workload(
                seed,
                dataset=args["--dataset"],
                version=args["--dataset-version"],
                name=args["--workload"],
                no_label = args["--no-label"],
                old_version=args["--old-version"],
                win_ratio=args["--win-ratio"],
                params = literal_eval(args["--params"])
            )
        elif args["label"]:
            generate_labels(
                dataset=args["--dataset"],
                version=args["--dataset-version"],
                workload=args["--workload"]
            )
        elif args["quicksel"]:
            dump_quicksel_query_files(
                dataset=args["--dataset"],
                version=args["--dataset-version"],
                workload=args["--workload"],
                overwrite=args["--overwrite"]
            )
            generate_quicksel_permanent_assertions(
                dataset=args["--dataset"],
                version=args["--dataset-version"],
                params=literal_eval(args["--params"]),
                overwrite=args["--overwrite"]
            )
        elif args["dump"]:
            dump_sqls(
                dataset=args["--dataset"],
                version=args["--dataset-version"],
                workload=args["--workload"])
        else:
            raise NotImplementedError
        exit(0)

