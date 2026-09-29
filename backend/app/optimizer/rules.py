from app.optimizer.gate_cancellation import cancel_adjacent

def rule_optimize(gates):
    return cancel_adjacent(gates)
