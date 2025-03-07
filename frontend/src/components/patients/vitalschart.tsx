import React, { useMemo } from "react";
import { Box, Text } from "@chakra-ui/react";
import { Chart, registerables } from "chart.js";
import { Line } from "react-chartjs-2";
import { ClinicalData } from "@/types";

// Register Chart.js components
Chart.register(...registerables);

interface VitalsChartProps {
  clinicalData: ClinicalData[];
}

const VitalsChart: React.FC<VitalsChartProps> = ({ clinicalData }) => {
  // Process data for the chart
  const chartData = useMemo(() => {
    // Sort by timestamp (ascending)
    const sortedData = [...clinicalData].sort(
      (a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    // Extract timestamps and format them
    const labels = sortedData.map((data) =>
      new Date(data.timestamp).toLocaleString([], {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    );

    // Extract vitals
    const heartRate = sortedData.map((data) => data.heart_rate);
    const respiratoryRate = sortedData.map((data) => data.respiratory_rate);
    const temperature = sortedData.map((data) => data.temperature);
    const systolicBP = sortedData.map((data) => data.systolic_bp);
    const oxygenSaturation = sortedData.map((data) => data.oxygen_saturation);

    return {
      labels,
      datasets: [
        {
          label: "Heart Rate",
          data: heartRate,
          borderColor: "rgb(255, 99, 132)",
          backgroundColor: "rgba(255, 99, 132, 0.5)",
          yAxisID: "y",
        },
        {
          label: "Respiratory Rate",
          data: respiratoryRate,
          borderColor: "rgb(54, 162, 235)",
          backgroundColor: "rgba(54, 162, 235, 0.5)",
          yAxisID: "y",
        },
        {
          label: "Temperature",
          data: temperature,
          borderColor: "rgb(255, 159, 64)",
          backgroundColor: "rgba(255, 159, 64, 0.5)",
          yAxisID: "y1",
        },
        {
          label: "Systolic BP",
          data: systolicBP,
          borderColor: "rgb(75, 192, 192)",
          backgroundColor: "rgba(75, 192, 192, 0.5)",
          yAxisID: "y2",
        },
        {
          label: "Oxygen Saturation",
          data: oxygenSaturation,
          borderColor: "rgb(153, 102, 255)",
          backgroundColor: "rgba(153, 102, 255, 0.5)",
          yAxisID: "y3",
        },
      ],
    };
  }, [clinicalData]);

  const options = {
    responsive: true,
    interaction: {
      mode: "index" as const,
      intersect: false,
    },
    stacked: false,
    scales: {
      y: {
        type: "linear" as const,
        display: true,
        position: "left" as const,
        title: {
          display: true,
          text: "Heart Rate (bpm) / Respiratory Rate (brpm)",
        },
      },
      y1: {
        type: "linear" as const,
        display: true,
        position: "right" as const,
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: "Temperature (°C)",
        },
        min: 35,
        max: 40,
      },
      y2: {
        type: "linear" as const,
        display: false,
        position: "right" as const,
        grid: {
          drawOnChartArea: false,
        },
      },
      y3: {
        type: "linear" as const,
        display: true,
        position: "right" as const,
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: "O2 Saturation (%)",
        },
        min: 80,
        max: 100,
      },
    },
  };

  if (clinicalData.length === 0) {
    return (
      <Box
        height="100%"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text>No vital signs data available</Text>
      </Box>
    );
  }

  return <Line data={chartData} options={options} />;
};

export default VitalsChart;
