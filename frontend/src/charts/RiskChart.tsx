import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer,
} from "recharts";

interface RiskChartProps {
  breachCount: number;
  profileCount: number;
  hasGravatar: boolean;
  riskScore: number;
}

const getRiskColor = (score: number): string => {
  if (score > 60) return "#ef4444";
  if (score > 30) return "#f59e0b";
  return "#22c55e";
};

const getRiskLabel = (score: number): string => {
  if (score > 70) return "Critical";
  if (score > 50) return "High";
  if (score > 30) return "Moderate";
  return "Low";
};

export default function RiskChart({ breachCount, profileCount, hasGravatar, riskScore }: RiskChartProps) {
  const data = [
    { metric: "Breaches", value: Math.min(breachCount * 20, 100) },
    { metric: "Social", value: Math.min(profileCount * 10, 100) },
    { metric: "Gravatar", value: hasGravatar ? 80 : 0 },
    { metric: "Overall", value: riskScore },
    { metric: "Web", value: Math.min(riskScore * 0.8, 80) },
  ];

  const color = getRiskColor(riskScore);

  return (
    <div className="card-glass" id="risk-chart">
      <h3 className="text-lg font-semibold mb-3">Risk Radar</h3>
      <ResponsiveContainer width="100%" height={250}>
        <RadarChart data={data}>
          <PolarGrid stroke="hsl(var(--muted-foreground))" opacity={0.15} />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
          />
          <Radar name="Risk" dataKey="value" stroke={color} fill={color} fillOpacity={0.15} />
        </RadarChart>
      </ResponsiveContainer>
      <div className="text-center mt-3">
        <span className="text-3xl font-bold" style={{ color }}>
          {riskScore.toFixed(0)}%
        </span>
        <div className="text-sm font-medium mt-1" style={{ color }}>
          {getRiskLabel(riskScore)} Risk
        </div>
      </div>
    </div>
  );
}
