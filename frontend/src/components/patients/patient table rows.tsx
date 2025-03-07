import React from "react";
import { Tr, Td, Badge, IconButton, HStack, Text } from "@chakra-ui/react";
import { ViewIcon, EditIcon } from "@chakra-ui/icons";
import { Patient } from "@/types";
import { useRouter } from "next/router";

interface PatientTableRowProps {
  patient: Patient;
  onClick: () => void;
}

const PatientTableRow: React.FC<PatientTableRowProps> = ({
  patient,
  onClick,
}) => {
  const router = useRouter();

  // Format date of birth
  const formatDOB = (dateString?: string) => {
    if (!dateString) return "Unknown";
    return new Date(dateString).toLocaleDateString();
  };

  // Prevent event bubbling for action buttons
  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    router.push(`/patients/edit/${patient.id}`);
  };

  return (
    <Tr
      onClick={onClick}
      _hover={{ bg: "gray.50", cursor: "pointer" }}
      transition="background-color 0.2s"
    >
      <Td>
        <Text fontWeight="semibold">
          {patient.first_name} {patient.last_name}
        </Text>
      </Td>
      <Td>{patient.mrn || "N/A"}</Td>
      <Td>{patient.gender || "Unknown"}</Td>
      <Td>{formatDOB(patient.date_of_birth)}</Td>
      <Td>
        <Badge colorScheme="green">Low</Badge>
      </Td>
      <Td>
        <HStack spacing={2}>
          <IconButton
            aria-label="View patient"
            icon={<ViewIcon />}
            size="sm"
            colorScheme="blue"
            variant="ghost"
            onClick={onClick}
          />
          <IconButton
            aria-label="Edit patient"
            icon={<EditIcon />}
            size="sm"
            colorScheme="teal"
            variant="ghost"
            onClick={handleEditClick}
          />
        </HStack>
      </Td>
    </Tr>
  );
};

export default PatientTableRow;
