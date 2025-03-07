import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import {
  Box,
  Heading,
  Text,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Button,
  Flex,
  Badge,
  useToast,
  Grid,
  GridItem,
  VStack,
  HStack,
  Divider,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
} from "@chakra-ui/react";
import { ArrowBackIcon, EditIcon, RepeatIcon } from "@chakra-ui/icons";
import MainLayout from "@/components/layouts/MainLayout";
import { useAuth } from "@/contexts/AuthContext";
import {
  getPatientSummary,
  syncPatientFromFhir,
} from "@/services/patient.service";
import { predictSepsis } from "@/services/prediction.service";
import { PatientSummary } from "@/types";
import AlertList from "@/components/alerts/AlertList";
import ClinicalDataTable from "@/components/patients/ClinicalDataTable";
import PredictionList from "@/components/predictions/PredictionList";
import VitalsChart from "@/components/patients/VitalsChart";

const PatientDetailsPage = () => {
  const [patientSummary, setPatientSummary] = useState<PatientSummary | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(true);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const router = useRouter();
  const { id } = router.query;
  const toast = useToast();
  const { user } = useAuth();

  useEffect(() => {
    if (id) {
      fetchPatientSummary();
    }
  }, [id]);

  const fetchPatientSummary = async () => {
    if (!id) return;

    try {
      setIsLoading(true);
      const data = await getPatientSummary(id as string);
      setPatientSummary(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load patient data",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSyncFHIR = async () => {
    if (!id) return;

    try {
      setIsActionLoading(true);
      await syncPatientFromFhir(id as string);

      toast({
        title: "Success",
        description: "Patient data synchronized from FHIR",
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      // Refresh patient data
      fetchPatientSummary();
    } catch (error) {
      toast({
        title: "Sync Failed",
        description: "Could not sync patient data from FHIR",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsActionLoading(false);
    }
  };

  const handlePredictSepsis = async () => {
    if (!id) return;

    try {
      setIsActionLoading(true);
      const result = await predictSepsis(id as string);

      toast({
        title: "Prediction Complete",
        description: `Sepsis prediction: ${result.prediction.probability.toFixed(
          2
        )}% risk`,
        status: "info",
        duration: 5000,
        isClosable: true,
      });

      // Refresh patient data
      fetchPatientSummary();
    } catch (error) {
      toast({
        title: "Prediction Failed",
        description: "Could not generate sepsis prediction",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsActionLoading(false);
    }
  };

  if (isLoading) {
    return (
      <MainLayout title="Patient Details">
        <Box textAlign="center" py={10}>
          <Heading>Loading patient data...</Heading>
        </Box>
      </MainLayout>
    );
  }

  if (!patientSummary) {
    return (
      <MainLayout title="Patient Details">
        <Box textAlign="center" py={10}>
          <Heading>Patient not found</Heading>
          <Button
            leftIcon={<ArrowBackIcon />}
            mt={4}
            onClick={() => router.push("/patients")}
          >
            Back to Patients
          </Button>
        </Box>
      </MainLayout>
    );
  }

  const {
    patient,
    latest_vitals,
    recent_clinical_data,
    sepsis_predictions,
    latest_prediction,
    active_alerts,
  } = patientSummary;

  // Calculate patient age
  let patientAge = "";
  if (patient.date_of_birth) {
    const birthDate = new Date(patient.date_of_birth);
    const ageDiff = Date.now() - birthDate.getTime();
    const ageDate = new Date(ageDiff);
    patientAge = Math.abs(ageDate.getUTCFullYear() - 1970).toString();
  }

  return (
    <MainLayout title={`${patient.first_name} ${patient.last_name}`}>
      {/* Navigation and actions header */}
      <Flex mb={6} justify="space-between" align="center" wrap="wrap">
        <Button
          leftIcon={<ArrowBackIcon />}
          variant="outline"
          onClick={() => router.push("/patients")}
          mb={{ base: 2, md: 0 }}
        >
          Back to Patients
        </Button>

        <HStack spacing={4}>
          <Button
            leftIcon={<RepeatIcon />}
            colorScheme="blue"
            onClick={handleSyncFHIR}
            isLoading={isActionLoading}
            loadingText="Syncing"
            isDisabled={user?.role === "nurse"}
          >
            Sync FHIR
          </Button>

          <Button
            colorScheme="green"
            onClick={handlePredictSepsis}
            isLoading={isActionLoading}
            loadingText="Predicting"
          >
            Predict Sepsis
          </Button>

          <Button
            leftIcon={<EditIcon />}
            variant="outline"
            onClick={() => router.push(`/patients/edit/${patient.id}`)}
          >
            Edit
          </Button>
        </HStack>
      </Flex>

      {/* Patient summary header */}
      <Box
        p={5}
        shadow="md"
        borderWidth="1px"
        borderRadius="lg"
        bg="white"
        mb={6}
      >
        <Grid
          templateColumns={{
            base: "1fr",
            md: "repeat(3, 1fr)",
            lg: "repeat(6, 1fr)",
          }}
          gap={6}
        >
          <GridItem colSpan={{ base: 1, md: 3, lg: 2 }}>
            <VStack align="start" spacing={1}>
              <Heading size="lg">
                {patient.first_name} {patient.last_name}
              </Heading>
              <Text color="gray.600">
                {patientAge ? `${patientAge} years` : ""}
                {patient.gender ? ` • ${patient.gender}` : ""}
              </Text>
              <Text>{patient.mrn ? `MRN: ${patient.mrn}` : "No MRN"}</Text>
            </VStack>
          </GridItem>

          <GridItem colSpan={{ base: 1, md: 1, lg: 1 }}>
            <Stat>
              <StatLabel>Blood Pressure</StatLabel>
              <StatNumber>
                {latest_vitals.systolic_bp && latest_vitals.diastolic_bp
                  ? `${latest_vitals.systolic_bp}/${latest_vitals.diastolic_bp}`
                  : "N/A"}
              </StatNumber>
              <StatHelpText>mmHg</StatHelpText>
            </Stat>
          </GridItem>

          <GridItem colSpan={{ base: 1, md: 1, lg: 1 }}>
            <Stat>
              <StatLabel>Heart Rate</StatLabel>
              <StatNumber>{latest_vitals.heart_rate || "N/A"}</StatNumber>
              <StatHelpText>BPM</StatHelpText>
            </Stat>
          </GridItem>

          <GridItem colSpan={{ base: 1, md: 1, lg: 1 }}>
            <Stat>
              <StatLabel>Temperature</StatLabel>
              <StatNumber>{latest_vitals.temperature || "N/A"}</StatNumber>
              <StatHelpText>°C</StatHelpText>
            </Stat>
          </GridItem>

          <GridItem colSpan={{ base: 1, md: 2, lg: 1 }}>
            <Stat>
              <StatLabel>Sepsis Risk</StatLabel>
              <StatNumber>
                {latest_prediction
                  ? `${(latest_prediction.probability * 100).toFixed(1)}%`
                  : "N/A"}
              </StatNumber>
              <StatHelpText>
                <Badge
                  colorScheme={
                    latest_prediction?.is_sepsis_risk ? "red" : "green"
                  }
                  variant="solid"
                  borderRadius="full"
                  px={2}
                >
                  {latest_prediction?.is_sepsis_risk ? "HIGH RISK" : "Low Risk"}
                </Badge>
              </StatHelpText>
            </Stat>
          </GridItem>
        </Grid>
      </Box>

      {/* Tab panels for detailed information */}
      <Tabs
        variant="enclosed"
        shadow="md"
        borderWidth="1px"
        borderRadius="lg"
        bg="white"
      >
        <TabList>
          <Tab>Overview</Tab>
          <Tab>Clinical Data</Tab>
          <Tab>Predictions</Tab>
          <Tab>Alerts ({active_alerts.length})</Tab>
        </TabList>

        <TabPanels>
          {/* Overview Panel */}
          <TabPanel>
            <Grid templateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={6}>
              <GridItem>
                <Heading size="md" mb={4}>
                  Vital Signs Trend
                </Heading>
                <Box height="300px">
                  <VitalsChart clinicalData={recent_clinical_data} />
                </Box>
              </GridItem>

              <GridItem>
                <Heading size="md" mb={4}>
                  Patient Information
                </Heading>
                <VStack align="start" spacing={4} divider={<Divider />}>
                  <Box width="100%">
                    <Text fontWeight="bold">Contact Information</Text>
                    <Text>{patient.phone_number || "No phone number"}</Text>
                    <Text>{patient.email || "No email"}</Text>
                    <Text>{patient.address || "No address"}</Text>
                  </Box>

                  <Box width="100%">
                    <Text fontWeight="bold">Latest Sepsis Prediction</Text>
                    {latest_prediction ? (
                      <>
                        <Text>
                          Risk:{" "}
                          {(latest_prediction.probability * 100).toFixed(1)}%
                        </Text>
                        <Text>
                          Date:{" "}
                          {new Date(
                            latest_prediction.timestamp
                          ).toLocaleString()}
                        </Text>
                        <Text>
                          Model Version: {latest_prediction.model_version}
                        </Text>
                      </>
                    ) : (
                      <Text>No predictions yet</Text>
                    )}
                  </Box>

                  <Box width="100%">
                    <Text fontWeight="bold">System Information</Text>
                    <Text>
                      Created:{" "}
                      {new Date(patient.created_at).toLocaleDateString()}
                    </Text>
                    <Text>
                      Updated:{" "}
                      {patient.updated_at
                        ? new Date(patient.updated_at).toLocaleDateString()
                        : "Never"}
                    </Text>
                  </Box>
                </VStack>
              </GridItem>
            </Grid>
          </TabPanel>

          {/* Clinical Data Panel */}
          <TabPanel>
            <ClinicalDataTable clinicalData={recent_clinical_data} />
          </TabPanel>

          {/* Predictions Panel */}
          <TabPanel>
            <PredictionList predictions={sepsis_predictions} />
          </TabPanel>

          {/* Alerts Panel */}
          <TabPanel>
            <AlertList
              alerts={active_alerts}
              onStatusChange={fetchPatientSummary}
            />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </MainLayout>
  );
};

export default PatientDetailsPage;
