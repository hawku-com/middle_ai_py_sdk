# Middle AI Python SDK

This provides an SDK to trace your Python application calls LLMs

## Install

```bash
$ pip install git+https://github.com/hawku-com/middle_ai_py_sdk.git
```

## How to use

```python
from middle_ai_sdk.tracer import Tracer

tracer = Tracer('app_reference')

def foo() -> None:
    model_params = { "abc": { "def": '1', "ghi": '2'}, "jkl": '3' }
    span = tracer.start_trace('trace_name', 'llm_model_name', model_params, 'prompt', 'user_id', 'thread_id')

    ...

    tracer.end_trace(span, llm_output)
```
