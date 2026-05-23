// ----------------- STATE STORE & CONFIGURATIONS -----------------
let currentMode = 'sim'; // 'sim', 'manual', 'stream'
let isPlaying = false;
let simTimer = null;
let currentFrameIndex = 0;
let historyBuffer = []; // Last 12 frames
const maxHistorySize = 12;

// Visual theme colors (F1 Hybrid Terminal Theme)
const COLORS = {
  crimson: '#E60000',
  amber: '#FF9900',
  green: '#00E676',
  blue: '#00B0FF',
  purple: '#AA00FF',
  slate: '#8E929E',
  border: '#2D2E30'
};

// ----------------- T20 CRICKET SIMULATION DATA TIMELINE -----------------
// Represents a dramatic final 2 overs of an IPL match driving spatial crowd mechanics.
const SIM_TIMELINE = [
  {
    marker: "Over 18.1",
    score_summary: "180/4 (18.1 Ov)",
    primary_actor: "Virat Kohli (74*)",
    secondary_actor: "Jasprit Bumrah (Bowler)",
    match_phase: "Steady Play",
    narrative: "Kohli takes a quick single. Crowd in South Seating roars. Concourse transit stable.",
    nodes: {
      "Gate A": { node_id: "Gate A", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.8, density_per_sqm: 1.1, turnstile_flow_rate: 35.0, cognitive_drift_index: 0.12 } },
      "Gate B": { node_id: "Gate B", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.9, density_per_sqm: 1.3, turnstile_flow_rate: 40.0, cognitive_drift_index: 0.15 } },
      "Main Concourse": { node_id: "Main Concourse", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 1.2, density_per_sqm: 1.8, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.18 } },
      "South Seating": { node_id: "South Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.4, density_per_sqm: 4.8, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.10 } },
      "North Seating": { node_id: "North Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.3, density_per_sqm: 4.5, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.11 } },
      "Food Court": { node_id: "Food Court", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.8, density_per_sqm: 2.2, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.20 } }
    }
  },
  {
    marker: "Over 18.2",
    score_summary: "184/4 (18.2 Ov)",
    primary_actor: "Hardik Pandya (12*)",
    secondary_actor: "Jasprit Bumrah (Bowler)",
    match_phase: "Steady Play",
    narrative: "Pandya hits a boundary! Wave of celebration sweeps South Seating. Food court starts to clear.",
    nodes: {
      "Gate A": { node_id: "Gate A", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.7, density_per_sqm: 1.0, turnstile_flow_rate: 30.0, cognitive_drift_index: 0.11 } },
      "Gate B": { node_id: "Gate B", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.8, density_per_sqm: 1.2, turnstile_flow_rate: 38.0, cognitive_drift_index: 0.14 } },
      "Main Concourse": { node_id: "Main Concourse", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 1.1, density_per_sqm: 1.9, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.17 } },
      "South Seating": { node_id: "South Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.3, density_per_sqm: 5.1, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.09 } },
      "North Seating": { node_id: "North Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.3, density_per_sqm: 4.6, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.10 } },
      "Food Court": { node_id: "Food Court", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.9, density_per_sqm: 1.9, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.22 } }
    }
  },
  {
    marker: "Over 18.3",
    score_summary: "184/5 (18.3 Ov)",
    primary_actor: "Hardik Pandya (Wicket!)",
    secondary_actor: "Jasprit Bumrah (Bowler)",
    match_phase: "Steady Play",
    narrative: "WICKET! Clean bowled! Shocked silence. Sudden mass seating shifts. Concourse density rises.",
    nodes: {
      "Gate A": { node_id: "Gate A", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.9, density_per_sqm: 1.2, turnstile_flow_rate: 45.0, cognitive_drift_index: 0.15 } },
      "Gate B": { node_id: "Gate B", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.8, density_per_sqm: 1.4, turnstile_flow_rate: 42.0, cognitive_drift_index: 0.18 } },
      "Main Concourse": { node_id: "Main Concourse", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 1.4, density_per_sqm: 2.5, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.25 } },
      "South Seating": { node_id: "South Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.5, density_per_sqm: 4.8, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.15 } },
      "North Seating": { node_id: "North Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.4, density_per_sqm: 4.4, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.14 } },
      "Food Court": { node_id: "Food Court", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.7, density_per_sqm: 2.1, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.28 } }
    }
  },
  {
    marker: "Over 18.4",
    score_summary: "185/5 (18.4 Ov)",
    primary_actor: "Rinku Singh (1*)",
    secondary_actor: "Jasprit Bumrah (Bowler)",
    match_phase: "Steady Play",
    narrative: "Rinku defends, takes a single. High nervous tension. Gate A entry ticket queues building up.",
    nodes: {
      "Gate A": { node_id: "Gate A", status: "WARNING", domain_numeric_values: { crowd_velocity_mps: 0.5, density_per_sqm: 2.8, turnstile_flow_rate: 95.0, cognitive_drift_index: 0.20 } },
      "Gate B": { node_id: "Gate B", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.8, density_per_sqm: 1.5, turnstile_flow_rate: 50.0, cognitive_drift_index: 0.15 } },
      "Main Concourse": { node_id: "Main Concourse", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 1.2, density_per_sqm: 2.7, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.22 } },
      "South Seating": { node_id: "South Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.3, density_per_sqm: 4.9, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.12 } },
      "North Seating": { node_id: "North Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.3, density_per_sqm: 4.5, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.11 } },
      "Food Court": { node_id: "Food Court", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.6, density_per_sqm: 2.0, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.24 } }
    }
  },
  {
    marker: "Over 18.5",
    score_summary: "189/5 (18.5 Ov)",
    primary_actor: "Virat Kohli (78*)",
    secondary_actor: "Jasprit Bumrah (Bowler)",
    match_phase: "Steady Play",
    narrative: "Kohli pulls! Boundary! Seating is packed. Turnstiles at Gate A are congested with late arrivals.",
    nodes: {
      "Gate A": { node_id: "Gate A", status: "WARNING", domain_numeric_values: { crowd_velocity_mps: 0.4, density_per_sqm: 3.5, turnstile_flow_rate: 110.0, cognitive_drift_index: 0.28 } },
      "Gate B": { node_id: "Gate B", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.7, density_per_sqm: 1.6, turnstile_flow_rate: 45.0, cognitive_drift_index: 0.16 } },
      "Main Concourse": { node_id: "Main Concourse", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 1.1, density_per_sqm: 2.9, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.21 } },
      "South Seating": { node_id: "South Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.2, density_per_sqm: 5.3, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.08 } },
      "North Seating": { node_id: "North Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.3, density_per_sqm: 4.6, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.09 } },
      "Food Court": { node_id: "Food Court", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.6, density_per_sqm: 1.8, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.22 } }
    }
  },
  {
    marker: "Over 18.6",
    score_summary: "195/5 (18.6 Ov)",
    primary_actor: "Virat Kohli (84*)",
    secondary_actor: "Jasprit Bumrah (Bowler)",
    match_phase: "Steady Play",
    narrative: "SIX! Kohli launches it! Pure pandemonium in Seating. Sudden rush inside Main Concourse.",
    nodes: {
      "Gate A": { node_id: "Gate A", status: "WARNING", domain_numeric_values: { crowd_velocity_mps: 0.3, density_per_sqm: 3.8, turnstile_flow_rate: 135.0, cognitive_drift_index: 0.34 } },
      "Gate B": { node_id: "Gate B", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.6, density_per_sqm: 1.7, turnstile_flow_rate: 55.0, cognitive_drift_index: 0.19 } },
      "Main Concourse": { node_id: "Main Concourse", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 1.3, density_per_sqm: 3.2, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.27 } },
      "South Seating": { node_id: "South Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.4, density_per_sqm: 5.6, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.12 } },
      "North Seating": { node_id: "North Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.3, density_per_sqm: 4.8, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.13 } },
      "Food Court": { node_id: "Food Court", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.7, density_per_sqm: 1.7, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.23 } }
    }
  },
  {
    marker: "Over 19.1",
    score_summary: "195/6 (19.1 Ov)",
    primary_actor: "Virat Kohli (Wicket!)",
    secondary_actor: "Mohit Sharma (Bowler)",
    match_phase: "Innings Break",
    narrative: "OUT! Kohli caught on boundary! Innings Break engaged. Concourse transit density warning.",
    nodes: {
      "Gate A": { node_id: "Gate A", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 0.1, density_per_sqm: 5.2, turnstile_flow_rate: 165.0, cognitive_drift_index: 0.62 } },
      "Gate B": { node_id: "Gate B", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.5, density_per_sqm: 1.9, turnstile_flow_rate: 65.0, cognitive_drift_index: 0.22 } },
      "Main Concourse": { node_id: "Main Concourse", status: "WARNING", domain_numeric_values: { crowd_velocity_mps: 0.9, density_per_sqm: 4.1, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.45 } },
      "South Seating": { node_id: "South Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.6, density_per_sqm: 5.1, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.28 } },
      "North Seating": { node_id: "North Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.4, density_per_sqm: 4.9, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.21 } },
      "Food Court": { node_id: "Food Court", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.8, density_per_sqm: 4.5, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.30 } }
    }
  },
  {
    marker: "Over 19.2",
    score_summary: "196/6 (19.2 Ov)",
    primary_actor: "MS Dhoni (1*)",
    secondary_actor: "Mohit Sharma (Bowler)",
    match_phase: "Innings Break",
    narrative: "Dhoni enters! Crowd noise breaking records. Gate A pathways crossing critical thresholds.",
    nodes: {
      "Gate A": { node_id: "Gate A", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 0.05, density_per_sqm: 7.2, turnstile_flow_rate: 180.0, cognitive_drift_index: 0.78 } },
      "Gate B": { node_id: "Gate B", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.6, density_per_sqm: 2.1, turnstile_flow_rate: 70.0, cognitive_drift_index: 0.25 } },
      "Main Concourse": { node_id: "Main Concourse", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 0.4, density_per_sqm: 5.4, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.58 } },
      "South Seating": { node_id: "South Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.2, density_per_sqm: 5.8, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.24 } },
      "North Seating": { node_id: "North Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.3, density_per_sqm: 5.1, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.22 } },
      "Food Court": { node_id: "Food Court", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.7, density_per_sqm: 5.1, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.35 } }
    }
  },
  {
    marker: "Over 19.3",
    score_summary: "202/6 (19.3 Ov)",
    primary_actor: "MS Dhoni (7*)",
    secondary_actor: "Mohit Sharma (Bowler)",
    match_phase: "Play Halted",
    narrative: "RAIN DELAY! Play Halted temporarily. Sign overrides triggered to open bypass exits.",
    nodes: {
      "Gate A": { node_id: "Gate A", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 0.02, density_per_sqm: 8.8, turnstile_flow_rate: 195.0, cognitive_drift_index: 0.89 } },
      "Gate B": { node_id: "Gate B", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.4, density_per_sqm: 2.5, turnstile_flow_rate: 80.0, cognitive_drift_index: 0.30 } },
      "Main Concourse": { node_id: "Main Concourse", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 0.25, density_per_sqm: 6.2, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.69 } },
      "South Seating": { node_id: "South Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.15, density_per_sqm: 6.0, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.18 } },
      "North Seating": { node_id: "North Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.25, density_per_sqm: 5.3, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.16 } },
      "Food Court": { node_id: "Food Court", status: "WARNING", domain_numeric_values: { crowd_velocity_mps: 0.5, density_per_sqm: 3.4, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.42 } }
    }
  },
  {
    marker: "Over 19.4",
    score_summary: "206/6 (19.4 Ov)",
    primary_actor: "MS Dhoni (11*)",
    secondary_actor: "Mohit Sharma (Bowler)",
    match_phase: "Steady Play",
    narrative: "Play resumed! Dhoni cuts it past third man. Seating exits controlled to prevent spillovers.",
    nodes: {
      "Gate A": { node_id: "Gate A", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 0.1, density_per_sqm: 9.2, turnstile_flow_rate: 190.0, cognitive_drift_index: 0.92 } },
      "Gate B": { node_id: "Gate B", status: "WARNING", domain_numeric_values: { crowd_velocity_mps: 0.3, density_per_sqm: 3.2, turnstile_flow_rate: 120.0, cognitive_drift_index: 0.45 } },
      "Main Concourse": { node_id: "Main Concourse", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 0.2, density_per_sqm: 6.9, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.74 } },
      "South Seating": { node_id: "South Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.1, density_per_sqm: 6.1, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.19 } },
      "North Seating": { node_id: "North Seating", status: "NORMAL", domain_numeric_values: { crowd_velocity_mps: 0.2, density_per_sqm: 5.4, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.17 } },
      "Food Court": { node_id: "Food Court", status: "WARNING", domain_numeric_values: { crowd_velocity_mps: 0.4, density_per_sqm: 3.9, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.48 } }
    }
  },
  {
    marker: "Over 19.5",
    score_summary: "206/7 (19.5 Ov)",
    primary_actor: "MS Dhoni (Wicket!)",
    secondary_actor: "Mohit Sharma (Bowler)",
    match_phase: "Steady Play",
    narrative: "OUT! Dhoni caught! Spectator rush to exits starts early. Main concourse velocity spiking.",
    nodes: {
      "Gate A": { node_id: "Gate A", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 0.2, density_per_sqm: 8.5, turnstile_flow_rate: 150.0, cognitive_drift_index: 0.88 } },
      "Gate B": { node_id: "Gate B", status: "WARNING", domain_numeric_values: { crowd_velocity_mps: 0.5, density_per_sqm: 3.8, turnstile_flow_rate: 140.0, cognitive_drift_index: 0.52 } },
      "Main Concourse": { node_id: "Main Concourse", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 1.8, density_per_sqm: 7.4, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.82 } },
      "South Seating": { node_id: "South Seating", status: "WARNING", domain_numeric_values: { crowd_velocity_mps: 1.1, density_per_sqm: 5.8, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.35 } },
      "North Seating": { node_id: "North Seating", status: "WARNING", domain_numeric_values: { crowd_velocity_mps: 0.9, density_per_sqm: 5.2, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.31 } },
      "Food Court": { node_id: "Food Court", status: "WARNING", domain_numeric_values: { crowd_velocity_mps: 0.6, density_per_sqm: 4.1, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.51 } }
    }
  },
  {
    marker: "Over 20.0",
    score_summary: "212/7 (20.0 Ov)",
    primary_actor: "Rinku Singh (7*)",
    secondary_actor: "Mohit Sharma (Bowler)",
    match_phase: "Post Match Egress",
    narrative: "MATCH COMPLETE! Rinku six to finish. Massive egress waves flushing into exit walkways.",
    nodes: {
      "Gate A": { node_id: "Gate A", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 5.2, density_per_sqm: 4.5, turnstile_flow_rate: 180.0, cognitive_drift_index: 0.95 } },
      "Gate B": { node_id: "Gate B", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 4.8, density_per_sqm: 4.2, turnstile_flow_rate: 175.0, cognitive_drift_index: 0.91 } },
      "Main Concourse": { node_id: "Main Concourse", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 3.5, density_per_sqm: 5.8, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.88 } },
      "South Seating": { node_id: "South Seating", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 2.8, density_per_sqm: 4.2, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.65 } },
      "North Seating": { node_id: "North Seating", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 2.5, density_per_sqm: 4.1, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.62 } },
      "Food Court": { node_id: "Food Court", status: "CRITICAL", domain_numeric_values: { crowd_velocity_mps: 2.1, density_per_sqm: 4.0, turnstile_flow_rate: 0.0, cognitive_drift_index: 0.70 } }
    }
  }
];

// ----------------- CHART.JS INITIALIZATION -----------------
const charts = {};

function initCharts() {
  const chartConfigs = {
    'chart-velocity': {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          { label: 'Gate A', borderColor: COLORS.crimson, backgroundColor: 'rgba(230,0,0,0.05)', data: [], fill: true, tension: 0.3 },
          { label: 'Gate B', borderColor: COLORS.amber, backgroundColor: 'rgba(255,153,0,0.05)', data: [], fill: true, tension: 0.3 },
          { label: 'Main Concourse', borderColor: COLORS.green, backgroundColor: 'rgba(0,230,118,0.05)', data: [], fill: true, tension: 0.3 }
        ]
      },
      options: getChartOptions('Velocity (mps)')
    },
    'chart-density': {
      type: 'bar',
      data: {
        labels: [],
        datasets: [
          { label: 'Concourse', backgroundColor: COLORS.crimson, data: [] },
          { label: 'Food Court', backgroundColor: COLORS.amber, data: [] },
          { label: 'South Seating', backgroundColor: COLORS.blue, data: [] },
          { label: 'North Seating', backgroundColor: COLORS.purple, data: [] }
        ]
      },
      options: getChartOptions('Spectators / sqm')
    },
    'chart-flow': {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          { label: 'Gate A turnstile', borderColor: COLORS.crimson, data: [], tension: 0.2, fill: false },
          { label: 'Gate B turnstile', borderColor: COLORS.amber, data: [], tension: 0.2, fill: false }
        ]
      },
      options: getChartOptions('Flow Rate (Spectators/min)')
    },
    'chart-drift': {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          { label: 'Venue-Wide Cognitive Drift Index', borderColor: COLORS.crimson, backgroundColor: 'rgba(230,0,0,0.1)', data: [], fill: true, tension: 0.4 }
        ]
      },
      options: getChartOptions('Drift Coeff (0.0 to 1.0)')
    }
  };

  for (const [id, config] of Object.entries(chartConfigs)) {
    const ctx = document.getElementById(id).getContext('2d');
    charts[id] = new Chart(ctx, config);
  }
}

function getChartOptions(yAxisLabel) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: COLORS.slate, font: { family: 'Inter', weight: 'bold', size: 10 } }
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255,255,255,0.03)' },
        ticks: { color: COLORS.slate, font: { family: 'JetBrains Mono', size: 9 } }
      },
      y: {
        grid: { color: 'rgba(255,255,255,0.03)' },
        ticks: { color: COLORS.slate, font: { family: 'JetBrains Mono', size: 9 } },
        title: { display: true, text: yAxisLabel, color: COLORS.slate, font: { family: 'Inter', weight: 'bold', size: 10 } }
      }
    }
  };
}

// ----------------- DATA DISPATCH & API CONSUMPTION -----------------
async function dispatchFrame(frame) {
  try {
    const response = await fetch('/api/match_cast', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(frame)
    });
    
    if (!response.ok) {
      throw new Error(`API Gateway error: ${response.statusText}`);
    }
    
    const aggregated = await response.json();
    renderStateUpdate(aggregated);
  } catch (error) {
    console.error("Frame dispatch failed:", error);
    logNarrative("SYSTEM", `Network connection friction. Retrying asynchronous gateway pipeline...`);
  }
}

// ----------------- RENDER ENGINE & UI SYNCHRONIZATION -----------------
function renderStateUpdate(data) {
  if (!data || !data.frame) return;

  const frame = data.frame;
  const assessments = data.assessments || {};
  const forecasts = data.forecasts || {};
  const signage = data.signage_states || {};
  const stats = data.stats || {};

  // 1. Top Score Strips
  document.getElementById('top-event-id').innerText = frame.event_id || 'IPL-2026-FINAL';
  document.getElementById('top-score').innerText = frame.score_summary || '';
  document.getElementById('top-actors').innerText = `${frame.primary_actor} | ${frame.secondary_actor}`;
  document.getElementById('top-marker').innerText = `${frame.marker} [${frame.match_phase}]`;

  // 2. Safety badge
  const safetyBadge = document.getElementById('top-safety-badge');
  const safetyStatus = stats.safety_zone || 'GREEN';
  safetyBadge.className = `safety-badge ${safetyStatus.toLowerCase()}`;
  safetyBadge.innerHTML = `<span class="indicator-dot active"></span> ${safetyStatus} dynamics`;

  // 3. Composure Index
  const composureVal = stats.global_crowd_anomaly_index !== undefined ? 1.0 - stats.global_crowd_anomaly_index : 0.85;
  document.getElementById('card-composure-val').innerHTML = `${composureVal.toFixed(2)}<span style="font-size: 1rem; color: var(--text-muted);">/1.0</span>`;
  const barComposure = document.getElementById('bar-composure');
  barComposure.style.width = `${composureVal * 100}%`;
  
  if (composureVal > 0.7) {
    barComposure.className = 'stat-fill green';
  } else if (composureVal > 0.4) {
    barComposure.className = 'stat-fill amber';
  } else {
    barComposure.className = 'stat-fill crimson';
  }

  // 4. GNN spillover metric card
  let totalSpillover = 0;
  let count = 0;
  for (const node of Object.values(forecasts)) {
    totalSpillover += node.spillover_probability;
    count++;
  }
  const avgSpillover = count > 0 ? (totalSpillover / count) * 100 : 8.5;
  const spilloverEl = document.getElementById('card-spillover-val');
  spilloverEl.innerText = `${avgSpillover.toFixed(1)}%`;
  
  const barSpill = document.getElementById('bar-spillover');
  barSpill.style.width = `${avgSpillover}%`;
  if (avgSpillover < 30) {
    spilloverEl.style.color = COLORS.green;
    barSpill.className = 'stat-fill green';
  } else if (avgSpillover < 60) {
    spilloverEl.style.color = COLORS.amber;
    barSpill.className = 'stat-fill amber';
  } else {
    spilloverEl.style.color = COLORS.crimson;
    barSpill.className = 'stat-fill crimson';
  }

  // 5. MARL policies signage card
  const signageListContainer = document.getElementById('marl-signage-list');
  signageListContainer.innerHTML = '';
  
  const policyStatusBadge = document.getElementById('marl-policy-status');
  if (data.overrides_triggered && data.overrides_triggered.length > 0) {
    policyStatusBadge.innerText = `${data.overrides_triggered.length} SIGN OVERRIDES`;
    policyStatusBadge.className = 'safety-badge critical';
  } else {
    policyStatusBadge.innerText = 'POLICIES NORMAL';
    policyStatusBadge.className = 'safety-badge green';
  }

  for (const [node, text] of Object.entries(signage)) {
    const isOverride = text.includes('EMERGENCY') || text.includes('WARNING') || text.includes('CRUSH') || text.includes('ROLLBACK');
    const color = isOverride ? COLORS.crimson : (text.includes('DELAY') ? COLORS.amber : COLORS.green);
    
    signageListContainer.innerHTML += `
      <div class="signage-item">
        <span class="signage-node">${node}:</span>
        <span class="signage-msg" style="color: ${color};">${text}</span>
      </div>
    `;
  }

  // 6. Mesh stats latency
  document.getElementById('mesh-latency').innerText = `${(stats.processing_latency_ms || 18.2).toFixed(1)} ms`;

  // Circuit Breaker visual indicator
  const gnnCbStatus = document.getElementById('cb-status-gnn');
  if (data.circuits && data.circuits.gnn && gnnCbStatus) {
    const state = data.circuits.gnn;
    gnnCbStatus.innerText = state;
    if (state === 'CLOSED') {
      gnnCbStatus.style.color = COLORS.green;
    } else if (state === 'OPEN') {
      gnnCbStatus.style.color = COLORS.crimson;
    } else {
      gnnCbStatus.style.color = COLORS.amber;
    }
  }

  // 7. Add logs to narrative feed
  if (frame.narrative) {
    logNarrative(frame.marker, frame.narrative);
  }

  if (data.anomalies_detected && data.anomalies_detected.length > 0) {
    for (const anom of data.anomalies_detected) {
      logNarrative(frame.marker, anom.log, true);
    }
  }

  // 8. Optimistic HITL Rollback Banner coordination
  const hitlBanner = document.getElementById('hitl-banner');
  const hitlBannerText = document.getElementById('hitl-banner-text');
  const hitlDenyBtn = document.getElementById('hitl-deny-btn');

  if (data.hitl_override_pending && data.hitl_timer > 0) {
    hitlBanner.style.display = 'flex';
    hitlBannerText.innerText = `Autonomous safety overrides deployed bypass paths. ${data.hitl_timer}s remaining to decline.`;
    hitlDenyBtn.innerText = `DENY / ROLLBACK (${data.hitl_timer}s)`;
  } else {
    hitlBanner.style.display = 'none';
  }

  // 9. Update history buffers
  historyBuffer.push({ frame, assessments, forecasts, stats });
  if (historyBuffer.length > maxHistorySize) {
    historyBuffer.shift();
  }

  updateChartsData();
}

function logNarrative(timestamp, msg, isAnomaly = false) {
  const container = document.getElementById('narrative-log-container');
  const entry = document.createElement('div');
  entry.className = 'narrative-entry';
  
  const timeSpan = document.createElement('span');
  timeSpan.className = 'entry-time';
  timeSpan.innerText = `[${timestamp}]`;
  
  const txtSpan = document.createElement('span');
  txtSpan.className = isAnomaly ? 'entry-anomaly' : 'entry-txt';
  txtSpan.innerText = msg;
  
  entry.appendChild(timeSpan);
  entry.appendChild(txtSpan);
  container.appendChild(entry);
  container.scrollTop = container.scrollHeight;
}

// ----------------- OPTIMISTIC HITL OVERRIDE ACTION -----------------
async function triggerHitlDeny() {
  try {
    const response = await fetch('/api/hitl/deny', { method: 'POST' });
    if (response.ok) {
      const res = await response.json();
      logNarrative("HITL OVERRIDE", "Operator forcefully issued DENY command! Saga compensating rollbacks completed.", true);
      document.getElementById('hitl-banner').style.display = 'none';
      
      // Request latest decoupled query state immediately
      const refreshResponse = await fetch('/api/latest');
      if (refreshResponse.ok) {
        const refreshData = await refreshResponse.json();
        renderStateUpdate(refreshData);
      }
    }
  } catch (error) {
    console.error("HITL Deny execution failure:", error);
  }
}

// ----------------- CHART POPULATION -----------------
function updateChartsData() {
  const labels = historyBuffer.map(h => h.frame.marker);

  // 1. Velocity Line Chart
  charts['chart-velocity'].data.labels = labels;
  charts['chart-velocity'].data.datasets[0].data = historyBuffer.map(h => h.frame.nodes["Gate A"].domain_numeric_values.crowd_velocity_mps);
  charts['chart-velocity'].data.datasets[1].data = historyBuffer.map(h => h.frame.nodes["Gate B"].domain_numeric_values.crowd_velocity_mps);
  charts['chart-velocity'].data.datasets[2].data = historyBuffer.map(h => h.frame.nodes["Main Concourse"].domain_numeric_values.crowd_velocity_mps);
  charts['chart-velocity'].update('none');

  // 2. Density Bar Chart
  charts['chart-density'].data.labels = labels;
  charts['chart-density'].data.datasets[0].data = historyBuffer.map(h => h.frame.nodes["Main Concourse"].domain_numeric_values.density_per_sqm);
  charts['chart-density'].data.datasets[1].data = historyBuffer.map(h => h.frame.nodes["Food Court"].domain_numeric_values.density_per_sqm);
  charts['chart-density'].data.datasets[2].data = historyBuffer.map(h => h.frame.nodes["South Seating"].domain_numeric_values.density_per_sqm);
  charts['chart-density'].data.datasets[3].data = historyBuffer.map(h => h.frame.nodes["North Seating"].domain_numeric_values.density_per_sqm);
  charts['chart-density'].update('none');

  // 3. Turnstile Flow Rate
  charts['chart-flow'].data.labels = labels;
  charts['chart-flow'].data.datasets[0].data = historyBuffer.map(h => h.frame.nodes["Gate A"].domain_numeric_values.turnstile_flow_rate);
  charts['chart-flow'].data.datasets[1].data = historyBuffer.map(h => h.frame.nodes["Gate B"].domain_numeric_values.turnstile_flow_rate);
  charts['chart-flow'].update('none');

  // 4. Cognitive Drift Line Chart
  charts['chart-drift'].data.labels = labels;
  charts['chart-drift'].data.datasets[0].data = historyBuffer.map(h => {
    const nodes = h.frame.nodes;
    let sum = 0, cnt = 0;
    for (const node of Object.values(nodes)) {
      sum += node.domain_numeric_values.cognitive_drift_index;
      cnt++;
    }
    return sum / cnt;
  });
  charts['chart-drift'].update('none');
}

// ----------------- INTERACTIVE CONTROL LOGIC -----------------
function setMode(mode) {
  currentMode = mode;
  document.getElementById('btn-mode-sim').classList.toggle('active', mode === 'sim');
  document.getElementById('btn-mode-manual').classList.toggle('active', mode === 'manual');
  document.getElementById('btn-mode-stream').classList.toggle('active', mode === 'stream');

  const simControls = document.getElementById('sim-controls-wrapper');
  const streamStatus = document.getElementById('stream-status-wrapper');
  const manualControls = document.getElementById('manual-controls-section');

  simControls.style.display = mode === 'sim' ? 'block' : 'none';
  streamStatus.style.display = mode === 'stream' ? 'block' : 'none';
  
  if (mode === 'manual') {
    manualControls.style.opacity = '1';
    manualControls.style.pointerEvents = 'auto';
    stopSim();
  } else {
    manualControls.style.opacity = '0.5';
    manualControls.style.pointerEvents = 'none';
  }

  if (mode === 'stream') {
    stopSim();
    startLongPollingStream();
  } else {
    stopLongPollingStream();
  }
}

// 1. Simulation controls
function toggleSim() {
  if (isPlaying) {
    stopSim();
  } else {
    isPlaying = true;
    document.getElementById('sim-play-btn').innerText = 'Pause';
    document.getElementById('sim-play-btn').style.backgroundColor = COLORS.crimson;
    simTimer = setInterval(stepSim, 3000);
  }
}

function stopSim() {
  isPlaying = false;
  document.getElementById('sim-play-btn').innerText = 'Play';
  document.getElementById('sim-play-btn').style.backgroundColor = '#1b1c1e';
  if (simTimer) {
    clearInterval(simTimer);
    simTimer = null;
  }
}

function stepSim() {
  if (currentFrameIndex >= SIM_TIMELINE.length) {
    currentFrameIndex = 0; // Loop simulation
  }
  const currentFrame = SIM_TIMELINE[currentFrameIndex];
  
  // Pack 24-dimensional feature vector dynamically for GNN/semantic bypass checks
  const feature_vector = [];
  const node_order = ["Gate A", "Gate B", "Main Concourse", "South Seating", "North Seating", "Food Court"];
  node_order.forEach(name => {
    const node_data = currentFrame.nodes[name].domain_numeric_values;
    feature_vector.push(
      node_data.crowd_velocity_mps,
      node_data.density_per_sqm,
      node_data.turnstile_flow_rate,
      node_data.cognitive_drift_index
    );
  });

  const payload = {
    match_id: "IPL_2026_M56",
    event_id: "IPL_VENUE_OS_M56",
    marker: currentFrame.marker,
    score_summary: currentFrame.score_summary,
    primary_actor: currentFrame.primary_actor,
    secondary_actor: currentFrame.secondary_actor,
    match_phase: currentFrame.match_phase || "Steady Play",
    plate_redacted: true,
    faces_redacted: true,
    feature_vector: feature_vector,
    nodes: currentFrame.nodes
  };

  dispatchFrame(payload);
  currentFrameIndex++;
}

// 2. Manual overrides controls
function updateOverrideLabel(metric, val) {
  const labels = {
    concourse: `${val}/m²`,
    gateflow: `${val}/min`,
    velocity: `${val} m/s`,
    drift: val
  };
  document.getElementById(`lbl-${metric}`).innerText = labels[metric];
}

function applyManualOverride() {
  if (currentMode !== 'manual') return;

  const concourseDensity = parseFloat(document.getElementById('override-concourse').value);
  const gateFlowRate = parseFloat(document.getElementById('override-gateflow').value);
  const crowdVelocity = parseFloat(document.getElementById('override-velocity').value);
  const behaviorDrift = parseFloat(document.getElementById('override-drift').value);

  // Re-generate nodes dictionary
  const nodes = {
    "Gate A": {
      node_id: "Gate A",
      status: gateFlowRate > 120 ? "CRITICAL" : "NORMAL",
      domain_numeric_values: { crowd_velocity_mps: crowdVelocity, density_per_sqm: concourseDensity * 0.8, turnstile_flow_rate: gateFlowRate, cognitive_drift_index: behaviorDrift }
    },
    "Gate B": {
      node_id: "Gate B",
      status: "NORMAL",
      domain_numeric_values: { crowd_velocity_mps: crowdVelocity * 1.1, density_per_sqm: concourseDensity * 0.7, turnstile_flow_rate: gateFlowRate * 0.9, cognitive_drift_index: behaviorDrift }
    },
    "Main Concourse": {
      node_id: "Main Concourse",
      status: concourseDensity > 4.5 ? "CRITICAL" : "NORMAL",
      domain_numeric_values: { crowd_velocity_mps: crowdVelocity * 0.9, density_per_sqm: concourseDensity, turnstile_flow_rate: 0.0, cognitive_drift_index: behaviorDrift }
    },
    "South Seating": {
      node_id: "South Seating",
      status: "NORMAL",
      domain_numeric_values: { crowd_velocity_mps: crowdVelocity * 0.3, density_per_sqm: concourseDensity * 1.5, turnstile_flow_rate: 0.0, cognitive_drift_index: behaviorDrift }
    },
    "North Seating": {
      node_id: "North Seating",
      status: "NORMAL",
      domain_numeric_values: { crowd_velocity_mps: crowdVelocity * 0.3, density_per_sqm: concourseDensity * 1.4, turnstile_flow_rate: 0.0, cognitive_drift_index: behaviorDrift }
    },
    "Food Court": {
      node_id: "Food Court",
      status: "NORMAL",
      domain_numeric_values: { crowd_velocity_mps: crowdVelocity * 0.6, density_per_sqm: concourseDensity * 0.9, turnstile_flow_rate: 0.0, cognitive_drift_index: behaviorDrift }
    }
  };

  // Build feature vector
  const feature_vector = [];
  const node_order = ["Gate A", "Gate B", "Main Concourse", "South Seating", "North Seating", "Food Court"];
  node_order.forEach(name => {
    const node_data = nodes[name].domain_numeric_values;
    feature_vector.push(
      node_data.crowd_velocity_mps,
      node_data.density_per_sqm,
      node_data.turnstile_flow_rate,
      node_data.cognitive_drift_index
    );
  });

  const overrideFrame = {
    match_id: "IPL_MANUAL_OVERRIDE",
    event_id: "VENUE_MANUAL_CONTROL",
    marker: `Over Override-${Date.now().toString().slice(-4)}`,
    score_summary: "MANUAL VECTORING ACTIVE",
    primary_actor: "OPERATOR_COMMAND",
    secondary_actor: "MANUAL_BYPASS",
    match_phase: "Steady Play",
    plate_redacted: true,
    faces_redacted: true,
    feature_vector: feature_vector,
    nodes: nodes
  };

  logNarrative("OPERATOR", `Force Manual Vector: Concourse Density=${concourseDensity}/sqm, Gate Flow=${gateFlowRate}/min, Velocity=${crowdVelocity}m/s`);
  dispatchFrame(overrideFrame);
}

// 3. Webhook live stream long polling
let pollingInterval = null;

function startLongPollingStream() {
  const dot = document.getElementById('stream-dot');
  const txt = document.getElementById('stream-status-text');
  dot.classList.add('active');
  txt.innerText = 'ONLINE (LISTENING)';
  txt.style.color = COLORS.green;

  pollingInterval = setInterval(async () => {
    try {
      const response = await fetch('/api/latest');
      if (response.ok) {
        const data = await response.json();
        if (data.initialized) {
          renderStateUpdate(data);
        }
      }
    } catch (e) {
      console.error("Stream polling failed:", e);
    }
  }, 2000);
}

function stopLongPollingStream() {
  const dot = document.getElementById('stream-dot');
  const txt = document.getElementById('stream-status-text');
  dot.classList.remove('active');
  txt.innerText = 'OFFLINE';
  txt.style.color = COLORS.slate;

  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
  }
}

// 4. Tab Coordinator
function switchTab(tabId) {
  const tabs = document.querySelectorAll('.nav-tab');
  tabs.forEach(tab => {
    tab.classList.toggle('active', tab.innerText.toLowerCase().includes(tabId));
  });

  const panels = document.querySelectorAll('.tab-content');
  panels.forEach(p => {
    p.classList.remove('active');
  });

  if (tabId === 'overview') {
    document.getElementById('tab-overview').classList.add('active');
  } else {
    document.getElementById(`tab-${tabId}`).classList.add('active');
    if (charts[`chart-${tabId}`]) {
      charts[`chart-${tabId}`].resize();
    }
  }
}

// ----------------- DIAGNOSTIC GNN CIRCUIT BREAK FAILOVER SIMULATOR -----------------
async function toggleGnnFailureSimulation() {
  try {
    const response = await fetch('/api/simulate_failure/gnn', { method: 'POST' });
    if (response.ok) {
      const res = await response.json();
      const btn = document.getElementById('btn-simulate-fail');
      if (res.simulate_gnn_failure) {
        btn.style.backgroundColor = COLORS.crimson;
        btn.style.color = '#fff';
        btn.innerText = 'GNN DROPPED (PROBING)';
        logNarrative("DIAGNOSTIC", "Simulating GNN microservice connection dropout. Circuit Breaker collecting fault vectors...", true);
      } else {
        btn.style.backgroundColor = '#1a1515';
        btn.style.color = COLORS.crimson;
        btn.innerText = 'Simulate GNN Drop';
        logNarrative("DIAGNOSTIC", "GNN microservice connection restored. Probing recovery.");
      }
    }
  } catch (error) {
    console.error("Failure toggle failed:", error);
  }
}

// ----------------- INITIAL BOOTSTRAPPER -----------------
window.addEventListener('DOMContentLoaded', () => {
  initCharts();
  stepSim();
});
