import argparse

def load_prompt(prompt_path: str) -> str:
    with open(f"{prompt_path}", "r", encoding="utf-8") as f:
        prompt = f.read()

    return prompt


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")