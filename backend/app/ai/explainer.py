def explain(analysis):
    return (
        f"The QHI is {analysis['health']['score']}/100 because the score combines "
        "depth, gate efficiency, qubit utilization, two-qubit efficiency, noise exposure, "
        "and optimization potential using project-specific weights."
    )
