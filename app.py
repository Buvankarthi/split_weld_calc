from flask import Flask, render_template, request

app = Flask(__name__)

# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def validate_positive(*values):
    """Ensure all values are positive numbers"""
    return all(v is not None and v > 0 for v in values)

def calculate_pitch(L, G):
    """Calculate pitch: P = L + G"""
    if L is not None and G is not None:
        return L + G
    return None

def calculate_total_weld_material(N, L):
    """Calculate total weld material: T = N × L"""
    if N is not None and L is not None:
        return N * L
    return None

def calculate_coverage_percentage(T, R):
    """Calculate weld coverage percentage: Coverage = (T / R) × 100"""
    if T is not None and R is not None and R > 0:
        return (T / R) * 100
    return None



def generate_layout_visualization(N, L, G):
    """Generate layout data for CSS-based visualization"""
    layout = []
    if N and L is not None:
        for i in range(int(N)):
            layout.append({"type": "weld", "length": L})
            if i < int(N) - 1 and G is not None:
                layout.append({"type": "gap", "length": G})
    return layout

def check_warnings(N, L, G, R, coverage):
    """Check for warning conditions"""
    warnings = []
    
    # Check if gap is too large (> 50mm or > 50% of weld length)
    if G is not None and L is not None and G > L:
        warnings.append(f"⚠ Gap ({G}mm) exceeds weld length ({L}mm) - sparse weld pattern")
    
    if G is not None and G > 50:
        warnings.append(f"⚠ Large gap detected: {G}mm - may affect structural integrity")
    
    # Check if coverage is too low
    if coverage is not None and coverage < 30:
        warnings.append(f"⚠ Low coverage: {round(coverage, 1)}% - consider increasing bead density")
    
    # Check if too many beads
    if N is not None and N > 100:
        warnings.append(f"⚠ Very high bead count: {int(N)} - verify calculation")
    
    return warnings

# ============================================================================
# FLASK ROUTE
# ============================================================================

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    layout = []
    warnings = []

    if request.method == "POST":
        def get_val(name):
            v = request.form.get(name)
            return float(v) if v and v.strip() != "" else None

        N = get_val("N")
        L = get_val("L")
        G = get_val("G")
        R = get_val("R")

        # --- AUTO-SOLVE FOR MISSING PARAMETER ---
        try:
            if N is None and validate_positive(R, L, G):
                # Solve for N: N = (R + G) / (L + G)
                N = (R + G) / (L + G)
            elif L is None and validate_positive(R, N, G):
                # Solve for L: L = (R - (N - 1) × G) / N
                L = (R - (N - 1) * G) / N
            elif G is None and validate_positive(R, N, L) and N > 1:
                # Solve for G: G = (R - N × L) / (N - 1)
                G = (R - N * L) / (N - 1)
            elif R is None and validate_positive(N, L, G):
                # Solve for R: R = N × L + (N - 1) × G
                R = N * L + (N - 1) * G

            # --- CALCULATE SECONDARY PARAMETERS ---
            P = calculate_pitch(L, G)
            T = calculate_total_weld_material(N, L)
            coverage = calculate_coverage_percentage(T, R)

            # --- GENERATE VISUALIZATIONS ---
            layout = generate_layout_visualization(N, L, G)
            
            # --- CALCULATE VISUALIZATION SCALE ---
            # Scale visualization to fit ~650px width for full run length
            visualization_scale = 650 / R if R and R > 0 else 0.5

            # --- CHECK WARNINGS ---
            warnings = check_warnings(N, L, G, R, coverage)

            # --- BUILD RESULT DICTIONARY ---
            result = {
                "N": round(N, 2) if N is not None else None,
                "L": round(L, 2) if L is not None else None,
                "G": round(G, 2) if G is not None else None,
                "R": round(R, 2) if R is not None else None,
                "P": round(P, 2) if P is not None else None,
                "T": round(T, 2) if T is not None else None,
                "coverage": round(coverage, 1) if coverage is not None else None,
            }

        except (ValueError, ZeroDivisionError) as e:
            warnings = [f"❌ Calculation error: {str(e)}"]

    return render_template(
        "index.html", 
        result=result, 
        layout=layout, 
        warnings=warnings,
        visualization_scale=visualization_scale if request.method == "POST" else 0.5
    )

if __name__ == "__main__":
    app.run(debug=True)
