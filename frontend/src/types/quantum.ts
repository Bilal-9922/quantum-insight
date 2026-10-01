export type HardwareRecommendation = {
  type?: string;
  priority?: "low" | "moderate" | "high" | string;
  title?: string;
  message?: string;
  metric?: number;
};

export type HardwareRecommendations = {
  available?: boolean;
  execution_level?: "favorable" | "moderate" | "challenging" | string;
  summary?: string;

  hardware_characteristics?: {
    minimum_qubits?: number;
    connectivity_importance?: string;
    gate_fidelity_importance?: string;
    noise_sensitivity?: string;
  };

  recommendations?: HardwareRecommendation[];

  basis?: {
    qubits?: number;
    gate_count?: number;
    depth?: number;
    two_qubit_gates?: number;
    two_qubit_ratio?: number;
    gate_density?: number;
    qubit_utilization?: number;
    noise_score?: number;
  };

  disclaimer?: string;
};

export type Analysis = {
  success: boolean;

  validation: {
    valid: boolean;
    error: string | null;
  };

  parser?: string;

  metrics: {
    qubits: number;
    active_qubits?: number;
    qubit_utilization?: number;
    gate_count: number;
    depth: number;
    one_qubit_gates?: number;
    two_qubit_gates: number;
    two_qubit_ratio?: number;
    gate_density?: number;
    measurement_ratio?: number;
    cancellation_opportunities?: number;
    gate_counts?: Record<string, number>;
  };

  circuit?: {
    qubits?: number;
    operations?: Array<{
      gate?: string;
      qubits?: number[];
      params?: number[];
    }>;
    [key: string]: unknown;
  };

  health: {
    score: number;
    category: string;

    components?: {
      depth_efficiency?: number;
      gate_efficiency?: number;
      qubit_utilization?: number;
      two_qubit_efficiency?: number;
      noise_exposure?: number;
      optimization_potential?: number;
      [key: string]: number | undefined;
    };

    weights?: Record<string, number>;
  };

  model_health?: {
    category?: string;
    [key: string]: unknown;
  };

  anomaly?: {
    anomaly?: boolean;
    score?: number;
    [key: string]: unknown;
  };

  noise?: {
    noise_exposure_percent?: number;
    method?: string;
    note?: string;
    [key: string]: unknown;
  };

  hardware_recommendations?: HardwareRecommendations;

  recommendations?: {
    summary?: string;
    recommendations?: string[];
    provider?: string;
    [key: string]: unknown;
  };

  explanation?: string;

  database?: {
    saved?: boolean;
    id?: number;
    [key: string]: unknown;
  };

  [key: string]: unknown;
};
