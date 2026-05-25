"""Flask app for the Runge-Kutta-Fehlberg (RKF45) calculator."""
import ast
import math
import operator as op
from flask import Flask, render_template, request, jsonify

from rkf45 import solve_rkf45

app = Flask(__name__)

# Safe expression evaluator for f(t, y) -------------------------------------
_ALLOWED_BINOPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
}
_ALLOWED_UNARYOPS = {ast.UAdd: op.pos, ast.USub: op.neg}
_ALLOWED_FUNCS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan, "atan2": math.atan2,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "exp": math.exp, "log": math.log, "log10": math.log10, "log2": math.log2,
    "sqrt": math.sqrt, "abs": abs, "pow": math.pow,
    "floor": math.floor, "ceil": math.ceil,
}
_ALLOWED_NAMES = {"pi": math.pi, "e": math.e}


def _eval_node(node, vars_):
    if isinstance(node, ast.Num):  # py<3.8 compat
        return node.n
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed")
    if isinstance(node, ast.Name):
        if node.id in vars_:
            return vars_[node.id]
        if node.id in _ALLOWED_NAMES:
            return _ALLOWED_NAMES[node.id]
        raise ValueError(f"Unknown identifier: {node.id}")
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        return _ALLOWED_BINOPS[type(node.op)](
            _eval_node(node.left, vars_), _eval_node(node.right, vars_)
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        return _ALLOWED_UNARYOPS[type(node.op)](_eval_node(node.operand, vars_))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        fname = node.func.id
        if fname not in _ALLOWED_FUNCS:
            raise ValueError(f"Function not allowed: {fname}")
        args = [_eval_node(a, vars_) for a in node.args]
        return _ALLOWED_FUNCS[fname](*args)
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def make_f(expr: str):
    tree = ast.parse(expr, mode="eval")

    def f(t, y):
        return _eval_node(tree.body, {"t": t, "y": y})

    # Smoke test so errors surface before solving
    f(0.0, 0.0)
    return f


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json(force=True) or {}
    try:
        expr = str(data.get("expression", "t + y")).strip()
        t0 = float(data.get("t0", 0))
        y0 = float(data.get("y0", 1))
        t_end = float(data.get("t_end", 1))
        h = float(data.get("h", 0.1))
        tol = float(data.get("tol", 1e-6))
        h_min = float(data.get("h_min", 1e-6))
        h_max = float(data.get("h_max", 1.0))

        if t_end <= t0:
            return jsonify({"error": "t_end must be greater than t0"}), 400

        f = make_f(expr)
        results = solve_rkf45(f, t0, y0, t_end, h, tol, h_min, h_max)
        return jsonify({"results": results})
    except Exception as e:  # noqa: BLE001
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
