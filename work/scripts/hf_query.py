import os
import sys
import duckdb

from huggingface_hub import HfApi

REPO = "FlyRank/internship-warehouse"
REL = "hf://datasets/" + REPO


def get_token():
    here = os.path.dirname(os.path.abspath(__file__))
    dirs = [os.getcwd(), here]
    for _ in range(3):
        here = os.path.dirname(here)
        dirs.append(here)
    for path in dirs:
        try:
            for line in open(os.path.join(path, ".env"), "r"):
                if line.strip().startswith("HF_TOKEN="):
                    return line.strip().split("=", 1)[1]
        except FileNotFoundError:
            pass
    return os.environ.get("HF_TOKEN")


def build_file_list(tok):
    files = [f for f in HfApi().list_repo_files(REPO, repo_type="dataset", token=tok) if f.endswith(".parquet")]
    return "[" + ",".join("'" + REL + "/" + f + "'" for f in files) + "]"


def main():
    tok = get_token()
    if not tok:
        print("no HF_TOKEN found (set HF_TOKEN env var or a .env file with HF_TOKEN=...)")
        sys.exit(1)

    con = duckdb.connect()
    con.execute("CREATE SECRET (TYPE huggingface, TOKEN '" + tok + "')")
    file_list = build_file_list(tok)

    def q(sql):
        return con.sql(sql.replace("$REL", REL).replace("$FILES", file_list)).fetchall()

    if len(sys.argv) > 1:
        sql = " ".join(sys.argv[1:])
        for row in q(sql):
            print(row)
    else:
        s = q("SELECT COUNT(*) n FROM read_parquet('$REL/fact_content_daily_performance_sample.parquet')")[0]
        print("sample rows:", s[0])
        print(q("DESCRIBE SELECT * FROM read_parquet('$REL/fact_content_daily_performance_sample.parquet')"))


if __name__ == "__main__":
    main()
