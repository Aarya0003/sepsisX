import React from "react";
import {
  Box,
  Text,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Button,
  useDisclosure,
  Flex,
} from "@chakra-ui/react";
import { ViewIcon } from "@chakra-ui/icons";
import { SepsisPrediction } from "@/types";
import PredictionDetailModal from "./PredictionDetailModal";

interface PredictionListProps {
  predictions: SepsisPrediction[];
}

const PredictionList: React.FC<PredictionListProps> = ({ predictions }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedPrediction, setSelectedPrediction] =
    React.useState<SepsisPrediction | null>(null);

  const handleViewDetails = (prediction: SepsisPrediction) => {
    setSelectedPrediction(prediction);
    onOpen();
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Box>
      {predictions.length > 0 ? (
        <>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Timestamp</Th>
                <Th>Probability</Th>
                <Th>Risk Level</Th>
                <Th>Model Version</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {predictions.map((prediction) => (
                <Tr key={prediction.id}>
                  <Td>{formatTimestamp(prediction.timestamp)}</Td>
                  <Td>{(prediction.probability * 100).toFixed(1)}%</Td>
                  <Td>
                    <Badge
                      colorScheme={prediction.is_sepsis_risk ? "red" : "green"}
                    >
                      {prediction.is_sepsis_risk ? "HIGH RISK" : "Low Risk"}
                    </Badge>
                  </Td>
                  <Td>{prediction.model_version}</Td>
                  <Td>
                    <Button
                      leftIcon={<ViewIcon />}
                      size="sm"
                      colorScheme="blue"
                      onClick={() => handleViewDetails(prediction)}
                    >
                      Details
                    </Button>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>

          {selectedPrediction && (
            <PredictionDetailModal
              isOpen={isOpen}
              onClose={onClose}
              prediction={selectedPrediction}
            />
          )}
        </>
      ) : (
        <Box textAlign="center" py={8}>
          <Heading size="md" color="gray.500">
            No predictions found
          </Heading>
          <Text mt={2}>This patient has no sepsis predictions yet</Text>
        </Box>
      )}
    </Box>
  );
};

export default PredictionList;
