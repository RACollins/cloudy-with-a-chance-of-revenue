"""SageMaker training entrypoint (skeleton).

Real AutoGluon training will replace the stub output in a later session.
"""

import argparse
import json
import os
from pathlib import Path

from ml.feature_importance.export import export_feature_importance_stub


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAINING"))
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR", "/opt/ml/model"))
    parser.add_argument("--job-id", type=str, default=os.environ.get("SM_HP_JOB_ID", "unknown"))
    parser.add_argument("--s3-bucket", type=str, default=os.environ.get("SM_HP_S3_BUCKET", ""))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model_dir = Path(args.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)

    # Stub artifact
    (model_dir / "model.tar.gz.stub").write_text("stub-model")

    fi = export_feature_importance_stub(args.job_id)
    fi_path = model_dir / "feature_importance.json"
    fi_path.write_text(json.dumps(fi))

    # SageMaker uploads model_dir; separate S3 copy handled in full implementation.
    print(json.dumps({"status": "ok", "job_id": args.job_id, "feature_importance": fi_path.name}))


if __name__ == "__main__":
    main()
