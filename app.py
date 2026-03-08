from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    layout = []

    if request.method == "POST":
        def get_val(name):
            v = request.form.get(name)
            return float(v) if v and v.strip() != "" else None

        N = get_val("N")
        L = get_val("L")
        G = get_val("G")
        R = get_val("R")

        # --- Calculations ---
        if R and L and G and not N:
            N = int((R + G) // (L + G))
        elif R and N and L and not G:
            G = (R - N * L) / (N - 1) if N > 1 else 0
        elif R and N and G and not L:
            L = (R - (N - 1) * G) / N
        elif N and L and G and not R:
            R = N * L + (N - 1) * G

        P = (L + G) if L is not None and G is not None else None
        T = (N * L) if N is not None and L is not None else None

        # --- Layout for visualization ---
        if N and L is not None:
            for i in range(int(N)):
                layout.append({"type": "weld", "length": L})
                if i < int(N) - 1 and G is not None:
                    layout.append({"type": "gap", "length": G})

        result = {
            "N": round(N, 2) if N is not None else None,
            "L": round(L, 2) if L is not None else None,
            "G": round(G, 2) if G is not None else None,
            "R": round(R, 2) if R is not None else None,
            "P": round(P, 2) if P is not None else None,
            "T": round(T, 2) if T is not None else None
        }

    return render_template("index.html", result=result, layout=layout)

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
