import React, { useState } from "react";
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Text,
  Select,
  HStack,
  Input,
  Button,
} from "@chakra-ui/react";
import { SearchIcon } from "@chakra-ui/icons";
import { ClinicalData } from "@/types";

interface ClinicalDataTableProps {
  clinicalData: ClinicalData[];
}

const ClinicalDataTable: React.FC<ClinicalDataTableProps> = ({
  clinicalData,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState("all");

  // Filter clinical data based on search and type
  const filteredData = clinicalData.filter((data) => {
    // Filter by search query (checking if any vital sign includes the query)
    const matchesSearch =
      searchQuery === "" ||
      Object.entries(data).some(([key, value]) => {
        if (typeof value === "number" && key !== "patient_id" && key !== "id") {
          return value.toString().includes(searchQuery);
        }
        return false;
      });

    // Filter by vital sign type
    const matchesType =
      selectedType === "all" ||
      (selectedType === "heart_rate" && data.heart_rate !== undefined) ||
      (selectedType === "blood_pressure" &&
        (data.systolic_bp !== undefined || data.diastolic_bp !== undefined)) ||
      (selectedType === "temperature" && data.temperature !== undefined) ||
      (selectedType === "respiratory_rate" &&
        data.respiratory_rate !== undefined) ||
      (selectedType === "oxygen_saturation" &&
        data.oxygen_saturation !== undefined) ||
      (selectedType === "labs" &&
        (data.wbc_count !== undefined ||
          data.lactate !== undefined ||
          data.creatinine !== undefined));

    return matchesSearch && matchesType;
  });

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Box>
      <HStack mb={4} spacing={4}>
        <Input
          placeholder="Search values..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          width={{ base: "full", md: "300px" }}
          leftElement={<SearchIcon color="gray.300" />}
        />

        <Select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          width={{ base: "full", md: "200px" }}
        >
          <option value="all">All Measurements</option>
          <option value="heart_rate">Heart Rate</option>
          <option value="blood_pressure">Blood Pressure</option>
          <option value="temperature">Temperature</option>
          <option value="respiratory_rate">Respiratory Rate</option>
          <option value="oxygen_saturation">Oxygen Saturation</option>
          <option value="labs">Lab Values</option>
        </Select>
      </HStack>

      <Box overflowX="auto">
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Timestamp</Th>
              <Th>Measurement</Th>
              <Th>Value</Th>
              <Th>Unit</Th>
            </Tr>
          </Thead>
          <Tbody>
            {filteredData.length > 0 ? (
              filteredData.flatMap((data) => {
                const rows = [];

                // Extract all measurements as individual rows
                if (data.heart_rate !== undefined) {
                  rows.push({
                    timestamp: data.timestamp,
                    measurement: "Heart Rate",
                    value: data.heart_rate,
                    unit: "bpm",
                  });
                }

                if (data.respiratory_rate !== undefined) {
                  rows.push({
                    timestamp: data.timestamp,
                    measurement: "Respiratory Rate",
                    value: data.respiratory_rate,
                    unit: "breaths/min",
                  });
                }

                if (data.temperature !== undefined) {
                  rows.push({
                    timestamp: data.timestamp,
                    measurement: "Temperature",
                    value: data.temperature,
                    unit: "°C",
                  });
                }

                if (
                  data.systolic_bp !== undefined &&
                  data.diastolic_bp !== undefined
                ) {
                  rows.push({
                    timestamp: data.timestamp,
                    measurement: "Blood Pressure",
                    value: `${data.systolic_bp}/${data.diastolic_bp}`,
                    unit: "mmHg",
                  });
                }

                if (data.oxygen_saturation !== undefined) {
                  rows.push({
                    timestamp: data.timestamp,
                    measurement: "Oxygen Saturation",
                    value: data.oxygen_saturation,
                    unit: "%",
                  });
                }

                if (data.blood_glucose !== undefined) {
                  rows.push({
                    timestamp: data.timestamp,
                    measurement: "Blood Glucose",
                    value: data.blood_glucose,
                    unit: "mg/dL",
                  });
                }

                if (data.wbc_count !== undefined) {
                  rows.push({
                    timestamp: data.timestamp,
                    measurement: "WBC Count",
                    value: data.wbc_count,
                    unit: "10³/µL",
                  });
                }

                if (data.platelet_count !== undefined) {
                  rows.push({
                    timestamp: data.timestamp,
                    measurement: "Platelet Count",
                    value: data.platelet_count,
                    unit: "10³/µL",
                  });
                }

                if (data.lactate !== undefined) {
                  rows.push({
                    timestamp: data.timestamp,
                    measurement: "Lactate",
                    value: data.lactate,
                    unit: "mmol/L",
                  });
                }

                if (data.creatinine !== undefined) {
                  rows.push({
                    timestamp: data.timestamp,
                    measurement: "Creatinine",
                    value: data.creatinine,
                    unit: "mg/dL",
                  });
                }

                if (data.bilirubin !== undefined) {
                  rows.push({
                    timestamp: data.timestamp,
                    measurement: "Bilirubin",
                    value: data.bilirubin,
                    unit: "mg/dL",
                  });
                }

                return rows.map((row, index) => (
                  <Tr key={`${data.id}-${index}`}>
                    <Td>{formatTimestamp(row.timestamp)}</Td>
                    <Td>{row.measurement}</Td>
                    <Td isNumeric>{row.value}</Td>
                    <Td>{row.unit}</Td>
                  </Tr>
                ));
              })
            ) : (
              <Tr>
                <Td colSpan={4} textAlign="center" py={4}>
                  <Text>No clinical data found</Text>
                </Td>
              </Tr>
            )}
          </Tbody>
        </Table>
      </Box>
    </Box>
  );
};

export default ClinicalDataTable;
