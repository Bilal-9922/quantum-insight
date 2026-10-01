export type HardwareRecommendation = {
  type?: string;
  priority?: "low" | "moderate" | "high" | string;
  title?: string;
  message?: string;
  metric?: number;
};

export type HardwareRecommendations = {
  available?: boolean;

  execution_level?:
    | "favorable"
    | "moderate"
    | "challenging"
    | string;

  summary?: string;

  recommended_hardware?: {
    system?: string;
    reason?: string;
    minimum_qubits?: number;
    connectivity_requirement?: string;
    gate_fidelity_requirement?: string;
    noise_sensitivity?: string;
  };

  hardware_characteristics?: {
    minimum_qubits?: number;
    connectivity_importance?: string;
    gate_fidelity_importance?: string;
    noise_sensitivity?: string;
    recommended_hardware_system?: string;
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
    noise_exposure_percent?: number;
  };

  disclaimer?: string;
};


/* ============================================================
   QUANTUM MAINTAINABILITY INDEX
   ============================================================ */

export type QMI = {
  score: number;
  category: string;

  components: {
    readability: number;
    gate_efficiency: number;
    modularity: number;
    scalability: number;
    gate_diversity: number;
    complexity: number;
  };

  weights: {
    readability: number;
    gate_efficiency: number;
    modularity: number;
    scalability: number;
    gate_diversity: number;
    complexity: number;
  };

  basis?: {
    qubits?: number;
    gate_count?: number;
    depth?: number;
    one_qubit_gates?: number;
    two_qubit_gates?: number;
    two_qubit_ratio?: number;
    gate_density?: number;
    unique_gate_types?: number;
    cancellation_opportunities?: number;
  };
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

    components: Record<
      string,
      number
    >;

    weights?: Record<
      string,
      number
    >;
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

  /* ==========================================================
     QUANTUM MAINTAINABILITY INDEX
     ========================================================== */

  qmi?: QMI;

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
