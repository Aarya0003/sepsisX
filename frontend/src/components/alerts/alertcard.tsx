import React from 'react';
import { Box, Flex, Badge, Text, Button, HStack, Spacer } from '@chakra-ui/react';
import { useRouter } from 'next/router';
import { Alert, AlertStatus } from '@/types';
import { updateAlertStatus } from '@/services/alert.service';

interface AlertCardProps {
  alert: Alert;
  onStatusChange?: () => void;
}

const AlertCard: React.FC<AlertCardProps> = ({ alert, onStatusChange }) => {
  const router = useRouter();
  const [isUpdating, setIsUpdating] = React.useState(false);

  const getSeverityColor = (severity: number) => {
    switch (severity) {
      case 5: return 'red';
      case 4: return 'orange';
      case 3: return 'yellow';
      case 2: return 'blue';
      default: return 'green';
    }
  };

  const getStatusColor = (status: AlertStatus) => {
    switch (status) {
      case 'pending': return 'red';
      case 'acknowledged': return 'blue';
      case 'action_taken': return 'green';
      case 'dismissed': return 'gray';
      default: return 'gray';
    }
  };

  const handleViewPatient = () => {
    router.push(`/patients/${alert.patient_id}`);
  };

  const handleStatusChange = async (newStatus: AlertStatus) => {
    try {
      setIsUpdating(true);
      await updateAlertStatus(alert.id, newStatus);
      if (onStatusChange) {
        onStatusChange();
      }
    } catch (error) {
      console.error('Failed to update alert status:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <Box
      p={4}
      mb={4}
      borderWidth="1px"
      borderRadius="lg"
      borderLeftWidth="4px"
      borderLeftColor={`${getSeverityColor(alert.severity)}.500`}
      _hover={{ shadow: 'md' }}
    >
      <Flex direction={{ base: 'column', md: 'row' }} align={{ md: 'center' }}>
        <Box flex="1">
          <HStack mb={2}>
            <Badge colorScheme={getSeverityColor(alert.severity)}>
              Severity {alert.severity}
            </Badge>
            <Badge colorScheme={getStatusColor(alert.status)}>
              {alert.status.replace('_', ' ').toUpperCase()}
            </Badge>
            <Text fontSize="sm" color="gray.500">
              {new Date(alert.created_at).toLocaleString()}
            </Text>
          </HStack>
          
          <Text fontWeight="bold" mb={1}>
            {alert.alert_type.replace(/_/g, ' ')}
          </Text>
          
          <Text mb={2}>{alert.message}</Text>
          
          {alert.patient && (
            <Text fontSize="sm">
              Patient: {alert.patient.first_name} {alert.patient.last_name} 
              {alert.patient.mrn ? ` (MRN: ${alert.patient.mrn})` : '
              {alert.patient.mrn ? ` (MRN: ${alert.patient.mrn})` : ''}
            </Text>
          )}
        </Box>
        
        <Spacer />
        
        <HStack spacing={2} mt={{ base: 4, md: 0 }}>
          <Button size="sm" colorScheme="blue" onClick={handleViewPatient}>
            View Patient
          </Button>
          
          {alert.status === 'pending' && (
            <Button 
              size="sm" 
              colorScheme="green" 
              onClick={() => handleStatusChange('acknowledged')}
              isLoading={isUpdating}
            >
              Acknowledge
            </Button>
          )}
          
          {alert.status === 'acknowledged' && (
            <Button 
              size="sm" 
              colorScheme="green" 
              onClick={() => handleStatusChange('action_taken')}
              isLoading={isUpdating}
            >
              Mark Actioned
            </Button>
          )}
          
          {alert.status === 'pending' && (
            <Button 
              size="sm" 
              colorScheme="gray" 
              onClick={() => handleStatusChange('dismissed')}
              isLoading={isUpdating}
            >
              Dismiss
            </Button>
          )}
        </HStack>
      </Flex>
    </Box>
  );
};

export default AlertCard;