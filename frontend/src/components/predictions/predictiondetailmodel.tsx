import React from "react";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  Text,
  Box,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Badge,
  Heading,
  Progress,
} from "@chakra-ui/react";
import { SepsisPrediction } from "@/types";
import {
  createFeedback,
  getFeedbackForPrediction,
} from "@/services/feedback.service";

interface PredictionDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  prediction: SepsisPrediction;
}

const PredictionDetailModal: React.FC<PredictionDetailModalProps> = ({
  isOpen,
  onClose,
  prediction,
}) => {
  const [feedback, setFeedback] = React.useState<any[]>([]);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  React.useEffect(() => {
    if (isOpen && prediction) {
      fetchFeedback();
    }
  }, [isOpen, prediction]);

  const fetchFeedback = async () => {
    try {
      const data = await getFeedbackForPrediction(prediction.id);
      setFeedback(data);
    } catch (error) {
      console.error("Error fetching feedback:", error);
    }
  };

  const handleSubmitFeedback = async (
    feedbackType: "correct" | "false_positive" | "false_negative" | "unsure"
  ) => {
    try {
      setIsSubmitting(true);
      await createFeedback(prediction.id, feedbackType);
      await fetchFeedback();
    } catch (error) {
      console.error("Error submitting feedback:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  // Get normalized risk factors from SHAP values
  const getRiskFactors = () => {
    if (!prediction.explanation) return [];

    const { features, shap_values } = prediction.explanation;

    // Combine features and SHAP values
    const featureImpacts = features.map((feature, index) => ({
      name: feature,
      impact: shap_values[index],
      value: prediction.features_used[feature],
    }));

    // Sort by absolute impact
    return featureImpacts.sort(
      (a, b) => Math.abs(b.impact) - Math.abs(a.impact)
    );
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Sepsis Prediction Details</ModalHeader>
        <ModalCloseButton />

        <ModalBody>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} mb={6}>
            <Stat>
              <StatLabel>Sepsis Probability</StatLabel>
              <StatNumber>
                {(prediction.probability * 100).toFixed(1)}%
              </StatNumber>
              <StatHelpText>
                <Badge
                  colorScheme={prediction.is_sepsis_risk ? "red" : "green"}
                >
                  {prediction.is_sepsis_risk ? "HIGH RISK" : "Low Risk"}
                </Badge>
              </StatHelpText>
            </Stat>

            <Stat>
              <StatLabel>Prediction Time</StatLabel>
              <StatNumber>{formatTimestamp(prediction.timestamp)}</StatNumber>
              <StatHelpText>Model v{prediction.model_version}</StatHelpText>
            </Stat>
          </SimpleGrid>

          <Box mb={6}>
            <Heading size="sm" mb={3}>
              Key Risk Factors
            </Heading>
            {getRiskFactors()
              .slice(0, 5)
              .map((factor, index) => (
                <Box key={index} mb={3}>
                  <Flex justify="space-between" mb={1}>
                    <Text>{factor.name}</Text>
                    <Text>{factor.value.toFixed(1)}</Text>
                  </Flex>
                  <Progress
                    value={50 + factor.impact * 50}
                    colorScheme={factor.impact > 0 ? "red" : "green"}
                    size="sm"
                  />
                  <Text fontSize="xs" color="gray.500" mt={1}>
                    {factor.impact > 0
                      ? "Increases sepsis risk"
                      : "Decreases sepsis risk"}
                  </Text>
                </Box>
              ))}
          </Box>

          <Box mb={6}>
            <Heading size="sm" mb={3}>
              Clinician Feedback
            </Heading>
            {feedback.length > 0 ? (
              feedback.map((item, index) => (
                <Box key={index} p={3} bg="gray.50" borderRadius="md" mb={2}>
                  <Text fontWeight="bold">
                    {item.feedback_type === "correct"
                      ? "✓ Correct prediction"
                      : item.feedback_type === "false_positive"
                      ? "✗ False positive"
                      : item.feedback_type === "false_negative"
                      ? "✗ False negative"
                      : "? Unsure"}
                  </Text>
                  {item.comments && <Text mt={1}>{item.comments}</Text>}
                  <Text fontSize="sm" color="gray.500" mt={1}>
                    By {item.user_name} on{" "}
                    {new Date(item.created_at).toLocaleString()}
                  </Text>
                </Box>
              ))
            ) : (
              <Text>No feedback provided yet</Text>
            )}
          </Box>

          <Box>
            <Heading size="sm" mb={3}>
              Provide Feedback
            </Heading>
            <SimpleGrid columns={2} spacing={3}>
              <Button
                colorScheme="green"
                size="sm"
                onClick={() => handleSubmitFeedback("correct")}
                isLoading={isSubmitting}
              >
                Correct
              </Button>

              <Button
                colorScheme="red"
                size="sm"
                onClick={() => handleSubmitFeedback("false_positive")}
                isLoading={isSubmitting}
              >
                False Positive
              </Button>

              <Button
                colorScheme="orange"
                size="sm"
                onClick={() => handleSubmitFeedback("false_negative")}
                isLoading={isSubmitting}
              >
                False Negative
              </Button>

              <Button
                colorScheme="gray"
                size="sm"
                onClick={() => handleSubmitFeedback("unsure")}
                isLoading={isSubmitting}
              >
                Unsure
              </Button>
            </SimpleGrid>
          </Box>
        </ModalBody>

        <ModalFooter>
          <Button colorScheme="blue" onClick={onClose}>
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default PredictionDetailModal;
