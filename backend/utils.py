_collected_answers: dict[str,str] = {}

def input_once(prompt: str, input_func=input) -> str:
    key = prompt.strip().lower()
    if key in _collected_answers:
        return _collected_answers[key]
    ans = input_func(prompt)
    _collected_answers[key] = ans
    return ans