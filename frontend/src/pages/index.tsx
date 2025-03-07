import React, { useState, useEffect } from "react";
import {
  Box,
  Heading,
  Button,
  Input,
  InputGroup,
  InputLeftElement,
  Stack,
  Flex,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  useToast,
} from "@chakra-ui/react";
import { SearchIcon, AddIcon } from "@chakra-ui/icons";
import { useRouter } from "next/router";
import MainLayout from "@/components/layouts/MainLayout";
import { Patient } from "@/types";
import { getPatients, searchPatients } from "@/services/patient.service";
import PatientTableRow from "@/components/patients/PatientTableRow";

const PatientsPage = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const router = useRouter();
  const toast = useToast();

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      setIsLoading(true);
      const data = await getPatients();
      setPatients(data);
    } catch (error) {
      toast({
        title: "Error fetching patients",
        description: "Could not retrieve patient list",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchPatients();
      return;
    }

    try {
      setIsLoading(true);
      const results = await searchPatients(searchQuery);
      setPatients(results);
    } catch (error) {
      toast({
        title: "Search failed",
        description: "Could not perform patient search",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddPatient = () => {
    router.push("/patients/new");
  };

  const handleRowClick = (patientId: string) => {
    router.push(`/patients/${patientId}`);
  };

  return (
    <MainLayout title="Patients">
      <Box mb={6}>
        <Heading size="lg" mb={2}>
          Patient Management
        </Heading>
        <Text color="gray.600">View and manage patient records</Text>
      </Box>

      <Flex
        mb={6}
        justify="space-between"
        direction={{ base: "column", md: "row" }}
      >
        <InputGroup maxW={{ md: "400px" }} mb={{ base: 4, md: 0 }}>
          <InputLeftElement pointerEvents="none">
            <SearchIcon color="gray.300" />
          </InputLeftElement>
          <Input
            placeholder="Search patients by name or MRN..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
        </InputGroup>

        <Stack direction="row" spacing={4}>
          <Button colorScheme="blue" onClick={handleSearch}>
            Search
          </Button>
          <Button
            leftIcon={<AddIcon />}
            colorScheme="green"
            onClick={handleAddPatient}
          >
            Add Patient
          </Button>
        </Stack>
      </Flex>

      <Box overflowX="auto" shadow="md" borderWidth="1px" borderRadius="lg">
        <Table variant="simple">
          <Thead bg="gray.50">
            <Tr>
              <Th>Name</Th>
              <Th>MRN</Th>
              <Th>Gender</Th>
              <Th>DOB</Th>
              <Th>Sepsis Risk</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {isLoading ? (
              <Tr>
                <Td colSpan={6} textAlign="center" py={4}>
                  <Text>Loading patients...</Text>
                </Td>
              </Tr>
            ) : patients.length > 0 ? (
              patients.map((patient) => (
                <PatientTableRow
                  key={patient.id}
                  patient={patient}
                  onClick={() => handleRowClick(patient.id)}
                />
              ))
            ) : (
              <Tr>
                <Td colSpan={6} textAlign="center" py={4}>
                  <Text>No patients found</Text>
                </Td>
              </Tr>
            )}
          </Tbody>
        </Table>
      </Box>
    </MainLayout>
  );
};

export default PatientsPage;
