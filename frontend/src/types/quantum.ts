export type Metrics = {
  qubits: number;
  gate_count: number;
  depth: number;
  one_qubit_gates: number;
  two_qubit_gates: number;
  two_qubit_ratio: number;
  gate_density: number;
  measurement_ratio: number;
  gate_counts: Record<string, number>;
};

export type Circuit = {
  [key: string]: unknown;
};

export type Analysis = {
  success: boolean;
  parser: string;
  metrics: Metrics;
  circuit: Circuit;

  health: {
    score: number;
    category: string;
    components: Record<string, number>;
  };

  anomaly: {
    anomaly: boolean;
    score: number;
  };

  noise: Record<string, unknown>;

  recommendations: {
    summary: string;
    recommendations: string[];
    provider: string;
  };

  explanation: string;
};