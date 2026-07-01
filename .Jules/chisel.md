## 2024-07-01 - Parenthesised exceptions and missing dependencies for typing checks
**Learning:** Found several syntax errors due to Python 3 exception grouping syntax `except tk.TclError, ValueError:` needing parentheses `except (tk.TclError, ValueError):`. Also noted `mypy` relies heavily on local environment stubs which weren't pre-installed. The codebase is large and relies on unstructured typing for action payloads.
**Action:** Always wrap multiple exceptions in parentheses.
