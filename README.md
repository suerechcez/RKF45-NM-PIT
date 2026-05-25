# Runge–Kutta–Fehlberg (RKF45) — Flask Calculator

An online calculator for the adaptive **RKF45** method, built with Flask +
MathJax. The numerical core is implemented manually in pure Python.

## Run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>.

> Do **not** open `templates/index.html` directly — it is a Jinja template
> rendered by Flask. Without the server, styling and `/solve` will not work.

## Files

- `app.py` — Flask routes and safe `f(t, y)` evaluator
- `rkf45.py` — Manual RKF45 implementation
- `templates/index.html` — UI with MathJax formulas + results table
- `static/style.css` — Styles
